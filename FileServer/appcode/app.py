# -*- coding: utf-8 -*-

from flask import Flask, request, json, Response, send_from_directory,send_file
from flask_cors import CORS, cross_origin
from urllib.parse import urlencode




import os
from stat import ST_MODE,S_ISDIR,S_ISREG
from datetime import date



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


# def build_foldertree(top, callback):
#     '''recursively descend the directory tree rooted at top,
#        calling the callback function for updating json folder tree'''

#     for f in os.listdir(top):
#         pathname = os.path.join(top, f)
#         mode = os.stat(pathname)[ST_MODE]
#         if S_ISDIR(mode):
#             # It's a directory, recurse into it            
#             build_foldertree(pathname, callback)
#         elif S_ISREG(mode):
#             # It's a file, call the callback function
#             callback(pathname)
#         else:
#             # Unknown file type, print a message
#             print('Skipping{} '.format(pathname))

# def visitfile(file):    
#     print('visiting', file)

supportedExt = {'.zip', '.pdf'}
@app.route('/<relativepath>', methods=['GET'])
@cross_origin()
def returnFolderFile(relativepath):
    '''
        path : if path is folder, return folder tree   
    '''
    print(request.headers)    
    file_path = base_folder + relativepath
    print(file_path)
    mode = os.stat(file_path)[ST_MODE]
    print(mode)
    if S_ISDIR(mode):
        list_dir = os.listdir(file_path)
        folder_tree = {'folder_tree':{}}
        for key in list_dir:
            cTime = os.path.getctime(file_path +'/' +  key)
            DateTime = date.fromtimestamp(cTime).strftime('%Y-%m-%d')    
            file_desc = {                
                'file_path' : file_path,
                'creation_time' : DateTime                
            }   
            
            folder_tree['folder_tree'].update({key : file_desc})
        res_json = json.dumps(folder_tree, indent = 4)
        print(res_json)
        return Response(res_json, status = 200, headers=None, mimetype="application/json")
    elif S_ISREG(mode):
        if file_path.lower().endswith(supportedExt):
            return send_file(file_path)

@app.route('/', methods=['GET'])
@cross_origin()
def returnBaseFolder():
    '''
        path : if path is folder, return folder tree   
    '''
    print('소설/만화')
    
    file_path = base_folder
    print(file_path)
    mode = os.stat(file_path)[ST_MODE]
    print(mode)
    
    list_dir = os.listdir(file_path)
    folder_tree = {'folder_tree':{}}
    for key in list_dir:
        cTime = os.path.getctime(file_path +'/' +  key)
        DateTime = date.fromtimestamp(cTime).strftime('%Y-%m-%d')    
        file_desc = {                
            'file_path' : file_path,
            'creation_time' : DateTime                
        }               
        folder_tree['folder_tree'].update({key : file_desc})
    res_json = json.dumps(folder_tree, indent = 4, ensure_ascii=False)
    print(res_json)
    # print(res_json)
    return Response(res_json, status = 200, headers=None, mimetype="application/json")
    
        
    

@app.route('/test', methods=['GET'])
@cross_origin()
def hello_world():   

    return 'hello world'


if __name__ == '__main__' :    
    app.run(host = server_config['HOST'], port = server_config['PORT'], debug=server_config['DEBUG'])


