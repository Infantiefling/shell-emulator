@echo off
cd /d "%~dp0.."
call run.bat --vfs examples/cli.csv --script scripts/demo.txt --config config.xml
