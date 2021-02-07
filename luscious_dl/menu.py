import os
from typing import Callable

from luscious_dl.downloader import Downloader
from luscious_dl.logger import logger, logger_file_handler
from luscious_dl.parser import extract_user_id, is_a_valid_id, extract_album_id, extract_ids_from_list
from luscious_dl.start import albums_download, users_download
from luscious_dl.utils import cls, create_default_files, open_config_menu, get_config_setting, read_list, info, \
  ListOrganizer


def list_txt_organizer(items: list[str], prefix: str) -> None:
  """
  :param items: List of urls or ids
  :param prefix: album/user
  """
  for item in items:
    ListOrganizer.remove(item)
    ListOrganizer.add(f'{prefix}-{int(item)}' if is_a_valid_id(item) else item)


def download(function: Callable[[list[int], Downloader], None], inputs: list[str], extractor: Callable[[str], int],
             downloader: Downloader, prefix: str):
  ids = extract_ids_from_list(inputs, extractor)
  function(ids, downloader)
  list_txt_organizer(inputs, prefix)
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
                   '1 - Download albums by URL or ID.\n'
                   '2 - Download all user albums\n'
                   '3 - Download albums from list.txt.\n'
                   '4 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')
    cls()

    if option in ['1', '2']:
      inputs = input('0 - Back.\n'
                     f'Enter {"album" if option == "1" else "user"} URL or ID.\n> ')
      cls()
      if inputs != '0':
        download(albums_download if option == '1' else users_download,
                 [input_.strip() for input_ in inputs.split(',')],
                 extract_album_id if option == '1' else extract_user_id,
                 downloader,
                 'album' if option == '1' else 'user'
                 )

    elif option == '3':
      list_txt = read_list()
      download(albums_download, list_txt, extract_album_id, downloader, 'album')

    elif option == '4':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
