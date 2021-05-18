import multiprocessing as mp
import time
from itertools import repeat
from pathlib import Path

import requests

from luscious_dl.logger import logger
from luscious_dl.utils import create_folder


def normalize_url(picture_url: str) -> str:
  """
  Fix possible errors in the picture url.
  :param picture_url: picture url
  :return: fixed url
  """
  if picture_url.startswith('//'):
    picture_url = picture_url.replace('//', '', 1)
  if not picture_url.startswith('http://') and not picture_url.startswith('https://'):
    picture_url = f'https://{picture_url}'
  # picture_url = picture_url.replace('cdnio.', 'w315.')
  return picture_url


class Downloader:
  """Downloader class."""
  def __init__(self, threads: int = 1, retries: int = 5, timeout: int = 30, delay: int = 0) -> None:
    self.threads = threads
    self.retries = retries
    self.timeout = timeout
    self.delay = delay

  def download_picture(self, picture_url: str, album_folder: Path) -> None:
    """
    Download picture.
    :param picture_url: picture url
    :param album_folder: album folder path
    """
    try:
      picture_url = normalize_url(picture_url)
      picture_name = picture_url.rsplit('/', 1)[1]
      picture_path = Path.joinpath(album_folder, picture_name)
      if not Path.exists(picture_path):
        logger.info(f'Start downloading: {picture_url}')
        retry = 1
        response = requests.get(picture_url, stream=True, timeout=self.timeout)
        while response.status_code != 200 and retry <= self.retries:
          logger.warning(f'{retry}º Retry: {picture_name}')
          response = requests.get(picture_url, stream=True, timeout=self.timeout)
          retry += 1
        if retry > self.retries:
          raise Exception('Reached maximum number of retries')
        if len(response.content) > 0:
          with picture_path.open('wb') as image:
            image.write(response.content)
            logger.log(5, f'Completed download of: {picture_name}')
        else:
          raise Exception('Zero content')
      else:
        logger.warning(f'Picture already exists: {picture_name} ')
    except Exception as e:
      logger.error(f'Failed to download picture: {picture_url}\n{e}')

  def download(self, urls: list[str], album_folder: Path) -> None:
    """
    Start download process.
    :param urls: list of image URLs
    :param album_folder: album folder
    """
    start_time = time.time()

    create_folder(album_folder)

    pool = mp.Pool(self.threads)
    pool.starmap(self.download_picture, zip(urls, repeat(album_folder)))

    end_time = time.time()
    logger.info(f'Finished in {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}')

    if self.delay:
      time.sleep(self.delay)
