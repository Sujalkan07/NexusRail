@echo off
setlocal
cd /d "C:\Users\sujal\OneDrive\Documents\GitHub\NexusRail"
".venv\Scripts\python.exe" -m pip install -r requirements.txt --disable-pip-version-check
".venv\Scripts\python.exe" -m pytest -q tests\test_phase1_validation.py
