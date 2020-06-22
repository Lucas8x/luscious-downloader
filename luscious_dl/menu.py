# -*- coding: utf-8 -*-
import os

from luscious_dl.logger import logger
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_setting
from luscious_dl.downloader import start


def menu() -> None:
  create_default_files()
  output_dir = os.path.abspath(os.path.normcase(get_config_setting('directory')))
  pool_size = get_config_setting('pool')
  retries = get_config_setting('retries')
  timeout = get_config_setting('timeout')
  delay = get_config_setting('delay')

  while True:
    option = input('Options:\n'
                   '1 - Enter album URL or ID.\n'
                   '2 - Download from list.txt.\n'
                   '3 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')
    cls()

    if option == '1':
      input_url_or_id = input('0 - Back.\n'
                              'Album URL/ID: ')
      if input_url_or_id != '0':
        cls()
        start(input_url_or_id, output_dir, pool_size, retries, timeout, delay, True)
      else:
        cls()

    elif option == '2':
      logger.log(5, 'Checking List.')
      with open('./list.txt') as x:
        list_txt = x.readlines()
        logger.log(5, f'Total of Links: {len(list_txt)}.')
      for line in list_txt:
        album_url_or_id = line.rstrip('\n')
        start(album_url_or_id, output_dir, pool_size, retries, timeout, delay, True)

    elif option == '3':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
