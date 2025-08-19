@echo off
echo ========================================
echo    Friday AI Assistant - Starting...
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Friday AI Web Server...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python backend.py
pause
