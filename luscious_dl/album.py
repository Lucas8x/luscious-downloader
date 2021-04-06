from typing import Union

import requests
from tabulate import tabulate

from luscious_dl.downloader import Downloader
from luscious_dl.logger import logger
from luscious_dl.querys import album_info_query, album_list_pictures_query, album_search_query
from luscious_dl.utils import format_foldername


class Album:
  """Album class."""
  def __init__(self, id_: Union[str, int] = None, title: str = None, author: str = None, number_of_pictures: int = None,
               number_of_animated_pictures: int = None) -> None:
    self.id_ = id_
    self.title = title
    self.author = author
    self.number_of_pictures = number_of_pictures
    self.number_of_animated_pictures = number_of_animated_pictures
    self.pictures = []

  def show(self) -> None:
    """Show album information."""
    table = [
      ['ID ', self.id_],
      ['Title', self.title],
      ['Author', self.author],
      ['Pictures', self.number_of_pictures],
      ['Gifs', self.number_of_animated_pictures]
    ]
    logger.log(5, f'Album information:\n{tabulate(table, tablefmt="jira")}')

  def fetch_info(self) -> bool:
    """
    Fetch album information.
    :return: bool - true if there are no error otherwise false
    """
    logger.log(5, 'Fetching album information...')
    response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumGet',
                             json=album_info_query(str(self.id_))).json()
    data = response['data']['album']['get']
    if 'errors' in data:
      logger.error(f'Something wrong with album: {self.id_}\nErrors: {data["errors"]}')
      logger.warning('Skipping...')
      return False
    self.title = data['title']
    self.author = data['created_by']['display_name']
    self.number_of_pictures = data['number_of_pictures']
    self.number_of_animated_pictures = data['number_of_animated_pictures']
    return True

  def fetch_pictures(self) -> None:
    """Fetch album pictures."""
    logger.log(5, 'Fetching album pictures...')
    page = 1
    while True:
      response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumListOwnPictures',
                               json=album_list_pictures_query(str(self.id_), page)).json()
      self.pictures.extend([picture['url_to_original'] for picture in response['data']['picture']['list']['items']])
      page += 1
      if not response['data']['picture']['list']['info']['has_next_page']:
        break
    logger.info(f'Total of {len(self.pictures)} links found.')

  def download(self, downloader: Downloader, foldername_format: str = '%t') -> None:
    """
    Start album download.
    :param downloader: Downloder object
    :param foldername_format:
      %i = album id
      %t = album name
      %a = album author
      %p = album pictures
      %g = album gifs
    """
    logger.info(f'Starting album download: {self.title}')
    if downloader:
      folder_name = format_foldername(self.id_, self.title, self.author, self.number_of_pictures,
                                      self.number_of_animated_pictures, foldername_format)
      downloader.download(self.pictures, folder_name)
      logger.info(f'Album download completed: {self.title}')
    else:
      logger.critical(f'Downloader not set in album: {self.id_} | {self.title}')


def search_albums(search_query: str, sorting: str = 'date_trending', page: int = 1, max_pages: int = 1) -> list[Album]:
  """
  Search for albums.
  :param search_query: keyword
  :param sorting: sorting method
  :param page: initial search page
  :param max_pages: maximum search page
  :return: Album list
  """
  logger.log(5, f'Searching albums with keyword: {search_query} | Page: {page} | Max pages: {max_pages} | Sort: {sorting}')
  albums = []
  while True:
    response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumList',
                             json=album_search_query(search_query, sorting, page)).json()
    data = response['data']['album']['list']
    page += 1
    for item in data['items']:
      albums.append(Album(item['id'], item['title'], item['created_by']['display_name'],
                          item['number_of_pictures'], item['number_of_animated_pictures']))
    if not data['info']['has_next_page'] or data['info']['page'] == max_pages:
      break
  return albums


def print_search(results: list[Album]) -> None:
  """
  Shows information of the searched albums.
  :param results: Album list
  """
  table = [
    [album.id_,
     album.title,
     album.number_of_pictures,
     album.number_of_animated_pictures,
     album.author
     ] for album in results
  ]
  headers = ('ID', 'Title', 'Pictures', 'Gifs', 'Author')
  logger.log(5, f'Search Result Total: {len(results)}\n{tabulate(table, headers)}')
