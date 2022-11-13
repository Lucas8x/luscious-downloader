# Luscious Downloader

CLI tool for downloading albums from [Luscious](https://luscious.net)

![Downloads](https://img.shields.io/pypi/dm/luscious-downloader?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/luscious-downloader?style=flat-square)
![License](https://img.shields.io/github/license/lucas8x/luscious-downloader?style=flat-square)

## 🚀 Installation

### Manual

_If you have python and git installed._

```bash
git clone https://github.com/Lucas8x/luscious-downloader.git
cd luscious-downloader
python setup.py install
```

### PIP

```bash
pip install luscious-downloader
```

If you want album to PDF conversion use:

```bash
pip install luscious-downloader[pdf]
```

### Windows Only

_If you don't have python or git installed._

1. [Download](https://github.com/Lucas8x/luscious-downloader/archive/main.zip).
2. Extract.
3. Run `run.bat`.
4. Wait install.
5. [Menu](#Menu)

## 🔨 Usage

**NOTE:** On windows you can press shift + right click to open terminal in selected folder.\
**NOTE²:** The default download folder will be the path where you're executing the command.\
**NOTE³:** You can enter multiple url and ids separated by commas.

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

Download all user's favorites:

```bash
lsd -u https://members.luscious.net/users/668124/ -f
lsd -u 668124,274991 -f
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

**⌨ CLI options:**

```text
Options:
    -h, --help              show help message
  # Download
    -a ALBUM_INPUTS, --album ALBUM_INPUTS
                            download album by url or id
    -u USER_INPUTS,  --user USER_INPUTS
                            download all user albums by url or id
    -s KEYWORD,      --search KEYWORD
                            search albums by keyword
    -f, --favorites
                            download only the user's favorites
    -g, --group, --agroup
                            group albums by uploader name
    -l, --list
                            download albums from list.txt in the folder
  # Search Options
    --download, -d          download albums from search results
    --page PAGE             page number of search results
    --max-page MAX_PAGES    max pages of search results
    --sorting {date_trending,rating_all_time}
                            sorting of search albums

  # Generate Options
    --pdf, -p               Enable album PDF generation
    --cbz, -c               Enable album CBZ generation
    --rm-origin-dir         Delete album folder when generate pdf or cbz

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

## 📜 Menu

1. Download albums by URL or ID.
2. Download all user albums.
3. Download all user favorites.
4. Search albums by keyword.
5. Download albums from list.txt.
6. [Settings](#settings).
0. Exit.

### ⚙️ Settings

1. Change Directory (Change albums download directory. Default = "./Albums/")
2. CPU Pool (Default = Your CPU Count)
3. Picture Retries (download attempts for each picture. Default = 5)
4. Picture Timeout (download timeout for each picture. Default = 30)
5. Download Delay (delay between downloading multiple albums. Default = 0)
6. Format output album folder name (Default = [%i]%t)
7. Generate PDF (Default = False)
8. Generate CBZ (Default = False)
9. Remove origin directory (Default = False)
10. Group albums by upload name (Default = False)
0. Back.

## 📝 License

[MIT](LICENSE)
