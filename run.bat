@echo off
.\venv\Scripts\python3.exe luscious-downloader.py
taskkill /f /im chromedriver.exe
cmd /k