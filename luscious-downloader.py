#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auto Download Luscious Pictures for you
pip install lxml p-tqdm requests selenium wget
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

# Check selected browser in config.json and Initialize Web Driver #
if not (os.path.exists('./config.json')): driver = "firefox"
else: driver = jsonVariables()[0]
if driver == "chrome":
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
elif driver == "firefox":
  options = Options()
  options.headless = True
  firefox_capabilities = DesiredCapabilities.FIREFOX
  firefox_capabilities['marionette'] = True
  driver = webdriver.Firefox(options=options, executable_path='./geckodriver.exe', capabilities=firefox_capabilities)

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
    print("1-Change Directory\n2-Login\n3-Switch Auto-Login\n4-Switch MultiProcess\n5-CPU Pool\n6-Switch Driver")
    escolhaJ = int(input(">"))
    if escolhaJ == 1:
      print("For default write 0")
      dir = str(input("Directory:"))
      if dir == "0":
        dir = './Albums/'
        data['dir'] = dir
    elif escolhaJ == 2:
      data['login'] = str(input("Login:"))
      data['password'] = str(input("Login:"))
    elif escolhaJ == 3:
      if data['doLogin']:
        data['doLogin'] = False
        print("Auto-Login Disabled")
      elif not data['doLogin']:
        data['doLogin'] = True
        print("Auto-Login Enabled")
    elif escolhaJ == 4:
      if data['multiprocess']:
        data['multiprocess'] = False
        print("MultiProcess Disabled")
      elif not data['multiprocess']:
        data['multiprocess'] = True
        print("MultiProcess Enabled")
    elif escolhaJ == 5:
      print("You have:", os.cpu_count(),"cpus. Recommend:", os.cpu_count()-1)
      print("Enter CPU Pool for Geting Direct Imgs Links")
      data['poolLinks'] = int(input("> "))
      print("Enter CPU Pool for Geting Direct Imgs Links")
      data['poolDown'] = int(input("> "))
    elif escolhaJ == 6:
      if data['driver'] == 'chrome':
        data['driver'] = 'firefox'
        print("Switched to Firefox/Geckodriver")
      elif data['driver'] == 'firefox':
        data['driver'] = 'chrome'
        print("Switched to ChromeDriver")

    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()

# Check if album is blocked and Log in if it is set#
def pageChecker(albumURL):
  driver.get(albumURL)
  html_source = driver.page_source
  tree = html.fromstring(html_source)
  check = tree.xpath('//*[@id="frontpage"]/h1/text()')
  check = str(*check)
  if check == "404 Not Found":
    doLogin = jsonVariables()[5]
    if doLogin:
      print("Auto-Login is enabled")
      login(albumURL, doLogin)
    else:
      print("Blocked Album:", albumURL, "\nTry turn on auto-login and write account info")
      listOrganizer(albumURL, 1)
  else:
    download(albumURL, False)

# Log in if it is set #
def login(albumURL, doLogin):
  if doLogin:
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
  download(albumURL, doLogin)

# Load Entire page / get links / download #
def download(albumURL, doLogin):
  if doLogin:
    driver.get(albumURL) #refresh

  html_source = driver.page_source
  tree = html.fromstring(html_source)

  # Album Information #
  albumName = tree.xpath('//*[@id="single_album_details"]/li[1]/h2/text()')
  uploader = tree.xpath('//*[@class="user_lnk"]/text()')
  pictures = tree.xpath('//*[@id="single_album_details"]/li[2]/div/p[1]/text()')
  print("Album Name:", str(*albumName))
  print("Uploader:", str(*uploader))
  print("Total of", str(*pictures))

  print("Loading entire page...")
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
  default = 'https://members.luscious.net/'

  # Combine default + imgPages for get Individual Img Page Link #
  imgPageLink = [default + x for x in imgPages]

  print("Total of",len(imgPageLink),"real links found")

  # Define Json Variables #
  dir = jsonVariables()[1]
  multiprocess = jsonVariables()[2]
  poolLinks = jsonVariables()[3]
  poolDowns = jsonVariables()[4]

  # Create Album Folder #
  albumName = re.sub('[^\w\-_\. ]', '_', str(*albumName))
  createFolder(dir+albumName+'/')

  # Acess imgPageLink and get direct link and download # Legacy Mode #
  if multiprocess == "legacy":
    print("Downloading with Legacy Mode...")
    time.sleep(1)
    for url in tqdm(imgPageLink, total=(len(imgPageLink))):
      downPicture(getDirectLink(url, doLogin), dir, albumName)

  # Get Direct Img Link #
  directImgLinks = []
  if multiprocess == False or doLogin == True:
    print("Getting Direct Imgs Links...")
    time.sleep(1)
    for url in tqdm(imgPageLink, total=(len(imgPageLink))):
      directImgLinks.append(getDirectLink(url, doLogin))

  elif multiprocess:
    print("Getting Direct Imgs Links with MultiProcess...")
    directImgLinks = (p_umap(getDirectLink, imgPageLink, doLogin, total=len(imgPageLink), num_cpus = poolLinks))

  # Download Pictures #
  if not multiprocess:
    print("Starting Download Pictures...")
    time.sleep(1)
    for url in tqdm(directImgLinks):
      downPicture(url, dir, albumName)

  elif multiprocess:
    print("Starting Download Pictures with MultiProcess...")
    p_umap(downPicture, directImgLinks, dir, albumName, total=len(directImgLinks), num_cpus = poolDowns)

  time.sleep(1)
  print("\nAlbum: ",albumName," Download Completed ",str(len(imgPageLink))," pictures has saved\nURL =",albumURL)
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
    print("Options:\n1-Enter URL\n2-From lista.txt\n3-Configs\n0-Sair")
    escolha = int(input(">"))

    if escolha == 1:
      pageChecker(albumURL = str(input("Album URL: ")))

    elif escolha == 2:
      print("Checking List...")
      with open('list.txt', 'r') as lista:
        qnt = len(open('list.txt').readlines())
        print("Number of links:",qnt)
        for url in lista:
          pageChecker(url)

    elif escolha == 3:
      configJsonSettings()

    elif escolha == 0:
      print("Xau ;-;")
      time.sleep(1)
      break

    else:
      print("Invalid Option")

driver.quit()