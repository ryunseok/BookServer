import os
import logging
import stat

from datetime import date, datetime

supportedExt = tuple({'.zip', '.pdf'})

class UpdateList() :
    def __init__(self,path, indays, callback):
        self._path = path 
        self._callback = callback
        self._updatedList = {}
        self._indays = indays

    @property
    def updatedList(self):
        self.buildUpdatedList(self._updatedList, self._path, self._callback)
        # self._callback(self._updatedList)
        return self._updatedList
    
    def buildUpdatedList(self, totalUpdatedList, path,callback) :
        
        file_path = u"{}".format(path)      
        file_path.replace('//','/')
        mode = os.stat(file_path)[stat.ST_MODE]              
        # logger.d(path)
        if stat.S_ISDIR(mode):
            subDirs = os.listdir(file_path)
            for subDir in subDirs:
                subPath = file_path + '/' + subDir                              
                self.buildUpdatedList(self._updatedList,subPath,callback) 
        elif stat.S_ISREG(mode):
            # filetering supported extension
            
            if file_path.lower().endswith(supportedExt):            
                file_info = os.stat(file_path)     
                # logger.d("File Info : {}".format(file_info))             

                # the time ot the last metadata change(UNIX), and, on others(Like Windows), is creation time
                cTime = file_info[stat.ST_CTIME]            
                DateTime = date.fromtimestamp(cTime).strftime('%Y-%m-%d-%a')  

                # delta between now and cTime
                nowTime = datetime.now()
                delta = (nowTime - datetime.fromtimestamp(cTime)).days

                if delta < 60 :
                    # if isDirectory is False : 
                    fileSize = file_info[stat.ST_SIZE]

                    #split path
                    split_path = file_path.split('/')            
                    #parent path
                    parentFolder = '/'.join(split_path[2:len(split_path) -1])               

                    # file name
                    fileName = split_path[len(split_path)- 1]    
                    # Series
                    series = split_path[len(split_path)- 2] 

                    #check Novel,Comic,etc.
                    if '소설' in parentFolder :
                        category = '소설'                        
                    elif '만화' in parentFolder :
                        category = '만화'
                    else:
                        category = '기타'
                    prefix = '[' + category + ']'
                
                    updateList = {
                        "CreationTime" : cTime,
                        "FileSize" : fileSize,
                        "ParentFolder" : '/' + parentFolder,
                        "FileName" : fileName,
                        "Category" : category                        
                    }  
                    # callback(updateList)                    
                    totalUpdatedList.update({prefix + series + '\t\t\t : ' + DateTime : updateList})
                    