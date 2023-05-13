import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def output_log(msg, level='info'):
    if level == 'error':
        logger.error(msg, exc_info=True)
    else:
        logger.info(msg)
