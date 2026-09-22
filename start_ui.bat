@echo off
title JevTools UI Cockpit
echo Starting JevTools Web Cockpit on http://localhost:8089...
py "%~dp0server.py" %*
pause
