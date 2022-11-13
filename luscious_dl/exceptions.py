class NoAlbumInformation(Exception):
  def __init__(self, id, message='') -> None:
    self.id = id
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    return f'No data from album: {self.id}'


class NoUserInformation(Exception):
  def __init__(self, id, message='') -> None:
    self.id = id
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    return f'No data from user: {self.id}'


class ReachedMaximunRetries(Exception):
  pass


class PictureZeroContent(Exception):
  pass


class InvalidID(Exception):
  pass


class InvalidInteger(Exception):
  pass


class NoValidPicturesForPDF(Exception):
  pass


class EmptyListTxtFile(Exception):
  pass