# Luscious Downloader
CLI tool for downloading Luscious Albums

## Requirements
* Python 3
* requests

## Installation
*If you have python and git installed.*
<pre><code>git clone https://github.com/Lucas8x/luscious-downloader.git
cd luscious-downloader
python setup.py install
</code></pre>
*or through pip.*
<pre><code>pip install luscious-downloader
</code></pre>

## Installation #2 (Windows Only)
*If you don't have python installed.*
1. [Download](https://github.com/Lucas8x/luscious-downloader/archive/master.zip).
2. Extract.
3. Run `run.bat`.
4. Wait install.

## Usage
**NOTE:** The default download folder will be the path where you are executing the command.\
**NOTE²:** You can enter multiple url and ids separated by commas.

Download albums:
<pre><code>lsd -a https://members.luscious.net/albums/light-yuri_275719/
lsd -a 275719,292887
</code></pre>

Download all user's albums:
<pre><code>lsd -u https://members.luscious.net/users/668124/
lsd -u 668124,274991
</code></pre>

Download search albums:
<pre><code>lsd -s yuri -d
lsd -s yuri -d --page 2 --max-page 5
</code></pre>

<pre><code>Options:
  -h, --help            show help message
# Download
  -a ALBUM_INPUTS, --album ALBUM_INPUTS
                        download album by url or id
  -u USER_INPUTS, --user USER_INPUTS
                        download all user albums by url or id
  -s KEYWORD, --search KEYWORD
                        search albums by keyword
# Search Options
  --download, -d        download albums from search results
  --page PAGE           page number of search results
  --max-page MAX_PAGES  max pages of search results

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
</code></pre>

## Menu
1. Enter albums URL or ID.
2. Download all user albums.
3. Download albums from list.txt.
4. [Settings](#settings).
0. Exit.

### Settings
1. Change Directory (Change albums download directory. Default = "./Albums/").
2. CPU Pool (Default = Your CPU Count).
3. Picture Retries (download attempts for each picture. Default = 5).
4. Picture Timeout (download timeout for each picture. Default = 30).
5. Download Delay (delay between downloading multiple albums. Default = 0)
0. Back.
