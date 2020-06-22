# -*- coding: utf-8 -*-
import argparse
import os

from luscious_dl.downloader import start


def command_line() -> None:
  parser = argparse.ArgumentParser(
    prog='Luscious Downloader',
    description='Download albums',
    add_help=True,
  )

  parser.add_argument('--download', '-d', dest='url_or_id',
                      action='store', required=True,
                      help='enter album url or id')

  # download args
  parser.add_argument('--output', '-o', dest='directory',
                      action='store',
                      default=os.getcwd(),
                      help='output directory')

  parser.add_argument('--threads', '-t', dest='threads',
                      action='store', type=int,
                      default=os.cpu_count(),
                      help='how many download threads')

  parser.add_argument('--retries', '-R', dest='retries',
                      action='store', type=int,
                      default=5,
                      help='download retries')

  parser.add_argument('--timeout', '-T', dest='timeout',
                      action='store', type=int,
                      default=30,
                      help='download timeout')

  parser.add_argument('--delay', '-D', dest='delay',
                      action='store', type=int,
                      default=0,
                      help='delay between downloading multiple albums')

  args = parser.parse_args()

  if args.url_or_id:
    inputs = args.url_or_id.split(',')

    for x in inputs:
      start(x, args.directory, args.threads, args.retries, args.timeout, args.delay)

  else:
    print('Please provide album url or id\n')
    exit()


if __name__ == '__main__':
  command_line()

