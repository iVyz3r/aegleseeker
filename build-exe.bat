@echo off
echo Setting up the environment...
echo Installing VENV environment...
python -m venv venv
call venv\Scripts\activate.bat
echo Installing required packages...
pip install pymem
pip install dearpygui
pip install pypresence
pip install pyinstaller
echo Building the executable...
pyinstaller --onefile --noconsole --icon="aegleseeker.ico" aeglemain.py
echo Build complete
echo Deactivating VENV environment...
deactivate
else
  echo Cant find venv, please run build.bat first to set up the environment.
endif
echo Build process finished.
