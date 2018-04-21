# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, send_from_directory, send_file, url_for, make_response
from flask_cors import CORS, cross_origin
from urllib.parse import urlencode, quote

import os
import logging
import stat

from datetime import date, datetime
from Utils import logger, dirUtils


# Create Flask
app = Flask(__name__)

# import Flask config
cwd = os.path.dirname(os.path.realpath(__file__))
with open(cwd + '/FileServer_config.json', 'r') as configfile:
    config = json.load(configfile)
configfile.close()

# config flask_CORS
app.config.update(config['CORS'])
cors = CORS(app)

# config Upload-directory
base_folder = config['UPLOADFOLDER']

# config server host,port,debug
server_config = config['DEFAULT']


# set logger instacne
Log = logger.Logger('FileServer', True, server_config)

# @app.route('/favicon.ico')
# def favicon():
#     Log.d("request favicon.ico")
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                           'favicon.ico',mimetype='image/vnd.microsoft.icon')


# supported File Extension
supportedExt = tuple({'.zip', '.pdf'})


def build_pathInfo(path):
    file_path = u"{}".format(base_folder + '/' + path)
    file_path = file_path.replace('//', '/')

    mode = os.stat(file_path)[stat.ST_MODE]

    if stat.S_ISDIR(mode):
        subDirs = os.listdir(file_path)
        folder_tree = {}
        for subDir in subDirs:
            # sub_path in folder
            sub_path = file_path + '/' + subDir
            sub_path = sub_path.replace('//', '/')
            sub_stat_info = os.stat(sub_path)
            fileSize = 0

            # check directory or file
            isDirectory = stat.S_ISDIR(sub_stat_info[stat.ST_MODE])
            category = ''
            if isDirectory is False:
                if sub_path.lower().endswith(supportedExt) is False:
                    continue
                else:
                    #check Novel,Comic,etc.
                    if '소설' in sub_path :
                        category = '소설'
                    elif '만화' in sub_path :
                        category = '만화'
                    else:
                        category = '기타'
                    fileSize = sub_stat_info[stat.ST_SIZE]

            # the time ot the last metadata change(UNIX), and, on others(Like Windows), is creation time
            cTime = os.path.getctime(sub_path)
            DateTime = date.fromtimestamp(cTime).strftime('%Y-%m-%d-%a')

            file_desc = {
                'parentFolder': sub_path.replace('/' + subDir, '').replace(base_folder, ''),
                'filePath': sub_path.replace(base_folder, ''),
                'DateTime': DateTime,
                'isDirectory': isDirectory,
                'fileSize': fileSize,
                'category' : category
            }

            folder_tree.update({subDir: file_desc})
        res_json = json.dumps(folder_tree, indent=4, ensure_ascii=False)

        return Response(res_json, status=200, headers=None, mimetype="application/json")
    elif stat.S_ISREG(mode):
        # filetering supported extension

        split_file_path = file_path.split('/')

        filename = split_file_path[len(split_file_path) - 1]

        for ext in supportedExt:
            if file_path.lower().endswith(ext):
                print(ext)
                mime_type = 'application/' + ext.replace('.', '')
                response = make_response(send_file(file_path,
                                                   mimetype=mime_type,
                                                   attachment_filename=filename,
                                                   as_attachment=True))
                response.headers['Content-Disposition'] = \
                    "attachment; " \
                    "filename*=UTF-8''{quoted_filename}".format(
                    quoted_filename=quote(
                        filename.encode('utf8'))
                )
                return response

@app.route('/favicon.ico')
def favicon():
    return Response(None,headers=None,status=200)

@app.route('/recentUpdated', methods=['GET'])
@cross_origin()
def recentUpdate():

    recentUpdatedList = {}
    updatedInDays = server_config['UPDATEDLIST_INDAYS']

    updateList = dirUtils.UpdateList(base_folder, updatedInDays, Log.d)
    recentUpdatedList.update(updateList.updatedList)
    
    res_json = json.dumps(recentUpdatedList, indent=4, ensure_ascii=False)
    return Response(res_json, headers=None, status=200, mimetype="application/json")


@app.route('/<path:resource>', methods=['GET'])
@cross_origin()
def returnFolderFile(resource):
    '''
        path : if path is folder, return folder tree   
    '''
    return build_pathInfo(resource)


@app.route('/', methods=['GET'])
@cross_origin()
def returnBaseFolder():
    '''
        path : if path is folder, return folder tree   
    '''
    return build_pathInfo('')


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=server_config['PORT'], debug=True)
