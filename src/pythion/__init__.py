import logging

LOGFILE = './log.txt'
logging.basicConfig(filename=LOGFILE,
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger('pythion')
logger.setLevel(logging.INFO)
