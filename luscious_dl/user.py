from typing import Union

import requests
from tabulate import tabulate

from luscious_dl.logger import logger
from luscious_dl.querys import user_info_query, user_albums_query, user_favorites_query


class User:
  """User class."""
  def __init__(self, id_: Union[str, int] = None) -> None:
    self.id_ = id_
    self.name = None
    self.number_of_albums = None
    self.number_of_favorites = None
    self.albums_ids = []

  def show(self) -> None:
    """Show user information."""
    table = [
      ['ID', self.id_],
      ['Name', self.name],
      ['Albums', self.number_of_albums],
      ['Favorites', self.number_of_favorites]
    ]
    logger.log(5, f'User information:\n{tabulate(table, tablefmt="jira")}')

  def fetch_info(self) -> bool:
    """
    Fetch user information.
    :return: bool - true if there are no error otherwise false
    """
    logger.log(5, 'Fetching user information...')
    response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=ProfileGet',
                             json=user_info_query(str(self.id_))).json()
    data = response['data']['userprofile']['get']
    if "errors" in data:
      logger.error(f'Something wrong with user: {self.id_}\nErrors: {data["errors"]}')
      logger.warning('Skipping...')
      return False
    self.name = data['user']['name']
    self.number_of_albums = data['number_of_albums']
    self.number_of_favorites = data['number_of_favorite_albums']
    return True

  def fetch_albums(self, only_favorites=False):
    """Fetch user albums."""
    logger.log(5, f'Fetching user {"favorites" if only_favorites else "albums"}...')
    n = 1
    while True:
      logger.info(f'Fetching user {"favorites" if only_favorites else "albums"} page: {n}...')
      json_query = user_favorites_query if only_favorites else user_albums_query
      response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumList',
                               json=json_query(str(self.id_), n)).json()
      self.albums_ids.extend([album['id'] for album in response['data']['album']['list']['items']])
      n += 1
      if not response['data']['album']['list']['info']['has_next_page']:
        break
    logger.info(f'Total of {len(self.albums_ids)} ids found.')
