import os
from argparse import Namespace
from copy import copy
from pathlib import Path

from luscious_dl.logger import logger_file_handler, logger
from luscious_dl.parser import is_a_valid_integer
from luscious_dl.start import start
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_data, read_list, info, \
  ListFilesManager, inputs_string_to_list


def list_txt_organizer(items: list[str], prefix: str) -> None:
  """
  Remove from list.txt and then add to list_completed.txt
  :param items: List of urls or ids
  :param prefix: album/user
  """
  for item in items:
    ListFilesManager.remove(item)
    ListFilesManager.add(f'{prefix}-{int(item)}' if is_a_valid_integer(item) else item)


def load_settings() -> Namespace:
  configs = get_config_data()
  base_namespace = Namespace(
    output_dir=Path(os.path.normcase(configs.get('directory', './albums/'))).resolve(),
    threads=configs.get('pool', os.cpu_count() or 1),
    retries=configs.get('retries', 5),
    timeout=configs.get('timeout', 30),
    delay=configs.get('delay', 0),
    foldername_format=configs.get('foldername_format', '%t'),
    gen_pdf=configs.get('gen_pdf', False),
    gen_cbz=configs.get('gen_cbz', False),
    rm_origin_dir=configs.get('rm_origin_dir', False),
    group_by_user=configs.get('group_by_user', False),
    album_inputs=None, user_inputs=None, only_favorites=False,
    keyword=None, search_download=False, sorting='date_trending', page=1, max_pages=1
  )
  return base_namespace


def menu() -> None:
  """Menu"""
  info()
  create_default_files()
  logger_file_handler()
  base_namespace = load_settings()

  while True:
    option = input('Options:\n'
                   '1 - Download albums by URL or ID.\n'
                   '2 - Download all user albums.\n'
                   '3 - Download all user favorites.\n'
                   '4 - Search albums by keyword.\n'
                   '5 - Download albums from list.txt.\n'
                   '6 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')

    if option in ('1', '2', '3'):
      inputs = input('\n0 - Back.\n'
                     f'Enter {"album" if option == "1" else "user"} URL or ID.\n> ')
      cls()
      if inputs != '0':
        args = copy(base_namespace)
        args.album_inputs = inputs if option == '1' else None
        args.user_inputs = inputs if option in ('2', '3') else None
        args.only_favorites = option == '3'
        start(args)
        list_txt_organizer(inputs_string_to_list(inputs), 'album' if option == '1' else 'user')
        logger.log(5, 'URLs/IDs added to completed list.')

    elif option == '4':
      keyword = input('Enter keyword\n> ')
      if not keyword:
        print('Please enter a keyword.\n')
        return
      page = input('Enter starting page number or leave blank\n> ')
      page = int(page) if is_a_valid_integer(page) else 1
      max_pages = input('Enter max page or leave blank\n> ')
      max_pages = int(max_pages) if is_a_valid_integer(max_pages) else 1
      search_download = input('Download search results? ("Y/N") ').strip() in 'yY'
      args = copy(base_namespace)
      args.keyword = keyword
      args.search_download = search_download
      args.page = page
      args.max_pages = max_pages
      start(args)

    elif option == '5':
      list_txt = list(set(read_list()))
      args = copy(base_namespace)
      args.album_inputs = ','.join(list_txt)
      start(args)
      list_txt_organizer(list_txt, 'album')
      logger.log(5, 'URLs/IDs added to completed list.')

    elif option == '6':
      open_config_menu()
      base_namespace = load_settings()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
