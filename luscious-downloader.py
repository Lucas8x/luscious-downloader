#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auto Download Luscious Pictures for you
pip install -r requirements.txt
"""
import os
import re
import time
import wget
import requests
from p_tqdm import *
import json
import locale
locale.setlocale(locale.LC_ALL, '')


def cls():
  os.system('cls' if os.name == 'nt' else 'clear')


def get_config_setting(setting):
  with open('config.json') as config:
    data = json.load(config)
  return data[setting]


def create_default_files():
  if not (os.path.exists('./config.json')):
    data = {
      "directory": "./Albums/",
      "multiprocess": True,
      "poolDown": os.cpu_count()-1
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
      print(f'Album Folder Created: {directory}')
  except OSError:
    print(f'Error: Creating directory: {directory}')


def list_organizer(album_url, action):
  list_txt = open('./list.txt')
  temp = []
  for line in list_txt:
    if album_url in line:
      line = line.replace(album_url, '')
    temp.append(line)
  list_txt.close()
  list_txt = open('./list.txt', 'w')
  for line in temp:
    list_txt.write(line)
  list_txt.close()

  if action:
    with open('./list_completed.txt') as completed:
      text = completed.read()
    with open('./list_completed.txt', 'a') as completed:
      if not text.endswith("\n"):
        completed.write('\n')
      completed.write(album_url)
    completed.close()


def open_config_menu():
  with open('config.json', 'r+') as j:
    data = json.load(j)
    while True:
      config_menu = input(f'1 - Change Directory [Current: {data["directory"]}].\n'
                          f'2 - Switch MultiProcess [Status: {data["multiprocess"]}].\n'
                          '3 - CPU Pool.\n'
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
        if data['multiprocess']:
          data['multiprocess'] = False
          print('MultiProcess Disabled.\n')
        elif not data['multiprocess']:
          data['multiprocess'] = True
          print('MultiProcess Enabled.\n')
      elif config_menu == '3':
        print(f'You have: {os.cpu_count()} cpus.\n'
              f'Recommend Pool: {os.cpu_count()-1}')
        data['poolDown'] = int(input('Enter CPU Pool for Download Pictures.\n'
                                     '> '))
      elif config_menu == '0':
        cls()
        break
      else:
        print("Invalid Option.\n")
    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()


def get_album_id(album_url):
  album_id = album_url.rsplit('/', 2)[1].rsplit('_', 1)[1] if album_url.endswith('/') \
    else album_url.rsplit('/', 1)[1].rsplit('_', 1)[1]
  if album_id:
    return album_id
  else:
    return
  #return album_id if album_id else


def get_album_info(album_id):
  response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumGet', json={
    "id": 6,
    "operationName": "AlbumGet",
    "query": "query AlbumGet($id: ID!) {album {get(id: $id) {... on Album {...AlbumStandard} ... on MutationError {errors {code message}}}}} fragment AlbumStandard on Album {id title number_of_pictures}",
    "variables": {
      "id": album_id
    }
  }).json()
  return response['data']['album']['get']


def get_pictures_urls(album_id):
  n = 1
  raw_data = []
  while True:
    response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumListOwnPictures', json={
      "id": 7,
      "operationName": "AlbumListOwnPictures",
      "query": "query AlbumListOwnPictures($input: PictureListInput!) {picture {list(input: $input) {info {...FacetCollectionInfo} items {...PictureStandardWithoutAlbum}}}} fragment FacetCollectionInfo on FacetCollectionInfo {page has_next_page has_previous_page total_items total_pages items_per_page url_complete} fragment PictureStandardWithoutAlbum on Picture {url_to_original url_to_video url}",
      "variables": {
        "input": {
          "filters": [
            {
              "name": "album_id",
              "value": album_id
            }
          ],
          "display": "rating_all_time",
          "page": n
        }
      }
    }).json()
    raw_data.append(response['data']['picture']['list']['items'])
    n += 1
    if not response['data']['picture']['list']['info']['has_next_page']:
      break
  data = [obj['url_to_original'] for arr in raw_data for obj in arr]
  return data


def show_album_info(album):
  try:
    print(f'Album Name: {album["title"]}\n'
          f'Total of {album["number_of_pictures"]} pictures')
  except Exception as e:
    print('Failed to print album information.\n'
          f'Error: {e}')


def download(album_url):
  album_id = get_album_id(album_url)
  album_info = get_album_info(album_id)
  album_name = album_info['title']
  show_album_info(album_info)
  directory = get_config_setting('directory')
  multiprocess = get_config_setting('multiprocess')
  pool_downs = get_config_setting('poolDown')

  print('Getting pictures urls...')
  picture_page_urls = get_pictures_urls(album_id)
  print(f'Total of {len(picture_page_urls)} real links found.')

  album_name = re.sub('[^\w\-_\. ]', '_', album_name)
  create_folder(f'{directory}{album_name}/')

  if multiprocess:
    print('[MultiProcess] Starting Download Pictures.')
    p_umap(download_picture, picture_page_urls, directory, album_name,
           total=len(picture_page_urls), num_cpus=pool_downs)

  elif not multiprocess:
    print('Starting Download Pictures.')
    for picture_url in tqdm(picture_page_urls):
      download_picture(picture_url, directory, album_name)

  print(f'\nAlbum: > {album_name} < Download Completed {len(picture_page_urls)} pictures has saved.'
        f'\nURL: {album_url}\n')
  list_organizer(album_url, True)


def download_picture(picture_url, directory, album_name):
  try:
    picture_path = f'{directory}{album_name}/{picture_url.rsplit("/", 1)[1]}'
    if not(os.path.exists(picture_path)):
      wget.download(picture_url, picture_path, bar=None)
  except Exception as e:
    print(f'\nFailed to download picture: {picture_url}\nError: {e}')


if __name__ == "__main__":
  create_default_files()
  while True:
    option = input('Options:\n'
                   '1 - Enter Album URL.\n'
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
        download(input_url)
      else:
        cls()

    elif option == '2':
      print('Checking List...')
      with open('list.txt') as x:
        url_list = x.readlines()
        print(f'Total of Links: {len(url_list)} \n')
      for url in url_list:
        download(url.rstrip('\n'))

    elif option == '3':
      open_config_menu()

    elif option == '0':
      print('Xau ;-;')
      time.sleep(1)
      exit()

    else:
      print('Invalid Option\n')
