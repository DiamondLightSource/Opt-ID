import logging

def getLogger(module):
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)8s | %(threadName)s | %(module)s::%(funcName)s::%(lineno)-4d | %(message)s',
                        datefmt='%H:%M:%S')
    logger = logging.getLogger(module)
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.CRITICAL)
    return logger

def setLoggerLevel(logger, level):
    try:
        levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        old_level = logging.getLevelName(logger.level)
        logger.setLevel(levels[max(0, min((len(levels) - 1), level))])
        new_level = logging.getLevelName(logger.level)
        logger.info('Changing logging level from [%s] to [%s]', old_level, new_level)
    except Exception as ex:
        logger.error('Error attempting to change logging level to [%s] [%s]', type(level), str(level), exc_info=ex)
        raise ex

# logger = getLogger(__name__)
#
# if __name__ == "__main__":
#
#     logger.setLevel(logging.INFO)
#     logger.debug('Hello %s.', 'World')
#     logger.info('Hello %s.', 'World')
#     logger.warning('Hello %s.', 'World')
#     logger.error('Hello %s.', 'World')
#     logger.critical('Hello %s.', 'World')
#
#     if logger.isEnabledFor(logging.INFO):
#         logger.info('INFO')