from typing import Union, List, Set

from luscious_dl.logger import logger
from luscious_dl.downloader import Downloader
from luscious_dl.command_line import command_line
from luscious_dl.album import Album, search_albums, print_search
from luscious_dl.user import User


def albums_download(albums_ids: Union[List[int], Set[int]], downloader: Downloader) -> None:
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


def users_download(users_ids: Union[List[int], Set[int]], downloader: Downloader) -> None:
  for id_ in users_ids:
    user = User(id_)
    try:
      if user.fetch_info():
        user.fetch_albums()
        user.show()
        albums_ids = user.albums_ids
        albums_download(albums_ids, downloader)
      else:
        raise Exception('User Information not found.')
    except Exception as e:
      logger.critical(f'User: {id_} Error: {e}')


def start() -> None:
  args = command_line()

  downloader = Downloader(args.directory, args.threads, args.retries, args.timeout, args.delay)

  if args.albums_ids is not None:
    albums_download(args.albums_ids, downloader)
  elif args.users_ids is not None:
    users_download(args.users_ids, downloader)
  elif args.keyword is not None:
    result = search_albums(search_query=args.keyword, page=args.page, max_pages=args.max_pages)
    print_search(result)
    if args.search_download:
      for album in result:
        album.show()
        album.fetch_pictures()
        album.download(downloader)


if __name__ == '__main__':
  start()
