# -*- coding: utf-8 -*-
import os
from typing import List

from luscious_dl.logger import logger, logger_file_handler
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_setting, read_list, info, \
  ListOrganizer
from luscious_dl.downloader import Downloader
from luscious_dl.parser import extract_user_id, is_a_valid_id, extract_album_id, extract_ids_from_list
from luscious_dl.start import albums_download, users_download


def list_txt_organizer(items: List[str], prefix: str) -> None:
  """
  :param items: List of urls or ids
  :param prefix: album/user
  """
  for item in items:
    ListOrganizer.remove(item)
    ListOrganizer.add(f'{prefix}-{int(item)}' if is_a_valid_id(item) else item)


def enter_inputs(option: str, downloader: Downloader):
  """
  :param option: selected option
  :param downloader: Downloder object
  """
  inputs = input(f'0 - Back.\nEnter {"album" if option == "1" else "user"} URL or ID.\n> ')
  if inputs != '0':
    cls()
    inputs = [input_.strip() for input_ in inputs.split(',')]
    ids = extract_ids_from_list(inputs, extract_album_id if option == '1' else extract_user_id)
    albums_download(ids, downloader) if option == '1' else users_download(ids, downloader)
    list_txt_organizer(inputs, 'album' if option == '1' else 'user')
    logger.log(5, 'URLs/IDs added to completed list.')


def menu() -> None:
  """Menu"""
  info()
  create_default_files()
  logger_file_handler()
  output_dir = os.path.abspath(os.path.normcase(get_config_setting('directory')))
  pool_size = get_config_setting('pool')
  retries = get_config_setting('retries')
  timeout = get_config_setting('timeout')
  delay = get_config_setting('delay')

  downloader = Downloader(output_dir, pool_size, retries, timeout, delay)

  while True:
    option = input('Options:\n'
                   '1 - Enter albums URL or ID.\n'
                   '2 - Download all user albums\n'
                   '3 - Download albums from list.txt.\n'
                   '4 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')
    cls()

    if option in ['1', '2']:
      enter_inputs(option, downloader)

    elif option == '3':
      list_txt = read_list()
      albums_ids = extract_ids_from_list(list_txt, extract_album_id)
      albums_download(albums_ids, downloader)
      list_txt_organizer(list_txt, 'album')

    elif option == '4':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
