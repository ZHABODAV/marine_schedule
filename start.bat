@echo off
echo Starting Enhanced Vessel Scheduler Server...
echo Direct link: http://localhost:5000
echo Don't close this window
start http://localhost:5000/
python api_server_enhanced.py
pause
