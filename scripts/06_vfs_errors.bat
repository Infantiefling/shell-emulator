@echo off
cd /d "%~dp0.."
echo === Missing VFS ===
call run.bat --vfs examples/missing.csv
echo.
echo === Invalid VFS ===
call run.bat --vfs examples/invalid.csv
pause
