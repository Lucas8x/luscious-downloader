import logging

from colorlog import ColoredFormatter


def logger_file_handler() -> None:
  """Add file handler"""
  file_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
  file_handler = logging.FileHandler('logs.log')
  file_handler.setLevel(logging.ERROR)
  file_handler.setFormatter(file_format)
  logger.addHandler(file_handler)


colored_formatter = ColoredFormatter("%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
                                     datefmt='%H:%M:%S',
                                     log_colors={
                                       'MSG': 'purple,bold',
                                       'DEBUG': 'cyan',
                                       'INFO': 'green',
                                       'WARNING': 'yellow',
                                       'ERROR': 'red',
                                       'CRITICAL': 'red',
                                     })

logging.addLevelName(5, 'MSG')
logger = logging.getLogger('luscious_dl')

console_format = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S')
console_handler = logging.StreamHandler()
console_handler.setFormatter(colored_formatter)

logger.addHandler(console_handler)
logger.setLevel(5)


if __name__ == '__main__':
  logger.log(5, 'random msg')
  logger.info('info msg')
  logger.warning('warning msg')
  logger.debug('debug msg')
  logger.error('error msg')
  logger.critical('critical msg')
