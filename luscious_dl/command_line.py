# -*- coding: utf-8 -*-
import argparse
import os
from typing import Any

from luscious_dl.parser import extract_album_id, extract_user_id, is_a_valid_id


def command_line() -> Any:
  parser = argparse.ArgumentParser(prog='Luscious Downloader', description='Download albums')

  group = parser.add_mutually_exclusive_group(required=True)

  group.add_argument('--album', '-a', dest='album_inputs', action='store', help='download album by url or id')

  group.add_argument('--user', '-u', dest='user_inputs', action='store', help='download all user albums by url or id')

  group.add_argument('--search', '-s', dest='keyword', action='store', help='search albums by keyword')

  # search args
  parser.add_argument('--download', '-d', dest='search_download', action='store_true',
                      help='download albums from search results')

  parser.add_argument('--page', dest='page', action='store', type=int, default=1, help='page numebr of search results')

  parser.add_argument('--max-page', dest='max_pages', action='store', type=int, default=1,
                      help='max pages of search results')

  '''parser.add_argument('--sorting', dest='sorting', action='store', default='date_trending',
                      help='search sorting', choices=['date_trending', 'search_score', 'rating_all_time'])'''

  # download args
  parser.add_argument('--output', '-o', dest='directory', action='store', default=os.getcwd(), help='output directory')

  parser.add_argument('--threads', '-t', dest='threads', action='store', type=int, default=os.cpu_count(),
                      help='how many download threads')

  parser.add_argument('--retries', '-R', dest='retries', action='store', type=int, default=5, help='download retries')

  parser.add_argument('--timeout', '-T', dest='timeout', action='store', type=int, default=30, help='download timeout')

  parser.add_argument('--delay', '-D', dest='delay', action='store', type=int, default=0,
                      help='delay between downloading multiple albums')

  args = parser.parse_args()

  if args.threads <= 0:
    args.threads = os.cpu_count()

  if args.page <= 0:
    args.page = 1
  if args.max_pages <= 0:
    args.max_pages = 1
  if args.page > args.max_pages:
    args.max_pages = args.page

  if args.keyword:
    args.keyword = args.keyword.strip()
  else:
    args.keyword = None

  if args.album_inputs:
    inputs = [id_.strip() for id_ in args.album_inputs.split(',')]
    args.albums_ids = set(int(input_) if is_a_valid_id(input_) else extract_album_id(input_) for input_ in inputs)
  else:
    args.albums_ids = None

  if args.user_inputs:
    inputs = [id_.strip() for id_ in args.user_inputs.split(',')]
    args.users_ids = set(int(input_) if is_a_valid_id(input_) else extract_user_id(input_) for input_ in inputs)
  else:
    args.users_ids = None

  return args


if __name__ == '__main__':
  command_line()
