@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/sample.csv --script scripts/demo_stage4.txt
