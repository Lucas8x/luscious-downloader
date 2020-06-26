# Luscious Downloader
CLi tool for downloading Luscious Albums

## Requirements
* Python 3
* requests

## Installation
*If you have python installed.*
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
**NOTE:** The default download folder will be the path where you are executing the command.

Download album by URL or ID:\
*You can enter multiple url and ids separated by commas.*
<pre><code>lsd -d https://members.luscious.net/albums/light-yuri_275719/
lsd -d 275719,292887
</code></pre>

<pre><code>
Options:
  -h, --help            show help message
# Download
  -d URL_OR_ID --download URL_OR_ID
                        download album by URL or ID
# Download Options
  -o DIRECTORY --output DIRECTORY       
                        output directory
  -t THREADS --threads THREADS
                        how many download threads
  -R RETRIES --retries RETRIES
                        download attempts for each picture
  -T TIMEOUT --timeout TIMEOUT
                        download timeout for each picture
  -D DELAY --delay DELAY
                        delay between downloading multiple albums
</code></pre>

## Menu
1. Enter Album URL or ID.
2. Download from list.txt.
3. [Settings](#settings).
0. Exit.

### Settings
1. Change Directory (Change albums download directory).
2. CPU Pool (Default = Your CPU Count).
3. Picture Retries (download attempts for each picture).
4. Picture Timeout (download timeout for each picture).
5. Download Delay (delay between downloading multiple albums)
0. Back.
