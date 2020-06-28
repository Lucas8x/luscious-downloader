# -*- coding: utf-8 -*-
import os
import re
import time
import requests
import multiprocessing as mp
from itertools import repeat
from typing import List

from luscious_dl.logger import logger
from luscious_dl.utils import create_folder


class Downloader:
  def __init__(self, output_dir: str, threads: int, retries: int = 5, timeout: int = 30, delay: int = 0):
    self.output_dir = output_dir
    self.threads = threads
    self.retries = retries
    self.timeout = timeout
    self.delay = delay

  def download_picture(self, picture_url: str, album_folder: str) -> None:
    try:
      if picture_url.startswith('//'):
        picture_url = picture_url.replace('//', '', 1)
      picture_name = picture_url.rsplit('/', 1)[1]
      picture_path = os.path.join(album_folder, picture_name)
      if not os.path.exists(picture_path):
        logger.info(f'Start downloading: {picture_url}')
        retry = 1
        res = requests.get(picture_url, stream=True, timeout=self.timeout)
        while res.status_code != 200 and retry <= self.retries:
          logger.warning(f'{retry}º Retry: {picture_name}')
          res = requests.get(picture_url, stream=True, timeout=self.timeout)
          retry += 1
        if len(res.content) > 0:
          with open(picture_path, 'wb') as image:
            image.write(res.content)
            logger.log(5, f'Completed download of: {picture_name}')
        else:
          raise Exception('Zero content')
      else:
        logger.warning(f'Picture already exists: {picture_name} ')
    except Exception as e:
      logger.error(f'Failed to download picture: {picture_url}\n{e}')

  def download(self, album_title: str, data: List) -> None:
    start_time = time.time()
    album_name = re.sub(r'[^\w\-_\. ]', '_', album_title)
    album_folder = os.path.join(self.output_dir, album_name)
    create_folder(album_folder)
    pool = mp.Pool(self.threads)
    pool.starmap(self.download_picture, zip(data, repeat(album_folder)))
    end_time = time.time()
    logger.info(f'Album download completed: {album_title}')
    logger.info(f'Finished in {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}')
    if self.delay:
      time.sleep(self.delay)
