@echo off
title Quick Push to GitHub
cls
echo ========================================================
echo   Pushing All Changes to GitHub...
echo ========================================================
git add .
set TIMESTAMP=%date% %time%
git commit -m "Update project: %TIMESTAMP%"
git push origin main
echo.
echo ========================================================
echo   Done! All changes are live on GitHub.
echo ========================================================
pause
