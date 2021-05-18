import json
from pathlib import Path
from typing import Union

import requests
from tabulate import tabulate

from luscious_dl.downloader import Downloader
from luscious_dl.logger import logger
from luscious_dl.querys import album_info_query, album_list_pictures_query, album_search_query


class Album:
  """Album class."""
  def __init__(self, id_: Union[str, int] = None, title: str = None, author: str = None, number_of_pictures: int = None,
               number_of_animated_pictures: int = None) -> None:
    self.id_ = id_
    self.title = title
    self.author = author
    self.number_of_pictures = number_of_pictures
    self.number_of_animated_pictures = number_of_animated_pictures
    self.info = {}
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
    self.info.update({
      'slug': data.get('slug', self.title),
      'language': data.get('language', {}).get('title', ''),
      'tags':  [tag.get('text', '') for tag in data.get('tags', {})],
      'genres':  [genre.get('title', '') for genre in data.get('genres', {})],
      'audiences':  [audience.get('title', '') for audience in data.get('audiences', {})],
    })
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

  def download(self, downloader: Downloader, album_folder: Path) -> None:
    """
    Start album download.
    :param downloader: Downloader object
    :param album_folder: album folder
    """
    logger.info(f'Starting album download: {self.title}')
    if downloader:
      downloader.download(self.pictures, album_folder)
      logger.info(f'Album download completed: {self.title}')
    else:
      logger.critical(f'Downloader not set in album: {self.id_} | {self.title}')

  def generate_metadata(self, album_dir: Path) -> None:
    """
    Create album metadata.json.
    :param album_dir: album folder path
    """
    metadata = {
      'id': self.id_,
      'title': self.title,
      'slug': self.info.get('slug', ''),
      'author': self.author,
      'pictures': self.number_of_pictures,
      'gifs': self.number_of_animated_pictures,
      'language': self.info.get('language', ''),
      'tags': self.info.get('tags', ''),
      'genres': self.info.get('genres', ''),
      'audiences': self.info.get('audiences', '')
    }
    with Path.joinpath(album_dir, 'metadata.json').open('w') as metadata_file:
      json.dump(metadata, metadata_file, indent=2)


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
