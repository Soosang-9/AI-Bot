import logging
import logging.handlers

class logger:
    def __init__(self, f_name='log.txt'):
        self.file_max_bytes = 10 * 1024 * 1024
        self.filename = './user_log/'+f_name
        # logging.basicConfig(filename='./log/log.txt', level=logging.DEBUG)
        self.logger = logging.getLogger('myLogger')
        self.logger.setLevel(logging.DEBUG)
        # fileHandler = logging.FileHandler('./log/log.txt')
        self.formatter = logging.Formatter('[%(levelname)8s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
        self.fileHandler = logging.handlers.RotatingFileHandler(filename=self.filename, maxBytes=self.file_max_bytes, backupCount=10)
        self.fileHandler.setFormatter(self.formatter)

        self.streamHandler = logging.StreamHandler()
        self.logger.addHandler(self.fileHandler)
        self.logger.addHandler(self.streamHandler)

    def write_info(self, text):
        self.logger.info(text)

    def write_warning(self, text):
        self.logger.warning(text)

    def write_debug(self, text):
        self.logger.debug(text)

    def write_critical(self, text):
        self.logger.critical(text)
        # if critical had occured do some action here

# Use : logger() create instance and write info, warning, debug, and critical
# logger = logger('test2.log')
# logger.write_info('test text')
# logger.write_info('test log')
