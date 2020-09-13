from typing import Union, List

from luscious_dl.logger import logger
from luscious_dl.downloader import Downloader
from luscious_dl.command_line import command_line
from luscious_dl.album import Album, search_albums, print_search
from luscious_dl.user import User
from luscious_dl.utils import info


def albums_download(albums_ids: List[int], downloader: Downloader) -> None:
  """
  Start albums download process.
  :param albums_ids: list of album ids
  :param downloader: Downloder object
  """
  for id_ in albums_ids:
    album = Album(id_)
    try:
      if album.fetch_info():
        album.show()
        album.fetch_pictures()
        album.download(downloader)
      else:
        raise Exception('Album Information not found.')
    except Exception as e:
      logger.critical(f'Album: {id_} Error: {e}')


def users_download(users_ids: List[int], downloader: Downloader) -> None:
  """
  Start users download process.
  :param users_ids: list of user ids
  :param downloader: Downloder object
  """
  for id_ in users_ids:
    user = User(id_)
    try:
      if user.fetch_info():
        user.fetch_albums()
        user.show()
        albums_download(user.albums_ids, downloader)
      else:
        raise Exception('User Information not found.')
    except Exception as e:
      logger.critical(f'User: {id_} Error: {e}')


def start() -> None:
  """Start"""
  info()
  args = command_line()
  downloader = Downloader(args.directory, args.threads, args.retries, args.timeout, args.delay)

  if args.albums_ids:
    albums_download(args.albums_ids, downloader)
  elif args.users_ids:
    users_download(args.users_ids, downloader)
  elif args.keyword:
    result = search_albums(search_query=args.keyword, page=args.page, max_pages=args.max_pages)
    print_search(result)
    if args.search_download:
      for album in result:
        album.show()
        album.fetch_pictures()
        album.download(downloader)


if __name__ == '__main__':
  start()
