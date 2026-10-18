@echo off

"%~dp0backend\.venv\Scripts\python.exe" "%~dp0deploy\start_local.py"

if errorlevel 1 pause
