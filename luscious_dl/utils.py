# -*- coding: utf-8 -*-
import os
import json

from luscious_dl.logger import logger


def cls():
  os.system('cls' if os.name == 'nt' else 'clear')


def get_config_setting(setting):
  with open('./config.json') as config:
    data = json.load(config)
  return data[setting]


def create_default_files():
  if not (os.path.exists('./config.json')):
    data = {
      "directory": "./Albums/",
      "pool": os.cpu_count()
    }
    with open('./config.json', 'a+') as config_file:
      json.dump(data, config_file, indent=2)
  if not (os.path.exists('./list.xt')):
    open('./list.txt', 'a+')
  if not (os.path.exists('./list_completed.txt')):
    open('./list_completed.txt', 'a+')


def create_folder(directory):
  try:
    if not os.path.exists(directory):
      os.makedirs(directory)
      logger.info(f'Album folder created: {directory}')
    else:
      logger.warn(f'Album folder {directory} already exist.')
  except OSError:
    logger.error(f'Creating directory: {directory}')


def list_organizer(album_url):
  with open('./list.txt') as list_txt:
    temp = ['' if album_url in line else line for line in list_txt]
  with open('./list.txt', 'w') as list_txt:
    for line in temp:
      list_txt.write(line)
  with open('./list_completed.txt') as completed:
    text = completed.read()
  with open('./list_completed.txt', 'a') as completed:
    if not text.endswith('\n'):
      completed.write('\n')
    completed.write(album_url)
    logger.log(5, 'Album url added to completed list.')


def open_config_menu():
  with open('./config.json', 'r+') as j:
    data = json.load(j)
    while True:
      config_menu = input(f'1 - Change Directory [Current: {data["directory"]}]\n'
                          f'2 - CPU Pool [Current: {data["pool"]}]\n'
                          '0 - Back and Save.\n'
                          '> ')
      cls()
      if config_menu == '1':
        new_path = input('For default directory enter 0\n'
                         f'Current directory: {data["directory"]}\n'
                         'Directory: ')
        if new_path not in ['0', ' ']:
          new_path = new_path.replace('\\', '/')
          data['directory'] = new_path if new_path.endswith('/') else f'{new_path}/'
        else:
          data['directory'] = './Albums/'
      elif config_menu == '2':
        print(f'You have: {os.cpu_count()} cores.')
        data['pool'] = int(input('Enter CPU Pool for Download Pictures.\n> '))
      elif config_menu == '0':
        cls()
        break
      else:
        print('Invalid Option.\n')
    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()
