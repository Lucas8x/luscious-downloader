# -*- coding: utf-8 -*-
import os

from luscious_dl.logger import logger
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_setting, list_organizer, read_list
from luscious_dl.downloader import Downloader
from luscious_dl.parser import extract_album_id, extract_user_id, is_a_valid_id
from luscious_dl.start import albums_download, users_download


def menu() -> None:
  create_default_files()
  output_dir = os.path.abspath(os.path.normcase(get_config_setting('directory')))
  pool_size = get_config_setting('pool')
  retries = get_config_setting('retries')
  timeout = get_config_setting('timeout')
  delay = get_config_setting('delay')

  downloader = Downloader(output_dir, pool_size, retries, timeout, delay)

  while True:
    option = input('Options:\n'
                   '1 - Enter albums by URL or ID.\n'
                   '2 - Download all user albums\n'
                   '3 - Download albums from list.txt.\n'
                   '4 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')
    cls()

    if option == '1':
      input_url_or_ids = input('0 - Back.\nAlbum URL/ID: ')
      if input_url_or_ids != '0':
        cls()
        inputs = [input_.strip() for input_ in input_url_or_ids.split(',')]
        albums_ids = set(int(input_) if is_a_valid_id(input_) else extract_album_id(input_) for input_ in inputs)
        albums_download(albums_ids, downloader)
        for id_ in albums_ids:
          list_organizer(f'Album: {id_}')
        logger.log(5, 'Album urls added to completed list.')
      else:
        cls()

    elif option == '2':
      input_user_url_or_id = input('0 - Back.\nUser URL/ID: ')
      if input_user_url_or_id != '0':
        cls()
        inputs = [id_.strip() for id_ in input_user_url_or_id.split(',')]
        users_ids = set(int(input_) if is_a_valid_id(input_) else extract_user_id(input_) for input_ in inputs)
        users_download(users_ids, downloader)
        for id_ in users_ids:
          list_organizer(f'User: {id_}')
        logger.log(5, 'Users urls added to completed list.')

    elif option == '3':
      list_txt = read_list()
      for item in list_txt:
        id_ = int(item) if is_a_valid_id(item) else extract_album_id(item)
        albums_download([id_], downloader)
        list_organizer(item)

    elif option == '4':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
