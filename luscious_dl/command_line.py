import argparse
import os
from pathlib import Path


def command_line() -> argparse.Namespace:
  """
  Defines the command line interface.
  :return: arguments
  """
  parser = argparse.ArgumentParser(prog='Luscious Downloader', description='Download albums from luscious.net')

  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('--album', '-a', dest='album_inputs', action='store', help='download album by url or id')
  group.add_argument('--user', '-u', dest='user_inputs', action='store', help='download all user albums by url or id')
  group.add_argument('--search', '-s', dest='keyword', action='store', help='search albums by keyword')

  # user args
  parser.add_argument('--favorites', '-f', dest='only_favorites', action='store_true',
                      help='download only user favorites')
  parser.add_argument('--group', '--agroup', '-g', dest='group_by_user', action='store_true',
                      help='when downloading user albums they will be grouped by name')

  # search args
  parser.add_argument('--download', '-d', dest='search_download', action='store_true',
                      help='download albums from search results')
  parser.add_argument('--page', dest='page', action='store', type=int, default=1, help='page number of search results')
  parser.add_argument('--max-page', dest='max_pages', action='store', type=int, default=1,
                      help='max pages of search results')
  parser.add_argument('--sorting', dest='sorting', action='store', default='date_trending',
                      help='search sorting', choices=['date_trending', 'rating_all_time'])

  # generate options
  parser.add_argument('--pdf', '-p', dest='gen_pdf', action='store_true',
                      help='enable pdf file generation')
  parser.add_argument('--cbz', '-c', dest='gen_cbz', action='store_true',
                      help='enable cbz file generation')
  parser.add_argument('--rm-origin-dir', dest='rm_origin_dir', action='store_true',
                      help='remove downloaded album dir when generated PDF file.')

  # downloader args
  parser.add_argument('--output', '-o', dest='output_dir', action='store', default=Path.cwd(), help='output directory')
  parser.add_argument('--threads', '-t', dest='threads', action='store', type=int, default=os.cpu_count(),
                      help='how many download threads')
  parser.add_argument('--retries', '-R', dest='retries', action='store', type=int, default=5, help='download retries')
  parser.add_argument('--timeout', '-T', dest='timeout', action='store', type=int, default=30, help='download timeout')
  parser.add_argument('--delay', '-D', dest='delay', action='store', type=int, default=0,
                      help='delay between downloading multiple albums')
  parser.add_argument('--format', dest='foldername_format', action='store', default='%t',
                      help='format album folder name')

  args = parser.parse_args()
  return args


if __name__ == '__main__':
  command_line()
