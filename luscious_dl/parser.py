from typing import Optional, Union, Callable
from luscious_dl.exceptions import InvalidID

from luscious_dl.logger import logger


def is_a_valid_integer(x: Union[str, int]) -> bool:
  """
  Check if it's a valid integer.
  :param x: id in string or int format
  :return: bool
  """
  try:
    return isinstance(int(x), int)
  except (ValueError, TypeError):
    return False


def extract_album_id(album_url: str) -> Optional[int]:
  """
  Extract id from album url.
  :param album_url: album url
  :return: album id
  """
  try:
    split = 2 if album_url.endswith('/') else 1
    album_id = album_url.rsplit('/', split)[1].rsplit('_', 1)[1]
    if not is_a_valid_integer(album_id):
      raise InvalidID
    return int(album_id)
  except InvalidID:
    logger.critical(f"Couldn't resolve album ID of {album_url}\nError: {e}")
  except Exception as e:
    logger.critical(f"Couldn't resolve album ID of {album_url}\nError: {e}")


def extract_user_id(user_url: str) -> Optional[int]:
  """
  Extract id from user url.
  :param user_url: user url
  :return: user id
  """
  try:
    split = 2 if user_url.endswith('/') else 1
    user_id = user_url.rsplit('/', split)[1]
    if not is_a_valid_integer(user_id):
      raise InvalidID
    return int(user_id)
  except InvalidID:
    logger.critical(f"Couldn't resolve user ID of {user_url}\nError: {e}")
  except Exception as e:
    logger.critical(f"Couldn't resolve user ID of {user_url}\nError: {e}")


def extract_ids_from_list(iterable: list[Union[str, int]], extractor: Callable[[str], Optional[int]]) -> list[int]:
  """
  Extract ids from list containing urls/ids.
  :param iterable: list containing urls/ids
  :param extractor: extraction function
  :return: A list containing the ids
  """
  return list(
      filter(
          None, {
              int(item) if is_a_valid_integer(item) else extractor(item)
              for item in iterable
          }))
