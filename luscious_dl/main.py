# -*- coding: utf-8 -*-
from luscious_dl.logger import logger
from luscious_dl.utils import cls, create_default_files, open_config_menu
from luscious_dl.downloader import start


def main() -> None:
  create_default_files()
  while True:
    option = input('Options:\n'
                   '1 - Enter album URL.\n'
                   '2 - Download from list.txt.\n'
                   '3 - Settings.\n'
                   '0 - Exit.\n'
                   '> ')
    cls()

    if option == '1':
      input_url = input('0 - Back.\n'
                        'Album URL: ')
      if input_url != '0':
        cls()
        start(input_url)
      else:
        cls()

    elif option == '2':
      logger.log(5, 'Checking List.')
      with open('./list.txt') as x:
        url_list = x.readlines()
        logger.log(5, f'Total of Links: {len(url_list)}.')
      for url in url_list:
        start(url.rstrip('\n'))

    elif option == '3':
      open_config_menu()

    elif option == '0':
      exit()

    else:
      print('Invalid Option.\n')


if __name__ == "__main__":
  main()
