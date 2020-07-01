import logging

def getLogger(module):
    logging.basicConfig(format='[ %(asctime)s.%(msecs)03d | %(threadName)-10s | %(levelname)-8s | %(module)s::%(funcName)s::%(lineno)d ] %(message)s',
                        datefmt='%H:%M:%S')
    logger = logging.getLogger(module)
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    return logger

logger = getLogger(__name__)

if __name__ == "__main__":

    logger.setLevel(logging.INFO)
    logger.debug('Hello %s.', 'World')
    logger.info('Hello %s.', 'World')
    logger.warning('Hello %s.', 'World')
    logger.error('Hello %s.', 'World')
    logger.critical('Hello %s.', 'World')

    if logger.isEnabledFor(logging.INFO):
        logger.info('INFO')