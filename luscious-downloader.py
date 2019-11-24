#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auto Download Luscious Pictures for you
pip install -r requirements.txt
"""
import os
import re
import time
import wget
from lxml import html
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pickle
from p_tqdm import *
import json
import locale
locale.setlocale(locale.LC_ALL, '')


def cls():
  os.system('cls' if os.name == 'nt' else 'clear')


def get_json_setting(setting):
  with open('config.json') as config:
    data = json.load(config)
  return data[setting]


def create_default_files():
  if not (os.path.exists('./config.json')):
    data = {
        "directory": "./Albums/",
        "multiprocess": True,
        "poolLinks": os.cpu_count()-1,
        "poolDown": os.cpu_count()-1,
        "driver": "firefox",
        "doLogin": False,
        "username": "",
        "password": ""
      }
    with open('./config.json', 'a+') as x:
      json.dump(data, x, indent=2)
  if not (os.path.exists('./list.xt')):
    open('./list.txt', 'a+')
  if not (os.path.exists('./list_completed.txt')):
    open('./list_completed.txt', 'a+')
  if not (os.path.exists('./list_blocked.xt')):
    open('./list_blocked.txt', 'a+')


def create_folder(directory):
  try:
    if not os.path.exists(directory):
      os.makedirs(directory)
      print(f"Album Folder Created: {directory}")
  except OSError:
    print(f"Error: Creating directory: {directory}")


def list_organizer(album_url, type):
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

  # Write Download Album URL in Last Line #
  if type == 'completed':
    with open('./list_completed.txt') as completed:
      text = completed.read()
    with open('./list_completed.txt', 'a') as completed:
      if not text.endswith("\n"):
        completed.write('\n')
      completed.write(album_url)
    completed.close()

  # Write Blocked Album URL in Last Line #
  elif type == 'blocked':
    with open('./list_blocked.txt') as blocked:
      text = blocked.read()
    with open('./list_blocked.txt', 'a') as blocked:
      if not text.endswith("\n"):
        blocked.write('\n')
      blocked.write(album_url)
    blocked.close()


def config_json_settings():
  with open('config.json', 'r+') as j:
    data = json.load(j)
    while True:
      print("1 - Change Directory"
            "\n2 - Login Credentials"
            "\n3 - Switch Auto-Login [ Staus:", data['doLogin'], "]"
            "\n4 - Switch MultiProcess [ Status:", data['multiprocess'], "]"
            "\n5 - CPU Pool"
            "\n6 - Switch Driver [ Current:", data['driver'], "]"
            "\n0 - Back")
      selected_setting = str(input(">"))
      cls()
      if selected_setting == '1':
        print("For default write 0\nCurrent directory:", data['directory'])
        directory = str(input("Directory: "))
        if directory == "0" or " ":
          data['directory'] = './Albums/'
        else:
          data['directory'] = directory
      elif selected_setting == '2':
        data['username'] = str(input("Username:"))
        data['password'] = str(input("Password:"))
      elif selected_setting == '3':
        if data['doLogin']:
          data['doLogin'] = False
          print("Auto-Login Disabled")
        elif not data['doLogin']:
          data['doLogin'] = True
          print("Auto-Login Enabled")
      elif selected_setting == '4':
        if data['multiprocess']:
          data['multiprocess'] = False
          print("MultiProcess Disabled")
        elif not data['multiprocess']:
          data['multiprocess'] = True
          print("MultiProcess Enabled")
      elif selected_setting == '5':
        print("You have:", os.cpu_count(),"cpus. Recommend:", os.cpu_count()-1)
        print("Enter CPU Pool for Geting Direct Imgs Links")
        data['poolLinks'] = int(input("> "))
        print("Enter CPU Pool for Download Pictures")
        data['poolDown'] = int(input("> "))
      elif selected_setting == '6':
        if data['driver'] == 'chrome':
          data['driver'] = 'firefox'
          print("Switched to Firefox/Geckodriver")
        elif data['driver'] == 'firefox':
          data['driver'] = 'chrome'
          print("Switched to ChromeDriver")
        print("Restart is necessary\n")
      elif selected_setting == '0':
        cls()
        break
      else:
        print("Invalid Option\n")
    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()


# Initialize Web Driver #
def my_driver():
  global driver
  selected_driver = get_json_setting('driver')
  if selected_driver == 'firefox':
    options = Options()
    options.headless = True
    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    driver = webdriver.Firefox(options=options, executable_path='./geckodriver.exe', capabilities=firefox_capabilities)
  elif selected_driver == 'chrome':
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--hide-scrollbars')
    options.add_argument("no-sandbox")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--disable-popup-blocking')
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    options.add_argument('window-size=1920x1080')
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=en")
    options.add_argument("--disable-extensions")
    options.add_argument('test-type')
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome('./chromedriver.exe', options=options)
  return driver


def page_checker(album_url):
  do_login = get_json_setting('doLogin')
  if not do_login:
    html_source = requests.get(album_url).content
  else:
    driver = my_driver()
    time.sleep(1)
    driver.get(album_url)
    html_source = driver.page_source

  tree = html.fromstring(html_source)
  check = tree.xpath('//*[@id="frontpage"]/h1/text()')
  check = str(*check)
  if check == "404 Not Found":
    if do_login:
      print("Auto-Login is enabled")
      login(album_url)
    else:
      print(f"Blocked Album: {album_url} \nTry turn on auto-login and write your account info")
      list_organizer(album_url, 1)
  else:
    download(album_url, False, tree)


# Log in if it is set #
def login(album_url):
  if not (os.path.exists('./cookies.pkl')):
    print("Logging in...")
    driver.get('https://members.luscious.net/login/')
    username = get_json_setting('username')
    password = get_json_setting('password')
    driver.find_element_by_id('id_login').send_keys(username)
    driver.find_element_by_id('id_password').send_keys(password)
    driver.find_element_by_xpath("//input[@value='Sign In']").click()
    pickle.dump(driver.get_cookies(), open('./cookies.pkl', 'wb'))
  for cookie in pickle.load(open('./cookies.pkl', 'rb')):
    driver.add_cookie(cookie)
  driver.get(album_url)
  tree = html.fromstring(driver.page_source)
  download(album_url, True, tree)


# Load Entire page / get links / download #
def download(album_url, do_login, tree):
  album_name = tree.xpath('//*[@class="o-h3 o-row-gut-half"]/a/text()')
  uploader = tree.xpath('//*[@class="username-display"]/text()')
  pictures = tree.xpath('//*[@class="album-info-item"]/text()')[0]
  print("Album Name:", str(*album_name))
  print("Uploader:", str(*uploader))
  print("Total of", str(pictures))

  directory = get_json_setting('directory')
  multiprocess = get_json_setting('multiprocess')
  pool_links = get_json_setting('poolLinks')
  pool_downs = get_json_setting('poolDown')

  print("Loading entire page...")

  if (multiprocess or not multiprocess) and not do_login:
    n = 1
    data = []
    if len(data) > 0:
      data.clear()
    album_url = re.sub('/albums/', '/pictures/album/', album_url)
    while True:
      json_page_request = requests.get(album_url+'sorted/newest/page/'+str(n)+'/.json/').json()
      source = json_page_request['html']
      tree = html.fromstring(source)
      data.append(tree.xpath('//*[@class="item thumbnail ic_container"]/a/@href'))
      n += 1
      if json_page_request['paginator_complete']:
        break
    flat = [x for sublist in data for x in sublist]
    image_page_links = ['https://members.luscious.net' + x for x in flat]

  elif do_login or multiprocess == "legacy":
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
      driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
      ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
      time.sleep(5)
      new_height = driver.execute_script('return document.body.scrollHeight')
      if new_height == last_height:
        break
      last_height = new_height
    html_source = driver.page_source
    tree = html.fromstring(html_source)
    # List all photos on the page
    image_pages = tree.xpath('//*[@class="item thumbnail ic_container"]/a/@href')
    # Combine site + imgPages for get Individual Img Page Link
    image_page_links = ['https://members.luscious.net/' + x for x in image_pages]

  print("Total of", len(image_page_links), "real links found")

  # Create Album Folder
  album_name = re.sub('[^\w\-_\. ]', '_', str(*album_name))
  create_folder(directory + album_name + '/')

  # Acess imgPageLink and get direct link and download # Legacy Mode
  if multiprocess == "legacy":
    print("[Legacy] Downloading")
    time.sleep(1)
    for url in tqdm(image_page_links, total=(len(image_page_links))):
      download_picture(get_direct_image_link(url, do_login), directory, album_name)

  # Get Direct Images Links
  direct_images_links = []
  if not multiprocess or do_login:
    print("Getting Direct Images Links")
    for url in tqdm(image_page_links, total=len(image_page_links)):
      direct_images_links.append(get_direct_image_link(url, do_login))

  elif multiprocess and not do_login:
    print("[MultiProcess] Getting Direct Images Links")
    direct_images_links = (p_umap(get_direct_image_link, image_page_links, do_login, total=len(image_page_links), num_cpus=pool_links))

  # Download Pictures
  if not multiprocess:
    print("Starting Download Pictures")
    for url in tqdm(direct_images_links):
      download_picture(url, directory, album_name)

  elif multiprocess:
    print("[MultiProcess] Starting Download Pictures")
    p_umap(download_picture, direct_images_links, directory, album_name, total=len(direct_images_links), num_cpus=pool_downs)

  print(f"\nAlbum: {album_name} Download Completed {len(image_page_links)} pictures has saved\nURL: {album_url}\n")
  list_organizer(album_url, 'completed')


def get_direct_image_link(url, do_login):
  try:
    if not do_login:
      return html.fromstring(requests.get(url).content).xpath('//*[@class="icon-download"]/@href')[0]
    elif do_login:
      driver.get(url)
      return driver.find_element_by_class_name('icon-download').get_attribute('href')
  except:
    print(f"\nFailed to get direct link from {url}")


def download_picture(url, directory, album_name):
  try:
    picture_path = f"{directory}{album_name}/{url.rsplit('/', 1)[1]}"
    if not(os.path.exists(picture_path)):
      wget.download(url, picture_path, bar=None)
  except:
    # Value Error ?
    print(f"\nFailed to download picture: {url}")


if __name__ == "__main__":
  create_default_files()
  while True:
    print("Options:"
          "\n1 - Enter Album URL"
          "\n2 - Download from list.txt"
          "\n3 - Settings"
          "\n0 - Exit")
    option = str(input("> "))
    cls()

    if option == '1':
      album_url = input("0 - Back\nAlbum URL: ")
      if album_url != '0':
        cls()
        page_checker(album_url)
      else:
        cls()
        pass

    elif option == '2':
      print("Checking List...")
      with open('list.txt') as url_list:
        quantity = len(open('list.txt').readlines())
        print(f"Total of Links: {quantity} \n")
        for album_url in url_list:
          page_checker(album_url)

    elif option == '3':
      config_json_settings()

    elif option == '0':
      print("Xau ;-;")
      time.sleep(1)
      exit()
      break

    else:
      print("Invalid Option\n")
