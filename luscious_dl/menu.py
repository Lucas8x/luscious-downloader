import os
from argparse import Namespace
from pathlib import Path

from luscious_dl.logger import logger_file_handler, logger
from luscious_dl.parser import is_a_valid_integer
from luscious_dl.start import start
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_data, read_list, info, \
  ListFilesManager


def list_txt_organizer(items: list[str], prefix: str) -> None:
  """
  Remove from list.txt and then add to list_completed.txt
  :param items: List of urls or ids
  :param prefix: album/user
  """
  for item in items:
    ListFilesManager.remove(item)
    ListFilesManager.add(f'{prefix}-{int(item)}' if is_a_valid_integer(item) else item)


def create_namespace(album_inputs=None, user_inputs=None, keyword=None, search_download=False, page=1, max_pages=1,
                     output_dir=None, threads=os.cpu_count() or 1, retries=5, timeout=30, delay=0,
                     sorting='date_trending', foldername_format='%t', only_favorites=False, gen_pdf=False,
                     rm_origin_dir=False) -> Namespace:
  return Namespace(album_inputs=album_inputs, user_inputs=user_inputs, keyword=keyword, search_download=search_download,
                   page=page, max_pages=max_pages, output_dir=output_dir, threads=threads, retries=retries,
                   timeout=timeout, delay=delay, sorting=sorting, foldername_format=foldername_format,
                   only_favorites=only_favorites, gen_pdf=gen_pdf, rm_origin_dir=rm_origin_dir)


def menu() -> None:
  """Menu"""
  info()
  create_default_files()
  logger_file_handler()
  configs = get_config_data()
  output_dir = Path(os.path.normcase(configs.get('directory', './Albums/'))).resolve()
  pool_size = configs.get('pool', 1)
  retries = configs.get('retries', 5)
  timeout = configs.get('timeout', 30)
  delay = configs.get('delay', 0)
  foldername_format = configs.get('foldername_format', '%t')
  gen_pdf = configs.get('gen_pdf', False)
  rm_origin_dir = configs.get('rm_origin_dir', False)

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
        args = create_namespace(album_inputs=inputs if option == '1' else None,
                                user_inputs=inputs if option in ('2', '3') else None,
                                output_dir=output_dir, threads=pool_size, retries=retries, timeout=timeout, delay=delay,
                                foldername_format=foldername_format,
                                only_favorites=option == '3',
                                gen_pdf=gen_pdf, rm_origin_dir=rm_origin_dir)
        start(args)
        list_txt_organizer([input_.strip() for input_ in inputs.split(',')], 'album' if option == '1' else 'user')
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
      args = create_namespace(keyword=keyword, search_download=search_download, page=page, max_pages=max_pages)
      start(args)

    elif option == '5':
      list_txt = list(set(read_list()))
      args = create_namespace(album_inputs=','.join(list_txt),
                              output_dir=output_dir,
                              threads=pool_size, retries=retries, timeout=timeout, delay=delay)
      start(args)
      list_txt_organizer(list_txt, 'album')
      logger.log(5, 'URLs/IDs added to completed list.')

    elif option == '6':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
