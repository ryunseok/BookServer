# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, send_from_directory,send_file,url_for
from flask_cors import CORS, cross_origin
from urllib.parse import urlencode

import os
import logging
import stat

from datetime import date, datetime
from Utils.logger import Logger



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
Log = Logger('FileServer',True, server_config )

@app.route('/favicon.ico')
def favicon():
    Log.d("request favicon.ico")
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

supportedExt = tuple({'.zip', '.pdf'})

def build_response(path) : 

    file_path = u"{}".format(base_folder + '/' +  path)      
    file_path.replace('//','/')
    mode = os.stat(file_path)[stat.ST_MODE]
    
    if stat.S_ISDIR(mode):
        list_dir = os.listdir(file_path)  
        folder_tree = {}
        for name in list_dir:
            # sub_path in folder
            sub_path = file_path + '/' + name
            sub_stat_info = os.stat(sub_path)  

             # check directory or file
            isDirectory = stat.S_ISDIR(sub_stat_info[stat.ST_MODE])   
            if isDirectory is False :                                  
                if sub_path.lower().endswith(supportedExt) is False :         
                    continue

            # File or Directory creation time
            cTime = os.path.getctime(sub_path)
            DateTime = date.fromtimestamp(cTime).strftime('%Y-%m-%d-%a')  

            # if isDirectory is False : 
            fileSize = sub_stat_info[stat.ST_SIZE]

            file_desc = {                
                'filePath' : file_path,
                'creationTime' : DateTime,
                'isDirectory' : isDirectory                                              
            }    
            if isDirectory is False : 
                file_desc.update({'fileSize' : fileSize})              
            folder_tree.update({name : file_desc})
        res_json = json.dumps(folder_tree, indent = 4,ensure_ascii=False)
        Log.d(res_json)
        # print(res_json)
        return Response(res_json, status = 200, headers=None, mimetype="application/json")
    elif stat.S_ISREG(mode):
        # filetering supported extension
        if file_path.lower().endswith(supportedExt):
            return send_file(file_path)

@app.route('/<path:resource>', methods=['GET'])
@cross_origin()
def returnFolderFile(resource):
    '''
        path : if path is folder, return folder tree   
    '''

    return build_response(resource)

@app.route('/', methods=['GET'])
@cross_origin()
def returnBaseFolder():
    '''
        path : if path is folder, return folder tree   
    '''
    return build_response('')
    
        
    

# @app.route('/test', methods=['GET'])
# @cross_origin()
# def hello_world():   

#     return 'hello world'


if __name__ == '__main__' :    
    app.run(host = '0.0.0.0', port = server_config['PORT'], debug=server_config['DEBUG'])


