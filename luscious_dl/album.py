# -*- coding: utf-8 -*-
import requests
from tabulate import tabulate
from typing import Union

from luscious_dl.logger import logger
from luscious_dl.downloader import Downloader
from luscious_dl.querys import album_info_query, album_list_pictures_query


class Album:
  def __init__(self, id_: Union[str, int] = None):
    self.id_ = id_
    self.title = None
    self.author = None
    self.number_of_pictures = None
    self.number_of_animated_pictures = None
    self.pictures = None

  def show(self) -> None:
    table = [
      ['ID ', self.id_],
      ['Title', self.title],
      ['Author', self.author],
      ['Pictures', self.number_of_pictures],
      ['Gifs', self.number_of_animated_pictures]
    ]
    logger.log(5, f'Album information\n{tabulate(table, tablefmt="jira")}')

  def fetch_info(self) -> bool:
    logger.log(5, 'Fetching album information...')
    response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumGet',
                             json=album_info_query(str(self.id_))).json()
    data = response['data']['album']['get']
    if "errors" in data:
      logger.error(f'Something wrong with album: {self.id_}\nErrors: {data["errors"]}')
      logger.warning('Skipping...')
      return False
    self.title = data['title']
    self.author = data['created_by']['display_name']
    self.number_of_pictures = data['number_of_pictures']
    self.number_of_animated_pictures = data['number_of_animated_pictures']
    return True

  def fetch_pictures(self) -> None:
    logger.log(5, 'Fetching album pictures...')
    page = 1
    raw_data = []
    while True:
      response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumListOwnPictures',
                               json=album_list_pictures_query(str(self.id_), page)).json()
      raw_data.append(response['data']['picture']['list']['items'])
      page += 1
      if not response['data']['picture']['list']['info']['has_next_page']:
        break
    self.pictures = [picture['url_to_original'] for arr in raw_data for picture in arr]
    logger.info(f'Total of {len(self.pictures)} links found.')

  def download(self, downloader: Downloader) -> None:
    logger.info(f'Starting album download: {self.title}')
    if downloader:
      downloader.download(self.title, self.pictures)
    else:
      logger.critical(f'Downloader not set in album {self.id_}')
