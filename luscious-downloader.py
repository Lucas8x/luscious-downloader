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

# Function to return values from config.json to others functions when called #
def jsonVariables():
  with open('config.json', 'r') as config:
    data = json.load(config)
    driver = data['driver']
    dir = data['dir']
    multiprocess = data['multiprocess']
    poolLinks = data['poolLinks']
    poolDowns = data['poolDown']
    doLogin = data['doLogin']
    username = data['username']
    password = data['password']
  config.close()
  return driver,dir,multiprocess,poolLinks,poolDowns,doLogin,username,password

# Create default files if not exist #
def defaultFiles():
  if not (os.path.exists('./config.json')):
    data = {
        "dir": "./Albums/",
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

# Create album folder #
def createFolder(directory):
  try:
    if not os.path.exists(directory):
      os.makedirs(directory)
      print("Album Folder Created:",directory)
  except OSError:
    print('Error: Creating directory. ' + directory)

# List Organizer #
def listOrganizer(albumURL, type):
  list = open("./list.txt", "r")
  tmp = []
  for line in list:
    if albumURL in line:
      line = line.replace(albumURL,'')
    tmp.append(line)
  list.close()
  list = open("./list.txt", "w")
  for line in tmp:
    list.write(line)
  list.close()

  # Put Blocked Album URL to Last Line #
  if type == 1:
    with open("./list_blocked.txt") as blocked:
      text = blocked.read()
    with open("./list_blocked.txt", 'a') as blocked:
      if not text.endswith("\n"):
        blocked.write('\n')
      blocked.write(albumURL)
    blocked.close()

  # Put Download Album URL to Last Line #
  elif type == 2:
    with open("./list_completed.txt") as completed:
      text = completed.read()
    with open("./list_completed.txt", 'a') as completed:
      if not text.endswith("\n"):
        completed.write('\n')
      completed.write(albumURL)
    completed.close()

# Change config.json settings #
def configJsonSettings():
  with open('config.json', 'r+') as j:
    data = json.load(j)
    while True:
      print("1 - Change Directory"
            "\n2 - Login"
            "\n3 - Switch Auto-Login [ Staus:",data['doLogin'],"]"
            "\n4 - Switch MultiProcess [ Status:",data['multiprocess'],"]"
            "\n5 - CPU Pool"
            "\n6 - Switch Driver [ Current:",data['driver'],"]"
            "\n0 - Back")
      optionToConfig = str(input(">"))
      cls()
      if optionToConfig == '1':
        print("For default write 0\nCurrent directory:", data['dir'])
        dir = str(input("Directory: "))
        if dir == "0" or " ":
          dir = './Albums/'
          data['dir'] = dir
      elif optionToConfig == '2':
        data['username'] = str(input("Username:"))
        data['password'] = str(input("Password:"))
      elif optionToConfig == '3':
        if data['doLogin']:
          data['doLogin'] = False
          print("Auto-Login Disabled")
        elif not data['doLogin']:
          data['doLogin'] = True
          print("Auto-Login Enabled")
      elif optionToConfig == '4':
        if data['multiprocess']:
          data['multiprocess'] = False
          print("MultiProcess Disabled")
        elif not data['multiprocess']:
          data['multiprocess'] = True
          print("MultiProcess Enabled")
      elif optionToConfig == '5':
        print("You have:", os.cpu_count(),"cpus. Recommend:", os.cpu_count()-1)
        print("Enter CPU Pool for Geting Direct Imgs Links")
        data['poolLinks'] = int(input("> "))
        print("Enter CPU Pool for Download Pictures")
        data['poolDown'] = int(input("> "))
      elif optionToConfig == '6':
        if data['driver'] == 'chrome':
          data['driver'] = 'firefox'
          print("Switched to Firefox/Geckodriver")
        elif data['driver'] == 'firefox':
          data['driver'] = 'chrome'
          print("Switched to ChromeDriver")
        print("Restart is necessary\n")
      elif optionToConfig == '0':
        cls()
        break
      else:
        print("Invalid Option\n")
    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()

# Check selected browser in config.json and Initialize Web Driver #
def mydriver():
  global driver
  mydriver = jsonVariables()[0]
  if mydriver == 'firefox':
    options = Options()
    options.headless = True
    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    driver = webdriver.Firefox(options=options, executable_path='./geckodriver.exe', capabilities=firefox_capabilities)
  elif mydriver == 'chrome':
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

# Check if album is blocked and Log in if it is set#
def pageChecker(albumURL):
  doLogin = jsonVariables()[5]
  if not doLogin:
    html_source = requests.get(albumURL).content
  else:
    driver = mydriver()
    time.sleep(1)
    driver.get(albumURL)
    html_source = driver.page_source

  tree = html.fromstring(html_source)
  check = tree.xpath('//*[@id="frontpage"]/h1/text()')
  check = str(*check)
  if check == "404 Not Found":
    if doLogin:
      print("Auto-Login is enabled")
      login(albumURL)
    else:
      print("Blocked Album:",albumURL,"\nTry turn on auto-login and write your account info")
      listOrganizer(albumURL, 1)
  else:
    download(albumURL, False, tree) #Call download with doLogin as False

# Log in if it is set #
def login(albumURL):
  if not (os.path.exists('./cookies.pkl')):
    print("Logging in...")
    driver.get('https://members.luscious.net/login/')
    username, password = jsonVariables()[6], jsonVariables()[7]
    driver.find_element_by_id('id_login').send_keys(username)
    driver.find_element_by_id('id_password').send_keys(password)
    driver.find_element_by_xpath("//input[@value='Sign In']").click()
    pickle.dump(driver.get_cookies(), open('./cookies.pkl', 'wb'))
  for cookie in pickle.load(open('./cookies.pkl', 'rb')):
    driver.add_cookie(cookie)
  driver.get(albumURL)
  tree = html.fromstring(driver.page_source)
  download(albumURL, True, tree)

# Load Entire page / get links / download #
def download(albumURL, doLogin, tree):
  # Album Information #
  albumName = tree.xpath('//*[@class="album_cover"]/h2/text()')
  uploader = tree.xpath('//*[@class="user_lnk"]/text()')
  pictures = tree.xpath('//*[@class="user_info"]/div/p[1]/text()')
  genre = tree.xpath('//*[@class="content_info"]/div/p/a/text()')
  print("Album Name:", str(*albumName))
  print("Genre:", str(*genre))
  print("Uploader:", str(*uploader))
  print("Total of", str(*pictures))

  # Define Json Variables #
  dir = jsonVariables()[1]
  multiprocess = jsonVariables()[2]
  poolLinks = jsonVariables()[3]
  poolDowns = jsonVariables()[4]

  print("Loading entire page...")
  #if multiprocess and not doLogin:
  if (multiprocess or not multiprocess) and not doLogin:
    n = 1;  data = []
    if len(data) > 0: data.clear()
    albumURL = re.sub('/albums/', '/pictures/album/', albumURL)
    while True:
      jsonPageRequest = requests.get(albumURL+'sorted/newest/page/'+str(n)+'/.json/').json()
      source = jsonPageRequest['html']
      tree = html.fromstring(source)
      data.append(tree.xpath('//*[@class="item thumbnail ic_container"]/a/@href'))
      n += 1
      if jsonPageRequest['paginator_complete'] == True:
        break
    flat = [x for sublist in data for x in sublist]
    imgPageLink = ['https://members.luscious.net' + x for x in flat]

  elif doLogin or multiprocess == "legacy":
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
    imgPages = tree.xpath('//*[@class="item thumbnail ic_container"]/a/@href') # List all photos on the page #
    imgPageLink = ['https://members.luscious.net/' + x for x in imgPages] # Combine site + imgPages for get Individual Img Page Link #

  print("Total of",len(imgPageLink),"real links found")

  # Create Album Folder #
  albumName = re.sub('[^\w\-_\. ]', '_', str(*albumName))
  createFolder(dir+albumName+'/')

  # Acess imgPageLink and get direct link and download # Legacy Mode #
  if multiprocess == "legacy":
    print("[Legacy] Downloading")
    time.sleep(1)
    for url in tqdm(imgPageLink, total=(len(imgPageLink))):
      downPicture(getDirectLink(url, doLogin), dir, albumName)

  # Get Direct Img Link #
  directImgLinks = []
  if not multiprocess or doLogin:
    print("Getting Direct Imgs Links...")
    for url in tqdm(imgPageLink, total=len(imgPageLink)):
      directImgLinks.append(getDirectLink(url, doLogin))

  elif multiprocess and not doLogin:
    print("[MultiProcess] Getting Direct Imgs Links")
    directImgLinks = (p_umap(getDirectLink, imgPageLink, doLogin, total=len(imgPageLink), num_cpus = poolLinks))

  # Download Pictures #
  if not multiprocess:
    print("Starting Download Pictures...")
    for url in tqdm(directImgLinks):
      downPicture(url, dir, albumName)

  elif multiprocess:
    print("[MultiProcess] Starting Download Pictures")
    p_umap(downPicture, directImgLinks, dir, albumName, total=len(directImgLinks), num_cpus = poolDowns)

  print("\nAlbum:",albumName,"Download Completed",len(imgPageLink),"pictures has saved\nURL:",albumURL)
  listOrganizer(albumURL,2) # Call organizeList function and put in list_completed #

# Get direct img link(.../img.png) #
def getDirectLink(url, doLogin):
  try:
    if not doLogin:
      return html.fromstring(requests.get(url).content).xpath('//*[@class="icon-download"]/@href')[0]
    elif doLogin:
      driver.get(url)
      return driver.find_element_by_class_name('icon-download').get_attribute('href')
  except: print("\nFailed to get link:",url)
  #except Exception as e: print("\n",e, url)

# Download Pictures from directImgLinks #
def downPicture(url,dir,albumName):
  try:
    if not((os.path.exists(dir+albumName+'/'+str(str(url).rsplit('/', 1)[1])))):
      wget.download(url,dir+albumName+'/'+str(str(url).rsplit('/', 1)[1]), bar=None)
  except: print("\nFailed to download:",url) # Value Error

# Main #
if __name__ == "__main__":
  defaultFiles()
  while True:
    print("Options:"
          "\n1 - Enter URL"
          "\n2 - From list.txt"
          "\n3 - Configs"
          "\n0 - Exit")
    option = str(input("> "))
    cls()

    if option == '1':
      albumURL = input("0 - Back\nAlbum URL: ")
      if albumURL == '0': cls(); pass
      else: cls(); pageChecker(albumURL)

    elif option == '2':
      print("Checking List...")
      with open('list.txt', 'r') as url_list:
        qnt = len(open('list.txt').readlines())
        print("Total of links:",qnt,"\n")
        for albumURL in url_list:
          pageChecker(albumURL)

    elif option == '3':
      configJsonSettings()

    elif option == '0':
      print("Xau ;-;")
      time.sleep(1)
      exit()
      break

    else:
      print("Invalid Option\n")
