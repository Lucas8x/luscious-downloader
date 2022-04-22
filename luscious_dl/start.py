import os
from argparse import Namespace
from pathlib import Path

from luscious_dl.album import Album, search_albums, print_search
from luscious_dl.command_line import command_line
from luscious_dl.downloader import Downloader
from luscious_dl.logger import logger
from luscious_dl.parser import extract_ids_from_list, extract_album_id, extract_user_id
from luscious_dl.user import User
from luscious_dl.utils import info, format_foldername, generate_pdf, inputs_string_to_list, delete_folder, generate_cbz


def albums_download(albums_ids: list[int], downloader: Downloader, output_dir: Path,
                    foldername_format='%t', gen_pdf=False, gen_cbz=False, rm_origin_dir=False) -> None:
  """
  Start albums download process.
  :param albums_ids: list of album ids
  :param downloader: Downloader object
  :param foldername_format: album folder name format
  :param output_dir: Path where albums will be saved
  :param gen_pdf: indicates whether to generate the pdf file
  :param gen_cbz: indicates whether to generate the cbz file
  :param rm_origin_dir: indicates whether the source folder will be deleted
  """
  for id_ in albums_ids:
    album = Album(id_)
    try:
      if album.fetch_info():
        formmatted_foldername = format_foldername(album, foldername_format)
        album_folder = Path.joinpath(output_dir, formmatted_foldername)
        album.show()
        album.fetch_pictures()
        # album.generate_metadata(album_folder)
        album.download(downloader, album_folder)
        if gen_pdf:
          generate_pdf(output_dir, formmatted_foldername, album_folder)
        if gen_cbz:
          generate_cbz(output_dir, formmatted_foldername, album_folder)
        if rm_origin_dir:
          delete_folder(album_folder, formmatted_foldername)
      else:
        raise Exception('Album Information not found.')
    except Exception as e:
      logger.critical(f'Album: {id_} Error: {e}')


def users_download(users_ids: list[int], downloader: Downloader, output_dir: Path, foldername_format='%t',
                   only_favorites=False, gen_pdf=False, gen_cbz=False, rm_origin_dir=False, group_by_user=False) -> \
        None:
  """
  Start users download process.
  :param users_ids: list of user ids
  :param downloader: Downloader object
  :param output_dir: Path where albums will be saved
  :param foldername_format: album folder name format
  :param only_favorites: defines if it's to download only the favorites
  :param gen_pdf: whether to generate the pdf file
  :param gen_cbz: whether to generate the cbz file
  :param rm_origin_dir: indicates whether the source folder will be deleted
  :param group_by_user:
  """
  for id_ in users_ids:
    user = User(id_)
    try:
      if user.fetch_info():
        user.fetch_albums(only_favorites)
        user.show()
        if group_by_user:
          output_dir = output_dir.joinpath(os.path.normcase(user.name))
        albums_download(user.albums_ids, downloader, output_dir, foldername_format, gen_pdf, gen_cbz, rm_origin_dir)
      else:
        raise Exception('User Information not found.')
    except Exception as e:
      logger.critical(f'User: {id_} Error: {e}')


def normalize_args(args: Namespace) -> Namespace:
  """
  Fix possible args inconsistencies.
  :param args: Namespace
  :return: Fixed Namespace
  """
  if args.threads <= 0:
    args.threads = os.cpu_count()
    if not args.threads:
      logger.warning('It was not possible to determine the number of CPUs in your system. '
                     'Only one will be used, this will decrease the amount of downloads.')
      args.threads = 1
  if args.page <= 0:
    args.page = 1
  if args.max_pages <= 0:
    args.max_pages = 1
  if args.page > args.max_pages:
    args.max_pages = args.page

  if args.only_favorites and not args.user_inputs:
    logger.warn(f"You're passing --favorites/-f flag without any user input.")
    args.only_favorites = False

  if args.gen_pdf and not args.album_inputs and not args.user_inputs and not args.search_download:
    logger.warn(f"You're passing --pdf flag without any album/user input or search download.")
    args.gen_pdf = False

  if args.gen_cbz and not args.album_inputs and not args.user_inputs and not args.search_download:
    logger.warn(f"You're passing --cbz flag without any album/user input or search download.")
    args.gen_cbz = False

  if args.rm_origin_dir and not args.gen_pdf and not args.gen_cbz:
    logger.warn(f"You're passing --rm-origin-dir flag without any pdf or cbz generation. This would delete the album "
                f"after download")
    args.rm_origin_dir = False

  args.keyword = args.keyword.strip() if args.keyword else None

  if args.album_inputs:
    inputs = inputs_string_to_list(args.album_inputs)
    args.albums_ids = extract_ids_from_list(inputs, extract_album_id)
  else:
    args.albums_ids = None

  if args.user_inputs:
    inputs = inputs_string_to_list(args.user_inputs)
    args.users_ids = extract_ids_from_list(inputs, extract_user_id)
  else:
    args.users_ids = None

  return args


def start(args: Namespace = None) -> None:
  """Start"""
  if not args:
    info()
  args = normalize_args(args or command_line())
  downloader = Downloader(args.threads, args.retries, args.timeout, args.delay)

  if args.albums_ids:
    albums_download(args.albums_ids, downloader, args.output_dir, args.foldername_format,
                    args.gen_pdf, args.gen_cbz, args.rm_origin_dir)
  elif args.users_ids:
    users_download(args.users_ids, downloader, args.output_dir, args.foldername_format,
                   args.only_favorites, args.gen_pdf, args.gen_cbz, args.rm_origin_dir, args.group_by_user)
  elif args.keyword:
    result = search_albums(args.keyword, args.sorting, args.page, args.max_pages)
    print_search(result)
    if args.search_download:
      for album in result:
        album.show()
        album.fetch_pictures()
        formmatted_foldername = format_foldername(album, args.foldername_format)
        album_folder = Path.joinpath(args.output_dir, formmatted_foldername)
        album.download(downloader, album_folder)
        if args.gen_pdf:
          generate_pdf(args.output_dir, formmatted_foldername, album_folder)


if __name__ == '__main__':
  start()
