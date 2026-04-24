@echo off
taskkill /FI "WINDOWTITLE eq ARLS Backend*" /T /F
taskkill /FI "WINDOWTITLE eq ARLS Frontend*" /T /F
