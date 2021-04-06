import os
from argparse import Namespace

from luscious_dl.album import Album, search_albums, print_search
from luscious_dl.command_line import command_line
from luscious_dl.downloader import Downloader
from luscious_dl.logger import logger
from luscious_dl.parser import extract_ids_from_list, extract_album_id, extract_user_id
from luscious_dl.user import User
from luscious_dl.utils import info


def albums_download(albums_ids: list[int], downloader: Downloader, foldername_format='%t') -> None:
  """
  Start albums download process.
  :param albums_ids: list of album ids
  :param downloader: Downloder object
  :param foldername_format: album folder name format
  """
  for id_ in albums_ids:
    album = Album(id_)
    try:
      if album.fetch_info():
        album.show()
        album.fetch_pictures()
        album.download(downloader, foldername_format)
      else:
        raise Exception('Album Information not found.')
    except Exception as e:
      logger.critical(f'Album: {id_} Error: {e}')


def users_download(users_ids: list[int], downloader: Downloader, foldername_format='%t') -> None:
  """
  Start users download process.
  :param users_ids: list of user ids
  :param downloader: Downloder object
  :param foldername_format: album folder name format
  """
  for id_ in users_ids:
    user = User(id_)
    try:
      if user.fetch_info():
        user.fetch_albums()
        user.show()
        albums_download(user.albums_ids, downloader, foldername_format)
      else:
        raise Exception('User Information not found.')
    except Exception as e:
      logger.critical(f'User: {id_} Error: {e}')


def normalize_args(args: Namespace) -> Namespace:
  if args.threads <= 0:
    args.threads = os.cpu_count()
    if not args.threads:
      args.threads = 1
  if args.page <= 0:
    args.page = 1
  if args.max_pages <= 0:
    args.max_pages = 1
  if args.page > args.max_pages:
    args.max_pages = args.page

  args.keyword = args.keyword.strip() if args.keyword else None

  if args.album_inputs:
    inputs = [input_.strip() for input_ in args.album_inputs.split(',')]
    args.albums_ids = extract_ids_from_list(inputs, extract_album_id)
  else:
    args.albums_ids = None

  if args.user_inputs:
    inputs = [input_.strip() for input_ in args.user_inputs.split(',')]
    args.users_ids = extract_ids_from_list(inputs, extract_user_id)
  else:
    args.users_ids = None

  return args


def start(args: Namespace = None) -> None:
  """Start"""
  if not args:
    info()
  args = normalize_args(args or command_line())
  downloader = Downloader(args.directory, args.threads, args.retries, args.timeout, args.delay)

  if args.albums_ids:
    albums_download(args.albums_ids, downloader, args.foldername_format)
  elif args.users_ids:
    users_download(args.users_ids, downloader, args.foldername_format)
  elif args.keyword:
    result = search_albums(args.keyword, args.sorting, args.page, args.max_pages)
    print_search(result)
    if args.search_download:
      for album in result:
        album.show()
        album.fetch_pictures()
        album.download(downloader)


if __name__ == '__main__':
  start()
