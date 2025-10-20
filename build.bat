@echo off
echo Setting up the environment...
echo Installing required packages...
pip install pymem
pip install dearpygui
pip install pypresence
pip install pyinstaller
py main.py

echo Build complete
