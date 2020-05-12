# -*- coding: utf-8 -*-
import os
import re
import time
import requests
import multiprocessing as mp
from itertools import repeat

from luscious_dl.logger import logger
from luscious_dl.utils import get_config_setting, create_folder, list_organizer


def get_album_id(album_url):
  try:
    logger.log(5, 'Resolving album id...')
    split = 2 if album_url.endswith('/') else 1
    album_id = album_url.rsplit('/', split)[1].rsplit('_', 1)[1]
    if isinstance(int(album_id), int):
      return album_id
  except Exception as e:
    logger.critical(f"Couldn't resolve album ID of {album_url}\n{e}")
    return False


def get_album_info(album_id):
  logger.log(5, 'Fetching album information...')
  response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumGet', json={
    "id": 6,
    "operationName": "AlbumGet",
    "query": "query AlbumGet($id: ID!) {album {get(id: $id) {... on Album {...AlbumStandard} ... on MutationError "
             "{errors {code message}}}}} fragment AlbumStandard on Album {id title number_of_pictures}",
    "variables": {
      "id": album_id
    }
  }).json()
  return response['data']['album']['get']


def get_pictures_urls(album_id):
  logger.log(5, 'Fetching album pictures...')
  n = 1
  raw_data = []
  while True:
    response = requests.post('https://members.luscious.net/graphql/nobatch/?operationName=AlbumListOwnPictures', json={
      "id": 7,
      "operationName": "AlbumListOwnPictures",
      "query": "query AlbumListOwnPictures($input: PictureListInput!) {picture {list(input: $input) {info "
               "{...FacetCollectionInfo} items {...PictureStandardWithoutAlbum}}}} fragment FacetCollectionInfo on "
               "FacetCollectionInfo {page has_next_page has_previous_page total_items total_pages items_per_page "
               "url_complete} fragment PictureStandardWithoutAlbum on Picture {url_to_original url_to_video url}",
      "variables": {
        "input": {
          "filters": [
            {
              "name": "album_id",
              "value": album_id
            }
          ],
          "display": "rating_all_time",
          "page": n
        }
      }
    }).json()
    raw_data.append(response['data']['picture']['list']['items'])
    n += 1
    if not response['data']['picture']['list']['info']['has_next_page']:
      break
  data = [obj['url_to_original'] for arr in raw_data for obj in arr]
  logger.info(f'Total of {len(data)} links found.')
  return data


def show_album_info(album):
  try:
    logger.log(5, f'Album Name: {album["title"]} - with {album["number_of_pictures"]} pictures.')
  except Exception as e:
    logger.warning(f'Failed to print album information.\n{e}')


def download_picture(picture_url, directory, album_name):
  try:
    picture_name = picture_url.rsplit('/', 1)[1]
    picture_path = f'{directory}{album_name}/{picture_name}'
    if not(os.path.exists(picture_path)):
      logger.info(f'Start downloading: {picture_url}')
      retries = 1
      res = requests.get(picture_url, stream=True)
      while res.status_code != 200 and retries <= 5:
        logger.warning(f'{retries}º Retry: {picture_name}')
        res = requests.get(picture_url, stream=True)
        retries += 1
      if len(res.content) > 0:
        with open(picture_path, 'wb') as image:
          image.write(res.content)
          logger.log(5, f'Completed download of: {picture_name}')
      else:
        raise Exception('Zero content')
    else:
      logger.warning(f'Picture: {picture_name} already exist.')
  except Exception as e:
    logger.error(f'Failed to download picture: {picture_url}\n{e}')


def start(album_url):
  start_time = time.time()
  album_id = get_album_id(album_url)
  if not album_id:
    logger.warning(f'No album id. Skipping...')
    return

  album_info = get_album_info(album_id)
  show_album_info(album_info)

  directory = get_config_setting('directory')
  pool_size = get_config_setting('pool')
  picture_page_urls = get_pictures_urls(album_id)

  album_name = re.sub('[^\w\-_\. ]', '_', album_info['title'])
  create_folder(f'{directory}{album_name}/')
  logger.info('Starting download pictures.')

  pool = mp.Pool(pool_size)
  pool.starmap(download_picture, zip(picture_page_urls, repeat(directory), repeat(album_name)))

  end_time = time.time()
  logger.info(f'Album > {album_name} < Download completed {len(picture_page_urls)} pictures has saved.')
  logger.info(f'Finished download in {end_time-start_time:.2f}')
  list_organizer(album_url)
