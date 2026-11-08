@echo off
python -m unittest discover -s tests -v
if errorlevel 1 exit /b 1
python reproduce_all.py --native-status
