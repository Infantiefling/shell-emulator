@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/nested.csv --script scripts/demo_stage4.txt
