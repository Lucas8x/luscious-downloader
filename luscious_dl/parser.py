# -*- coding: utf-8 -*-
from typing import Optional, Union

from luscious_dl.logger import logger


def is_a_valid_id(id_) -> bool:
  try:
    if isinstance(int(id_), int):
      return True
  except ValueError:
    return False


def extract_album_id(album_url: str) -> Optional[int]:
  try:
    # logger.log(5, 'Resolving album url...')
    split = 2 if album_url.endswith('/') else 1
    album_id = album_url.rsplit('/', split)[1].rsplit('_', 1)[1]
    if is_a_valid_id(album_id):
      return int(album_id)
    else:
      raise Exception('ValueError')
  except Exception as e:
    # logger.critical(f"Couldn't resolve album ID of {album_url}\nError: {e}")
    return None


def extract_user_id(user_url: str) -> Optional[int]:
  try:
    # logger.log(5, 'Resolving user url...')
    split = 2 if user_url.endswith('/') else 1
    user_id = user_url.rsplit('/', split)[1]
    if is_a_valid_id(user_id):
      return int(user_id)
    else:
      raise Exception('ValueError')
  except Exception as e:
    # logger.critical(f"Couldn't resolve user ID of {user_url}\nError: {e}")
    return None


if __name__ == '__main__':
  print(extract_album_id('https://members.luscious.net/albums/light-yuri_275719/'))
  print(extract_album_id('https://members.luscious.net/albums/light-yuri_275719'))
  print(extract_user_id('https://members.luscious.net/users/668124/'))
  print(extract_user_id('https://members.luscious.net/users/668124'))
