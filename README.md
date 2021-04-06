# Luscious Downloader

CLI tool for downloading albums from [Luscious](https://luscious.net)

![Downloads](https://img.shields.io/pypi/dm/luscious-downloader?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/luscious-downloader?style=flat-square)
![License](https://img.shields.io/github/license/lucas8x/luscious-downloader?style=flat-square)

## Manual Installation

_If you have python and git installed._

```bash
git clone https://github.com/Lucas8x/luscious-downloader.git
cd luscious-downloader
python setup.py install
```

## Installation (pip)

```bash
pip install luscious-downloader
```

## Installation #2 (Windows Only)

_If you don't have python or git installed._

1. [Download](https://github.com/Lucas8x/luscious-downloader/archive/main.zip).
2. Extract.
3. Run `run.bat`.
4. Wait install.
5. [Menu](#Menu)

## Usage

**NOTE:** The default download folder will be the path where you are executing the command.\
**NOTE²:** You can enter multiple url and ids separated by commas.

Download albums:

```bash
lsd -a https://members.luscious.net/albums/light-yuri_275719/
lsd -a 275719,292887
```

Download all user's albums:

```bash
lsd -u https://members.luscious.net/users/668124/
lsd -u 668124,274991
```

Download search albums:

```bash
lsd -s yuri -d
lsd -s yuri -d --page 2 --max-page 5
```

Download top albums:

```bash
lsd -s yuri -d --sorting rating_all_time
```

Format output album folder name:

```bash
lsd -a 275719 --format [%i][%t]
#Output: [275719][Light Yuri]
```

Supported album folder formatter:

- %i = Album ID
- %t = Album name/title
- %a = Album authors' name
- %p = Album total pictures
- %g = Album total gifs

CLI options:

```
Options:
    -h, --help              show help message
  # Download
    -a ALBUM_INPUTS, --album ALBUM_INPUTS
                            download album by url or id
    -u USER_INPUTS,  --user USER_INPUTS
                            download all user albums by url or id
    -s KEYWORD,      --search KEYWORD
                            search albums by keyword
  # Search Options
    --download, -d          download albums from search results
    --page PAGE             page number of search results
    --max-page MAX_PAGES    max pages of search results
    --sorting {date_trending,rating_all_time}
                            sorting of search albums

  # Download Options
    --output DIRECTORY, -o DIRECTORY
                            output directory
    --threads THREADS, -t THREADS
                            how many download threads
    --retries RETRIES, -R RETRIES
                            download retries
    --timeout TIMEOUT, -T TIMEOUT
                            download timeout
    --delay DELAY, -D DELAY
                            delay between downloading multiple albums
    --format FORMAT
                            format output album folder name
```

## Menu

1. Download albums by URL or ID.
2. Download all user albums.
3. Download albums from list.txt.
4. Search albums by keyword.
5. [Settings](#settings).
0. Exit.

### Settings

1. Change Directory (Change albums download directory. Default = "./Albums/").
2. CPU Pool (Default = Your CPU Count).
3. Picture Retries (download attempts for each picture. Default = 5).
4. Picture Timeout (download timeout for each picture. Default = 30).
5. Download Delay (delay between downloading multiple albums. Default = 0)
0. Back.
