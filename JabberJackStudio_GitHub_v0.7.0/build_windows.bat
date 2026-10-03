@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements-dev.txt
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
python -m PyInstaller --noconfirm --clean --windowed --onefile --name JabberJackStudio app\jack_generator.py
python -m PyInstaller --noconfirm --clean --windowed --onefile --name ImportFactoryFaces import_factory_faces.py
mkdir dist\assets\faces 2>nul
mkdir dist\tools 2>nul
copy README.md dist\ >nul
copy LICENSE dist\ >nul
copy THIRD_PARTY.md dist\ >nul
echo Build complete. Put ffmpeg.exe in dist\tools or install FFmpeg on PATH.
pause
