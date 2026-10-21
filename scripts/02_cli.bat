@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/files.csv --script scripts/demo_stage3.txt
