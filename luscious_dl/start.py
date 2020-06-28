from typing import Union, List, Set

from luscious_dl.logger import logger
from luscious_dl.downloader import Downloader
from luscious_dl.command_line import command_line
from luscious_dl.album import Album
from luscious_dl.user import User


def album_download(albums_ids: Union[List, Set], downloader: Downloader):
  for id_ in albums_ids:
    album = Album(id_)
    try:
      if album.fetch_info():
        album.show()
        album.fetch_pictures()
        album.download(downloader)
      else:
        raise Exception('Information not found.')
    except Exception as e:
      logger.critical(f'Album: {id_} Error: {e}')


def user_download(users_ids: Union[List, Set], downloader: Downloader):
  for id_ in users_ids:
    user = User(id_)
    try:
      if user.fetch_info():
        user.fetch_albums()
        user.show()
        albums_ids = user.get_albums_ids()
        album_download(albums_ids, downloader)
    except Exception as e:
      logger.critical(f'User: {id_} Error: {e}')


def start():
  args = command_line()

  downloader = Downloader(args.directory, args.threads, args.retries, args.timeout, args.delay)

  if args.albums_ids is not None:
    album_download(args.albums_ids, downloader)
  elif args.users_ids is not None:
    user_download(args.users_ids, downloader)


if __name__ == '__main__':
  start()
