import os
import logging

from os import F_OK
from stat import ST_MODE,S_ISDIR,S_ISREG
from datetime import date, datetime


class Logger() :
    def __init__(self, log_tag, debug_mode, param):

        self._logger = logging.getLogger(log_tag)
        if debug_mode is True :
            self._logger.setLevel(logging.DEBUG)
        
        log_output_folder = param['OUTPUT_LOGFOLDER']

        if (os.access(log_output_folder, F_OK)) is False:
            os.makedirs(log_output_folder)

        expression_time = '%Y-%m-%d-%p-%I-%M'
        logFileName = log_output_folder + '/' +  datetime.now().strftime(expression_time) + '.log'
        logFileHandler = logging.FileHandler( logFileName)
        logStreamHandler = logging.StreamHandler()

        # add handlers to log instance
        self._logger.addHandler(logFileHandler)
        self._logger.addHandler(logStreamHandler)
    
    def d(self,message):
        return self._logger.debug(message)

    def e(self,message):
        return self._logger.error(message)

    def w(self,message):
        return self._logger.warning(message)

    def i(self,message):
        return self._logger.info(message)

    def c(self,message):
        return self._logger.critical(message)