from copy import copy

from luscious_dl.logger import logger_file_handler, logger
from luscious_dl.parser import is_a_valid_integer
from luscious_dl.start import start
from luscious_dl.utils import cls, create_default_files, open_config_menu, read_list, info, list_txt_organizer, \
  inputs_string_to_list, get_root_path, load_settings


def showMenu():
  print(
    'Options:',
    '1 - Download albums by URL or ID.',
    '2 - Download all user albums.',
    '3 - Download all user favorites.',
    '4 - Search albums by keyword.',
    '5 - Download albums from list.txt.',
    '6 - Settings.',
    '0 - Exit.',
    sep='\n'
  )


def download_album_or_user(option, namespace):
  inputs = input('\n0 - Back.\n'
                f'Enter {"album" if option == "1" else "user"} URL or ID.\n> ')
  cls()
  if inputs == '0':
    return
  namespace.album_inputs = inputs if option == '1' else None
  namespace.user_inputs = inputs if option in ('2', '3') else None
  namespace.only_favorites = option == '3'
  start(namespace)
  list_txt_organizer(inputs_string_to_list(inputs), 'album' if option == '1' else 'user')
  logger.log(5, 'URLs/IDs added to completed list.')


def search_by_keyword(namespace):
  keyword = input('\n0 - Back\nEnter keyword\n> ')
  if not keyword:
    return print('Please enter a keyword.\n')
  if keyword == '0':
    return cls()
  page = input('Enter starting page number or leave blank\n> ')
  page = int(page) if is_a_valid_integer(page) else 1
  max_pages = input('Enter max page or leave blank\n> ')
  max_pages = int(max_pages) if is_a_valid_integer(max_pages) else 1
  search_download = input('Download search results? ("Y/N") ').strip()
  search_download = search_download in 'yY' and search_download != ''
  namespace.keyword = keyword
  namespace.search_download = search_download
  namespace.page = page
  namespace.max_pages = max_pages
  start(namespace)


def download_from_list(namespace):
  list_txt = read_list(get_root_path())
  if not len(list_txt):
    return logger.log(5, 'List.txt is empty.')
  namespace.album_inputs = ','.join(list_txt)
  start(namespace)
  list_txt_organizer(list_txt, 'album')
  logger.log(5, 'URLs/IDs added to completed list.')



def menu() -> None:
  """Menu"""
  info()
  create_default_files()
  logger_file_handler()
  base_namespace = load_settings()

  while True:
    showMenu()
    option = input('> ')

    if option in ('1', '2', '3'):
      download_album_or_user(option, copy(base_namespace))

    elif option == '4':
      search_by_keyword(copy(base_namespace))

    elif option == '5':
      download_from_list(copy(base_namespace))

    elif option == '6':
      open_config_menu()
      base_namespace = load_settings()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
