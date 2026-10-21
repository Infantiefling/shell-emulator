@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/minimal.csv --script scripts/demo_stage3.txt --config config.xml
