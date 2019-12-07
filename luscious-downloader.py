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
from lxml import html
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
        "poolLinks": os.cpu_count()-1,
        "poolDown": os.cpu_count()-1
      }
    with open('./config.json', 'a+') as x:
      json.dump(data, x, indent=2)
  if not (os.path.exists('./list.xt')):
    open('./list.txt', 'a+')
  if not (os.path.exists('./list_completed.txt')):
    open('./list_completed.txt', 'a+')


def create_folder(directory):
  try:
    if not os.path.exists(directory):
      os.makedirs(directory)
      print(f"Album Folder Created: {directory}")
  except OSError:
    print(f"Error: Creating directory: {directory}")


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

  if action == 'completed':
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
      print("1 - Change Directory."
            f"\n2 - Switch MultiProcess [Status: {data['multiprocess']}]."
            "\n3 - CPU Pool."
            "\n0 - Back.")
      selected_setting = str(input(">"))
      cls()
      if selected_setting == '1':
        print(f"For default enter 0\nCurrent directory: {data['directory']}")
        directory = str(input("Directory: "))
        if directory == '0' or ' ':
          data['directory'] = './Albums/'
        else:
          data['directory'] = directory
      elif selected_setting == '2':
        if data['multiprocess']:
          data['multiprocess'] = False
          print("MultiProcess Disabled.\n")
        elif not data['multiprocess']:
          data['multiprocess'] = True
          print("MultiProcess Enabled.\n")
      elif selected_setting == '3':
        print(f"You have: {os.cpu_count()} cpus.\nRecommend Pool: {os.cpu_count()-1}")
        print("Enter CPU Pool for Geting Direct Imgs Links.")
        data['poolLinks'] = int(input("> "))
        print("Enter CPU Pool for Download Pictures.")
        data['poolDown'] = int(input("> "))
      elif selected_setting == '0':
        cls()
        break
      else:
        print("Invalid Option.\n")
    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()


def get_individual_image_page_urls(corrected_album_url):
  n = 1
  data = []
  while True:
    json_page_request = requests.get(f"{corrected_album_url}sorted/newest/page/{n}/.json/").json()
    source = json_page_request['html']
    tree = html.fromstring(source)
    data.append(tree.xpath('//*[@class="item thumbnail ic_container"]/a/@href'))
    n += 1
    if json_page_request['paginator_complete']:
      break
  partial_image_page_urls = [x for sublist in data for x in sublist]
  return ['https://members.luscious.net' + x for x in partial_image_page_urls]


def show_album_info(tree):
  try:
    album_name = tree.xpath('//*[@class="column sidebar"]//h3[contains(text(),"In album:")]/a/text()')[0]
    pictures = tree.xpath('//*[@class="column sidebar"]/div/p[contains(text(),"pictures total")]/text()')[0]
    print(f"Album Name: {album_name}\n"
          f"{pictures}")
  except Exception as e:
    print(f"Failed to print album information.\nError: {e}")


def download(album_url):
  corrected_album_url = re.sub('/albums/', '/pictures/album/', album_url)

  html_source = requests.get(corrected_album_url).content
  tree = html.fromstring(html_source)

  album_name = tree.xpath('//*[@class="column sidebar"]//h3/a/text()')[0]

  show_album_info(tree)

  directory = get_config_setting('directory')
  multiprocess = get_config_setting('multiprocess')
  pool_links = get_config_setting('poolLinks')
  pool_downs = get_config_setting('poolDown')

  print("Loading entire page...")
  individual_image_page_urls = get_individual_image_page_urls(corrected_album_url)
  print(f"Total of {len(individual_image_page_urls)} real links found.")

  album_name = re.sub('[^\w\-_\. ]', '_', album_name)
  create_folder(f"{directory}{album_name}/")

  if multiprocess == "legacy":
    print("[Legacy] Starting Download.")
    time.sleep(1)
    for individual_image_page_url in tqdm(individual_image_page_urls, total=(len(individual_image_page_urls))):
      download_picture(get_direct_image_link(individual_image_page_url), directory, album_name)

  elif multiprocess:
    print("[MultiProcess] Getting Direct Images Links.")
    direct_images_urls = p_umap(get_direct_image_link, individual_image_page_urls,
                                total=len(individual_image_page_urls), num_cpus=pool_links)

    print("[MultiProcess] Starting Download Pictures.")
    p_umap(download_picture, direct_images_urls, directory, album_name,
           total=len(direct_images_urls), num_cpus=pool_downs)

  elif not multiprocess:
    direct_images_urls = []
    print("Getting Direct Images Links")
    for individual_image_page_url in tqdm(individual_image_page_urls, total=len(individual_image_page_urls)):
      direct_images_urls.append(get_direct_image_link(individual_image_page_url))

    print("Starting Download Pictures.")
    for direct_image_url in tqdm(direct_images_urls):
      download_picture(direct_image_url, directory, album_name)

  print(f"\nAlbum: > {album_name} < Download Completed {len(individual_image_page_urls)} pictures has saved."
        f"\nURL: {album_url}\n")
  list_organizer(album_url, 'completed')


def get_direct_image_link(page_url):
  try:
    return html.fromstring(requests.get(page_url).content).xpath('//*[@class="icon-download"]/@href')[0]
  except Exception as e:
    print(f"\nFailed to get direct link from {page_url}\nError: {e}")


def download_picture(picture_url, directory, album_name):
  try:
    picture_path = f"{directory}{album_name}/{picture_url.rsplit('/', 1)[1]}"
    if not(os.path.exists(picture_path)):
      wget.download(picture_url, picture_path, bar=None)
  except Exception as e:
    print(f"\nFailed to download picture: {picture_url}\nError: {e}")


if __name__ == "__main__":
  create_default_files()
  while True:
    print("Options:"
          "\n1 - Enter Album URL."
          "\n2 - Download from list.txt."
          "\n3 - Settings."
          "\n0 - Exit.")
    option = str(input("> "))
    cls()

    if option == '1':
      input_url = input("0 - Back.\nAlbum URL: ")
      if input_url != '0':
        cls()
        download(input_url)
      else:
        cls()

    elif option == '2':
      print("Checking List...")
      with open('list.txt') as url_list:
        quantity = len(open('list.txt').readlines())
        print(f"Total of Links: {quantity} \n")
        for url in url_list:
          download(url)

    elif option == '3':
      open_config_menu()

    elif option == '0':
      print("Xau ;-;")
      time.sleep(1)
      exit()

    else:
      print("Invalid Option\n")
