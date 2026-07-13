@echo off

call venv\Scripts\activate


pyinstaller ^
 --name NoVisageLock ^
 --windowed ^
 --onedir ^
 --clean ^
 --add-data "config.json;." ^
 --add-data "tray.py;." ^
 --add-data "enroll_camera.py;." ^
 --add-data "models;models" ^
 main.py


pause