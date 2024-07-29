@echo off
set path_now=%~dp0
echo Run: pip install -r %path_now%requirements.txt
pip install -r %path_now%requirements.txt