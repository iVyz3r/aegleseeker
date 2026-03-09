:: Aegleseeker Client
:: Copyright (C) 2026 ilyVyzer_
::
:: This program is free software: you can redistribute it and/or modify
:: it under the terms of the GNU General Public License version 3.

@echo off
echo Setting up the environment...
echo Installing required packages...
pip install pymem
pip install dearpygui
pip install pypresence
pip install pyinstaller
py aeglemain.py

echo Build complete
