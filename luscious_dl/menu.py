import os
from argparse import Namespace

from luscious_dl.logger import logger_file_handler, logger
from luscious_dl.parser import is_a_valid_integer
from luscious_dl.start import start
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_setting, read_list, info, \
  ListOrganizer


def list_txt_organizer(items: list[str], prefix: str) -> None:
  """
  :param items: List of urls or ids
  :param prefix: album/user
  """
  for item in items:
    ListOrganizer.remove(item)
    ListOrganizer.add(f'{prefix}-{int(item)}' if is_a_valid_integer(item) else item)


def create_namespace(album_inputs=None, user_inputs=None, keyword=None, search_download=False, page=1, max_pages=1,
                     directory=None, threads=os.cpu_count(), retries=5, timeout=30, delay=0) -> Namespace:
  return Namespace(album_inputs=album_inputs, user_inputs=user_inputs, keyword=keyword, search_download=search_download,
                   page=page, max_pages=max_pages, directory=directory, threads=threads, retries=retries,
                   timeout=timeout, delay=delay)


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

  while True:
    option = input('Options:\n'
                   '1 - Download albums by URL or ID.\n'
                   '2 - Download all user albums\n'
                   '3 - Download albums from list.txt.\n'
                   '4 - Search albums by keyword.\n'
                   '5 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')
    cls()

    if option in ['1', '2']:
      inputs = input('0 - Back.\n'
                     f'Enter {"album" if option == "1" else "user"} URL or ID.\n> ')
      cls()
      if inputs != '0':
        args = create_namespace(album_inputs=inputs if option == '1' else None,
                                user_inputs=inputs if option == '2' else None,
                                directory=output_dir, threads=pool_size, retries=retries, timeout=timeout, delay=delay)
        start(args)
        list_txt_organizer([input_.strip() for input_ in inputs.split(',')], 'album' if option == '1' else 'user')
        logger.log(5, 'URLs/IDs added to completed list.')

    elif option == '3':
      list_txt = read_list()
      args = create_namespace(album_inputs=','.join(list_txt),
                              directory=output_dir, threads=pool_size, retries=retries, timeout=timeout, delay=delay)
      start(args)
      list_txt_organizer(list_txt, 'album')
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
      search_download = True if input('Download search results? ("Y/N") ').strip() in 'yY' else False
      args = create_namespace(keyword=keyword, search_download=search_download, page=page, max_pages=max_pages)
      start(args)

    elif option == '5':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
