import json
import os
from typing import Any

from luscious_dl import __version__
from luscious_dl.logger import logger


def info() -> None:
  """Show package version"""
  logger.info(f'Luscious Downloader version: {__version__}')


def cls() -> None:
  """Clears the command prompt"""
  os.system('cls' if os.name == 'nt' else 'clear')


"""def format_filename(name: str) -> str:
  pass"""


def get_config_setting(setting: str) -> Any:
  """
  Retrieve the key value
  :param setting: json key
  :return: key value
  """
  with open('./config.json') as config:
    data = json.load(config)
  return data[setting]


def read_list() -> list[str]:
  """
  Read text file content.
  :return: list content
  """
  try:
    logger.log(5, 'Reading list...')
    with open('./list.txt') as file:
      list_txt = file.read().split('\n')
      logger.log(5, f'Total of Items: {len(list_txt)}.')
    return list_txt
  except Exception as e:
    print(f'Failed to read the list.txt.\n{e}')


def create_default_files() -> None:
  """Create the initial files when using the menu"""
  if not os.path.exists('./config.json'):
    data = {
      "directory": "./Albums/",
      "pool": os.cpu_count(),
      "retries": 5,
      "timeout": 30,
      "delay": 0
    }
    with open('./config.json', 'a+') as config_file:
      json.dump(data, config_file, indent=2)
  if not os.path.exists('./list.xt'):
    open('./list.txt', 'a+')
  if not os.path.exists('./list_completed.txt'):
    open('./list_completed.txt', 'a+')


def create_folder(directory: str) -> None:
  """
  Creates folder in the specified path.
  :param directory: folder path
  """
  try:
    if not os.path.exists(directory):
      os.makedirs(directory, exist_ok=True)
      logger.info(f'Album folder created in: {directory}')
    else:
      logger.warn(f'Album folder already exist in: {directory}')
  except OSError:
    logger.error(f'Creating directory in: {directory}')


class ListOrganizer:
  @staticmethod
  def add(string: str) -> None:
    """
    Add string to list_completed.txt
    :param string: Mostly URL or ID of Album or User
    """
    with open('./list_completed.txt') as completed:
      text = completed.read()
    with open('./list_completed.txt', 'a') as completed:
      if not text.endswith('\n'):
        completed.write('\n')
      completed.write(string)
      logger.log(5, f'Added to completed list: {string}')

  @staticmethod
  def remove(string: str) -> None:
    """
    Remove string from list.txt
    :param string: Mostly URL or ID of Album or User
    """
    with open('./list.txt') as list_txt:
      temp = ['' if string in line else line for line in list_txt]
    with open('./list.txt', 'w') as list_txt:
      for line in temp:
        list_txt.write(line)


def open_config_menu() -> None:
  """Open config.json menu"""
  with open('./config.json', 'r+') as j:
    data = json.load(j)
    while True:
      config_menu = input(f'1 - Change Directory [Current: {data["directory"]}]\n'
                          f'2 - CPU Pool [Current: {data["pool"]}]\n'
                          f'3 - Picture Retries [Current: {data["retries"]}]\n'
                          f'4 - Picture Timeout [Current: {data["timeout"]}]\n'
                          f'5 - Download Delay [Current: {data["delay"]}]\n'
                          '0 - Back and Save.\n'
                          '> ')
      cls()
      if config_menu == '1':
        new_path = input(f'Current directory: {data["directory"]}\n'
                         '1 - Restore default directory\n'
                         '0 - Back\n'
                         'Directory: ')
        if new_path not in ['0', '1', ' ']:
          data['directory'] = os.path.normcase(new_path)
        elif new_path == '1':
          data['directory'] = './Albums/'
        else:
          pass
      elif config_menu == '2':
        print(f'You have: {os.cpu_count()} cores.')
        data['pool'] = int(input('Enter CPU Pool for download pictures.\n> '))
      elif config_menu == '3':
        data['retries'] = int(input('Enter how many pictures retries.\n> '))
      elif config_menu == '4':
        data['timeout'] = int(input('Enter picture timeout.\n> '))
      elif config_menu == '5':
        data['delay'] = int(input('Enter album download delay.\n> '))
      elif config_menu == '0':
        cls()
        break
      else:
        print('Invalid Option.\n')
    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()
