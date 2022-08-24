from copy import copy

from luscious_dl.logger import logger_file_handler, logger
from luscious_dl.parser import is_a_valid_integer
from luscious_dl.start import start
from luscious_dl.utils import cls, create_default_files, open_config_menu, read_list, info, list_txt_organizer, \
  inputs_string_to_list, get_root_path, load_settings


def menu() -> None:
  """Menu"""
  info()
  create_default_files()
  logger_file_handler()
  base_namespace = load_settings()

  while True:
    print(*(
      'Options:',
      '1 - Download albums by URL or ID.',
      '2 - Download all user albums.',
      '3 - Download all user favorites.',
      '4 - Search albums by keyword.',
      '5 - Download albums from list.txt.',
      '6 - Settings.',
      '0 - Exit.'
    ), sep='\n')
    option = input('> ')

    if option in ('1', '2', '3'):
      inputs = input('\n0 - Back.\n'
                     f'Enter {"album" if option == "1" else "user"} URL or ID.\n> ')
      cls()
      if inputs == '0':
        continue
      args = copy(base_namespace)
      args.album_inputs = inputs if option == '1' else None
      args.user_inputs = inputs if option in ('2', '3') else None
      args.only_favorites = option == '3'
      start(args)
      list_txt_organizer(inputs_string_to_list(inputs), 'album' if option == '1' else 'user')
      logger.log(5, 'URLs/IDs added to completed list.')

    elif option == '4':
      keyword = input('\n0 - Back\nEnter keyword\n> ')
      if not keyword:
        print('Please enter a keyword.\n')
        continue
      if keyword == '0':
        cls()
        continue
      page = input('Enter starting page number or leave blank\n> ')
      page = int(page) if is_a_valid_integer(page) else 1
      max_pages = input('Enter max page or leave blank\n> ')
      max_pages = int(max_pages) if is_a_valid_integer(max_pages) else 1
      search_download = input('Download search results? ("Y/N") ').strip()
      search_download = search_download in 'yY' and search_download != ''

      args = copy(base_namespace)
      args.keyword = keyword
      args.search_download = search_download
      args.page = page
      args.max_pages = max_pages
      start(args)

    elif option == '5':
      list_txt = read_list(get_root_path())
      if len(list_txt) > 0:
        args = copy(base_namespace)
        args.album_inputs = ','.join(list_txt)
        start(args)
        list_txt_organizer(list_txt, 'album')
        logger.log(5, 'URLs/IDs added to completed list.')
      else:
        logger.log(5, 'List.txt is empty.')

    elif option == '6':
      open_config_menu()
      base_namespace = load_settings()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == '__main__':
  menu()
