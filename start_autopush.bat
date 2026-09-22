@echo off
title GitHub Auto-Sync Watcher
cls
echo ========================================================
echo   GitHub Auto-Sync Watcher
echo   Repo: thamizharasanm2528-byte/Data_Analytics_Project_RetailPrice
echo ========================================================
echo.
echo Any changes you save in the project will automatically be
echo committed and pushed to GitHub after 15 seconds.
echo.
echo Keep this window open in the background while working.
echo Press Ctrl+C to stop auto-sync.
echo.
.venv\Scripts\python.exe auto_sync.py
pause
