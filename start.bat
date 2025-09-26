@echo off
echo Starting Alerting Platform...

echo.
echo Initializing backend database...
cd backend
python database.py

echo.
echo Starting backend server...
start "Backend" cmd /k "python main.py"

echo.
echo Installing frontend dependencies...
cd ..\frontend
call npm install

echo.
echo Starting frontend development server...
start "Frontend" cmd /k "npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul