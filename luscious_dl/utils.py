import json
import os
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from luscious_dl import __version__
from luscious_dl.logger import logger


def info() -> None:
  """Show package version."""
  logger.info(f'Luscious Downloader version: {__version__}')


def cls() -> None:
  """Clears the command prompt."""
  os.system('cls' if os.name == 'nt' else 'clear')


"""def format_filename(name: str) -> str:
  pass"""


def inputs_string_to_list(inputs_string: str) -> list[str]:
  """
  Convert a string with comma-separated items into a list of strings.
  :param inputs_string: a string with comma-separated items
  :return: list of strings
  """
  return [input_.strip() for input_ in inputs_string.split(',')]


def format_foldername(album, foldername_format: str = '%t') -> str:
  """
  Format album folder name.
  :param album: Album instance
  :param foldername_format:
    %i = album id
    %t = album name
    %a = album author
    %p = album pictures
    %g = album gifs
  :return: formatted folder name string
  """
  album_name = re.sub(r'[^\w\-_\. ]', '_', album.title)
  folder_name = foldername_format \
      .replace('%i', str(album.id_)) \
      .replace('%t', album_name) \
      .replace('%a', album.author) \
      .replace('%p', str(album.number_of_pictures)) \
      .replace('%g', str(album.number_of_animated_pictures)) \
      .replace('[]', '').strip()
  return folder_name


def create_folder(directory: Path) -> None:
  """
  Creates folder in the specified path.
  :param directory: folder path
  """
  try:
    if not Path.exists(directory):
      Path.mkdir(directory, parents=True, exist_ok=True)
      logger.info(f'Album folder created in: {directory}')
    else:
      logger.warn(f'Album folder already exist in: {directory}')
  except Exception as e:
    logger.error(f'Create folder: {e}')


def delete_folder(directory: Path, formmatted_name: str = '') -> None:
  shutil.rmtree(directory, ignore_errors=True)
  logger.log(5, f'Album {formmatted_name} folder deleted.')


def get_files_paths_in_folder(folder: Path):
  pictures_path_list = []
  for file_name in folder.iterdir():
    picture_path = Path.joinpath(folder, file_name)
    if picture_path.is_dir():
      continue
    pictures_path_list.append(picture_path)
  return pictures_path_list


def generate_pdf(output_dir: Path, formmatted_name: str, album_folder: Path) -> None:
  """
  Create pdf file containing album pictures [jpg,jpeg,png].
  :param output_dir: output folder path
  :param formmatted_name: formmatted album name
  :param album_folder: album folder path
  """
  valid_extensions = ('.jpg', '.jpeg', '.png')
  try:
    from PIL import Image
    logger.info('Generating album pdf file...')

    pictures_path_list = get_files_paths_in_folder(album_folder)
    pictures_path_list = list(filter(lambda file: file.suffix.lower() in valid_extensions, pictures_path_list))

    pictures = []
    if len(pictures_path_list) > 0:
      for picture_path in pictures_path_list:
        img = Image.open(picture_path)
        if picture_path.suffix.lower() == '.png' or img.mode == 'RGBA':
          img = img.convert('RGB')
        pictures.append(img)

    if len(pictures) == 0:
      raise Exception('Pictures list is empty, probably has no valid images [jpg, jpeg, png]')

    pdf_filename = f'{formmatted_name}.pdf'
    pdf_path = Path.joinpath(output_dir, pdf_filename)

    logger.info(f'Adding {len(pictures)} pictures to pdf...')

    pictures[0].save(pdf_path, save_all=True, append_images=pictures[1:])
    logger.log(5, f'Album PDF saved to: {output_dir}')

    for img in pictures:
      img.close()

  except ImportError:
    logger.error('Please install Pillow package by using pip.')
  except Exception as e:
    logger.error(f'Failed to generate album pdf: {e}')


def generate_cbz(output_dir: Path, formmatted_name: str, album_folder: Path):
  logger.info('Generating album CBZ file...')
  try:
    cbz_filename = f'{formmatted_name}.cbz'
    cbz_path = Path.joinpath(output_dir, cbz_filename)

    with ZipFile(cbz_path, 'w') as cbz_file:
      for file in album_folder.rglob('*'):
        cbz_file.write(file, file.name)

    logger.log(5, f'Album CBZ saved to: {output_dir}')

  except Exception as e:
    logger.error(f'Failed to generate CBZ file: {e}')


# \/ Menu only functions \/ #

def get_root_path() -> Path:
  """
  Return project root path.
  :return: PurePath subclass
  """
  return Path(__file__).parent.parent


def get_config_data() -> dict:
  """
  Load and return config.json data.
  :return: dictionary
  """
  try:
    with get_root_path().joinpath('config.json').open() as config:
      data = json.load(config)
      return data
  except Exception as e:
    logger.warning(f'Something went wrong loading config file: {e}')
    return {}


def read_list() -> list[str]:
  """
  Read list.txt file content.
  :return: list.txt content
  """
  try:
    logger.log(5, 'Reading list...')
    with get_root_path().joinpath('list.txt').open() as list_file:
      list_txt = list_file.read()
      if len(list_txt) > 0:
        list_txt = list_txt.split('\n')
      logger.log(5, f'Total of Items: {len(list_txt)}.')
    return list_txt
  except Exception as e:
    print(f'Failed to read the list.txt.\n{e}')


def create_default_files() -> None:
  """Create the initial files when using the menu."""
  root = get_root_path()
  if not Path.exists(root.joinpath('config.json')):
    data = {
      "directory": "./albums/",
      "pool": os.cpu_count() or 1,
      "retries": 5,
      "timeout": 30,
      "delay": 0,
      "foldername_format": "%t",
      "gen_pdf": False,
      "gen_cbz": False,
      "rm_origin_dir": False,
      "group_by_user": False,
    }
    with root.joinpath('config.json').open('a+') as config_file:
      json.dump(data, config_file, indent=2)
  if not Path.exists(root.joinpath('list.txt')):
    root.joinpath('list.txt').touch()
  if not Path.exists(root.joinpath('list_completed.txt')):
    root.joinpath('list_completed.txt').touch()


class ListFilesManager:
  """Class to manage url list files."""
  @staticmethod
  def add(string: str) -> None:
    """
    Add string to list_completed.txt
    :param string: Mostly URL or ID of Album or User
    """
    path = get_root_path().joinpath('list_completed.txt')
    with path.open() as completed:
      text = completed.read()
    with path.open('a') as completed:
      if not text.endswith('\n'):
        completed.write('\n')
      completed.write(string)
      logger.log(5, f'Added to completed list: {string}')

  @staticmethod
  def remove(string: str) -> None:
    """
    Remove string from list.txt
    :param string: Mostly URL or ID of Album or User
    """
    path = get_root_path().joinpath('list.txt')
    with path.open() as list_txt:
      temp = ['' if string in line else line for line in list_txt]
    with path.open('w') as list_txt:
      for line in temp:
        list_txt.write(line)


def open_config_menu() -> None:
  """Open settings/config menu"""
  options = {
    '2': {'key': 'pool', 'msg': 'Enter CPU Pool for download pictures.\n> '},
    '3': {'key': 'retries', 'msg': 'Enter CPU Pool for download pictures.\n> '},
    '4': {'key': 'timeout', 'msg': 'Enter picture timeout.\n> '},
    '5': {'key': 'delay', 'msg': 'Enter album download delay.\n> '},
    '7': {'key': 'gen_pdf', 'switch': True},
    '8': {'key': 'gen_cbz', 'switch': True},
    '9': {'key': 'rm_origin_dir', 'switch': True},
    '10': {'key': 'group_by_user', 'switch': True}
  }
  common_options = [str(x) for x in range(2, 11)]
  common_options.remove('6')

  with get_root_path().joinpath('config.json').open('r+') as json_file:
    data = json.load(json_file)
    while True:
      config_menu = input(f'1 - Change Directory [Current: {data.get("directory")}]\n'
                          f'2 - CPU Pool [Current: {data.get("pool")}]\n'
                          f'3 - Picture Retries [Current: {data.get("retries")}]\n'
                          f'4 - Picture Timeout [Current: {data.get("timeout")}]\n'
                          f'5 - Download Delay [Current: {data.get("delay")}]\n'
                          f'6 - Format output album folder name [Current: {data.get("foldername_format")}]\n'
                          f'7 - Generate PDF [Current: {data.get("gen_pdf")}]\n'
                          f'8 - Generate CBZ [Current: {data.get("gen_cbz")}]\n'
                          f'9 - Remove origin directory [Current: {data.get("rm_origin_dir")}]\n'
                          f'10 - Group Albums by Uploader name [Current: {data.get("group_by_user")}]\n'
                          '0 - Back.\n'
                          '> ')
      cls()

      if config_menu == '1':
        new_path = input(f'Current directory: {data.get("directory")}\n'
                         '1 - Restore default directory\n'
                         '0 - Back\n'
                         'Directory: ')
        if new_path not in ['0', '1', ' ']:
          data['directory'] = os.path.normcase(new_path)
        elif new_path == '1':
          data['directory'] = './Albums/'

      elif config_menu in common_options:
        if config_menu == '2':
          print(f'You have: {os.cpu_count()} cores.')
        opt = options[config_menu]
        key = opt.get('key')
        data[key] = not data.get(key) if opt.get('switch') else int(input(opt.get('msg')))

      elif config_menu == '6':
        print(
          'Supported album folder formatter:',
          '%i = Album ID',
          '%t = Album name/title',
          '%a = Album authors name',
          '%p = Album total pictures',
          '%g = Album total gifs',
          sep='\n'
        )
        new_folderformat = input('\nEnter album folder format.\n> ')
        if not any(identifier in new_folderformat for identifier in ('%i', '%t', '%a')):
          if input('\nNo album identifiers found.\nYou sure? ("Y/N")\n> ') in 'nN':
            print('\nAlbum folder format set to the default.\n')
            new_folderformat = '%t'
        data['foldername_format'] = new_folderformat

      elif config_menu == '0':
        cls()
        break

      else:
        print('Invalid Option.\n')

      json_file.seek(0)
      json.dump(data, json_file, indent=2)
      json_file.truncate()
