#!/usr/bin/venv python
# -*- coding: utf-8 -*-
"""Auto Download Luscious Pictures for you
pip install lxml selenium tqdm urllib3 wget
"""
import locale
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
#from colorama import init
#init()
#from tqdm import tqdm
from p_tqdm import *
#from multiprocessing import Pool, Process, Manager, freeze_support, RLock, cpu_count
#freeze_support()
import json
locale.setlocale(locale.LC_ALL, '')

with open('config.json', 'r') as j:
  data = json.load(j)
  driver = data['driver']
  j.close()
  if(driver == "chrome"):
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

  elif(driver == "firefox"):
    options = Options()
    options.headless = True
    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    driver = webdriver.Firefox(options=options, executable_path='./geckodriver.exe', capabilities=firefox_capabilities)

def defaultFiles():
  if not (os.path.exists('./config.json')):
    data = {
        "dir": "./Albums/",
        "login": "",
        "password": "",
        "multiprocess": "true",
        "poolLinks": "3",
        "poolDown": "3",
        "driver": "chrome"
      }
    with open('./config.json', 'a+') as x:
      json.dump(data, x, indent=2)
  if not (os.path.exists('./list.xt')):
    open('./list.txt', 'a+')
  if not (os.path.exists('./list_completed.txt')):
    open('./list_completed.txt', 'a+')
  if not (os.path.exists('./list_blocked.xt')):
    open('./list_blocked.txt', 'a+')

def createFolder(directory):
  try:
    if not os.path.exists(directory):
      os.makedirs(directory)
      print("Album Folder Created:",directory)
  except OSError:
    print('Error: Creating directory. ' + directory)

def myJson():
  with open('config.json', 'r+') as j:
    data = json.load(j)
    print("1-Change Directory\n2-Login\n3-MultiProcess\n4-CPU Pool\n5-Switch Driver")
    escolhaJ = int(input(">"))
    if(escolhaJ == 1):
      print("For default write 0")
      dir = str(input("Directory:"))
      if(dir == '0'):
        dir = './Albums/'
        data['dir'] = dir
    elif(escolhaJ == 2):
      data['login'] = str(input("Login:"))
      data['password'] = str(input("Login:"))
    elif(escolhaJ == 3):
      if (data['multiprocess'] == 'true'):
        status = 'false'
        print("MultiProcess Disabled")
      elif (data['multiprocess'] == 'false'):
        status = 'true'
        print("MultiProcess Enabled")
      data['multiprocess'] = status
    elif(escolhaJ == 4):
      print("You have:", os.cpu_count(),"cpus")
      print("Enter CPU Pool for Geting Direct Imgs Links")
      data['poolLinks'] = str(input("> "))
      print("Enter CPU Pool for Geting Direct Imgs Links")
      data['poolDown'] = str(input("> "))
    elif(escolhaJ == 5):
      if (data['driver'] == 'chrome'):
        data['driver'] = 'firefox'
        print("Switched to Firefox/Geckodriver")
      elif (data['driver'] == 'firefox'):
        data['driver'] = 'chrome'
        print("Switched to ChromeDriver")

    j.seek(0)
    json.dump(data, j, indent=2)
    j.truncate()

def pageChecker(albumURL):
  driver.get(albumURL)
  html_source = driver.page_source
  tree = html.fromstring(html_source)
  check = tree.xpath('//*[@id="frontpage"]/h1/text()')
  check = str(*check)
  if(check == "404 Not Found"):
    print("Blocked Album:", albumURL)
    organizeList(albumURL,1)
  else:
    download(albumURL)

def organizeList(albumURL,type):
  x = open("./list.txt", "r")
  tmp = []
  for line in x:
    if albumURL in line:
      line = line.replace(albumURL,'')
    tmp.append(line)
  x.close()
  x = open("./list.txt", "w")
  for line in tmp:
    x.write(line)
  x.close()

  if(type == 1):
    with open("./list_completed.txt") as b:
      text = b.read()
    with open("./list_blocked.txt", 'a') as b:
      if not text.endswith("\n"):
        b.write('\n')
      b.write(albumURL)
    b.close()
  if(type == 2):
    with open("./list_completed.txt") as c:
      text = c.read()
    with open("./list_completed.txt", 'a') as c:
      if not text.endswith("\n"):
        c.write('\n')
      c.write(albumURL)
    c.close()

def download(albumURL):
  html_source = driver.page_source
  tree = html.fromstring(html_source)

  # Album Information
  albumName = tree.xpath('//*[@id="single_album_details"]/li[1]/h2/text()')
  uploader = tree.xpath('//*[@class="user_lnk"]/text()')
  pictures = tree.xpath('//*[@id="single_album_details"]/li[2]/div/p[1]/text()')

  #albumName = "".join(albumName)
  albumName = str(*albumName)
  print("Album Name:", albumName)
  print("Uploader:", str(*uploader))
  print("Total of", str(*pictures))

  print("Loading entire page...")
  last_height = driver.execute_script("return document.body.scrollHeight")
  while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    ActionChains(driver).send_keys(Keys.PAGE_UP).perform()
    time.sleep(5)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
      break
    last_height = new_height

  html_source = driver.page_source
  tree = html.fromstring(html_source)

  imgPages = tree.xpath('//*[@class="item thumbnail ic_container"]/a/@href') #lista de todas as fotos na página
  default = "https://members.luscious.net/"

  # Combine default + imgPages for get Individual Img Page Link
  #print("Combining Links...")
  for x in imgPages:
    imgPageLink = [default + x for x in imgPages]

  print("Total of",len(imgPageLink),"real links found")

  #Define Json Variables
  with open('config.json', 'r') as j:
    data = json.load(j)
    dir = data['dir']
    multiprocess = data['multiprocess']
    poolLinks =  int(data['poolLinks'])
    poolDowns = int(data['poolDown'])
    j.close()

  # Create Album Folder
  albumName = re.sub('[^\w\-_\. ]', '_', albumName)
  createFolder(dir+albumName+'/')

  time.sleep(1)

  # Acess imgPageLink > get direct link and download # Legacy Mode
  if(multiprocess == "legacy"):
    print("Downloading with Legacy Mode...")
    time.sleep(1)
    for url in tqdm(imgPageLink, total=(len(imgPageLink))):
      downPic(getLink(url), dir, albumName)

  #Get Direct Img Link
  directImgLinks = []
  time.sleep(1)
  if (multiprocess == "false"):
    print("Getting Direct Imgs Links...")
    for url in tqdm(imgPageLink, total=(len(imgPageLink))):
      directImgLinks.append(getLink(url))

  elif (multiprocess == "true"):
    print("Getting Direct Imgs Links with MultiProcess...")
    directImgLinks = (p_umap(getLink, imgPageLink, total=len(imgPageLink), num_cpus = poolLinks))

  time.sleep(1)

  # Download pictures
  time.sleep(1)
  if(multiprocess == "false"):
    print("Starting Download Pictures...")
    for url in tqdm(directImgLinks):
      downPic(url, dir, albumName)

  elif(multiprocess == "true"):
    print("\rStarting Download Pictures with MultiProcess...")
    #for _ in tqdm(pool.starmap(multiDown, zip(directImgLinks, repeat(dir),repeat(albumName))), total=len(directImgLinks)): pass
    p_umap(downPic, directImgLinks, dir, albumName, total=len(directImgLinks), num_cpus = poolDowns)

  time.sleep(1)
  print("\nAlbum: ",albumName," Download Completed ",str(len(imgPageLink))," pictures has saved\nURL =",albumURL)
  organizeList(albumURL,2)

  #if(escolha == 2):
    #if(baixados < qnt): print("Downloading Next Album...\n")
    #else: print("All albums downloaded")

def getLink(url):
  try:
    return html.fromstring(requests.get(url).content).xpath('//*[@class="icon-download"]/@href')[0]
  except: print("Failed to get link:",url)

def downPic(url,dir,albumName):
  try:
    if ((os.path.exists(dir+albumName+'/'+str(str(url).rsplit('/', 1)[1]))) == False):
      wget.download(url,dir+albumName+'/'+str(str(url).rsplit('/', 1)[1]), bar=None)
  except: print("Failed to download:",url) # Value Error

if __name__ == "__main__":
  defaultFiles()
  menu = True
  while menu == True:
    print("Options:\n1-Enter URL\n2-From lista.txt\n3-Configs\n0-Sair")
    escolha = int(input(">"))

    if (escolha == 1): pageChecker(albumURL = str(input('Album URL: ')))
    elif (escolha == 2):
      print("Checking List...")
      with open('list.txt', 'r') as lista:
        qnt = len(open('list.txt').readlines())
        print("Number of links:",qnt)
        for url in lista:
          pageChecker(url)

    elif (escolha == 3): myJson()

    elif(escolha == 0):
      menu = False
      print("Xau ;-;")
      time.sleep(1)

    else: print("Invalid Option")

driver.quit()