@echo off
cd /d "%~dp0"
python -c "import PIL,numpy" >nul 2>nul
if errorlevel 1 python -m pip install -r requirements.txt
python app\jack_generator.py
