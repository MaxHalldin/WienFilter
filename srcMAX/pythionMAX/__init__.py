import logging
import os

LOGFOLDER = f'{os.path.expanduser("~")}/.pythion'
if not os.path.isdir(LOGFOLDER):
    os.makedirs(LOGFOLDER)
LOGFILE = LOGFOLDER + '/log.txt'

logging.basicConfig(filename=LOGFILE,
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger('pythion')
logger.setLevel(logging.INFO)
