@echo off
title JevTools
echo Starting JevTools Web Dashboard on http://localhost:8089...
py "%~dp0server.py" %*
pause
