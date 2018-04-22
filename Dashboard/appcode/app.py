
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory, json, Response, logging
from functools import wraps
from passlib.hash import sha256_crypt
from wtforms import Form, widgets, StringField, TextAreaField, IntegerField, SelectMultipleField, RadioField, PasswordField, validators
from flask_cors import CORS, cross_origin
from urllib.parse import urlencode

import jinja2.exceptions
import requests
import base64

import os
import logging
import stat

import time
from datetime import date, datetime
from client.httpclient import HTTPCLIENT


# Create Flask
app = Flask(__name__)

# import Flask config
cwd = os.path.dirname(os.path.realpath(__file__))
with open(cwd + '/Dashboard_config.json', 'r') as configfile:
    config = json.load(configfile)
configfile.close()

cwd = os.path.dirname(os.path.realpath(__file__))
with open(cwd + '/userpassword.json', 'r') as configfile:
    auth_credential = json.load(configfile)
    auth_id = auth_credential['user_id']
    auth_pw = str(base64.b64encode(
        str(auth_credential['user_pw']).encode('utf-8')))
configfile.close()

# config flask_CORS
app.config.update(config['CORS'])
cors = CORS(app)

# config server host,port,debug
server_config = config['DEFAULT']

# config File Server
file_server_config = config['FILESERVER']
http_client = HTTPCLIENT(file_server_config)


logger = logging.getLogger('Test')
logger.setLevel(logging.DEBUG)
logStreamHandler = logging.StreamHandler()
logger.addHandler(logStreamHandler)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/<path:resource>')
@is_logged_in
def getFolderInfo(resource):

    response = http_client.get(resource)

    # split_resource = resource.split('/')
    # upFolder = '/'.join(split_resource[0:])
    # for key in folder :

    content_type = response.headers['Content-Type'].split('/')[1]
    # print('Content Type : {}'.format(content_type))
    logger.info('headers : {}'.format(response.headers))
    if content_type == 'json':
        folder = json.loads(response.text)
        keys = folder.keys()
        values = folder.values()

        if len(keys) > 0:
            upFolder = (list(values)[0]['parentFolder']).split('/')
            upFolder = '/'.join(upFolder[0:len(upFolder)-1])
            if upFolder == '':
                upFolder = '/dashboard'
            return render_template('dashboard.html', quicklink=quicklink, update=updateList_dict, folder=folder, upFolder=upFolder)
        else:
            return redirect(url_for('dashboard'))
    elif content_type == 'pdf' or content_type == 'zip':
        return Response(response.content,
                        headers={
                            'Content-Disposition': response.headers['Content-Disposition'],
                            'Content-Type' : response.headers['Content-Type']})
    
      
    else:
        return '<strong>Page Not Found!</strong>', 404


@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)


@app.errorhandler(404)
def not_found(e):
    return '<strong>Page Not Found!</strong>', 404


@app.route('/')
def index():
    return render_template('login.html', data = {'response': None})


@app.route('/login', methods = ['GET', 'POST'])
def login():
    data={
        'response': None
    }

    if request.method == 'POST':
        # print(auth_id, auth_pw)

        user_info = {
            'user_id': request.form['user_id'],
            'user_pw': str(base64.b64encode(str(request.form['user_pw']).encode('utf-8')))
        }

        if auth_id == user_info['user_id']:
            if auth_pw == user_info['user_pw']:
                # success login
                session['logged_in'] = True
                session['user_id'] = user_info['user_id']
                return redirect(url_for('dashboard'))

        data['response'] = {
            'success': False,
            'message': 'Incorrect id or password'
        }
        return render_template('login.html', data=data)


# Dashboard


quicklink = {}
response = http_client.get()
quicklink = json.loads(response.text)

response = response = http_client.get('recentUpdated')
updateList = json.loads(response.text)

def sort_by_date(rows):
    # print(rows[1]['CreationTime'])
    # print(rows)
    return rows[1]['CreationTime']
   
# sort_by_date(updateList)
updateList_sorted = sorted(updateList.items(), key= sort_by_date ,reverse=True)

# conver list(key, value) to dict(key:value)
updateList_dict = dict()
for key,value in updateList_sorted :
    # print('{} : {}'. format(key,value))
    updateList_dict.update({key : value}) 
print(updateList_dict)


@app.route('/dashboard', methods=['GET'])
@is_logged_in
def dashboard():

    # request folder tree from fileserver(127.0.0.1:5555)
    response = http_client.get()
    folder = json.loads(response.text)

    return render_template('dashboard.html', quicklink=quicklink, update=updateList_dict, folder=folder)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0',
            port=server_config['PORT'], debug=server_config['DEBUG'])
