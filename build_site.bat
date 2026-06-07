@echo off
setlocal
cd /d "%~dp0"
python build_site.py
endlocal
