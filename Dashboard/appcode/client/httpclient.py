
import requests
import json
class HTTPCLIENT():

    def __init__(self,param):
        self._ip = param['IP']
        self._port = param['PORT']
        self._schema = param['SCHEMA']
        self._baseurl = self._schema + self._ip + ':' + self._port
    
    def get(self, url=None, headers=None):
        if url is None :
            target_url = self._baseurl + '/' 
        else :
            target_url = self._baseurl + '/' + url
        
        response = requests.get(target_url , headers=headers)

        return response
        
        

