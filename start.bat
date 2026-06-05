@echo off
echo Starting Frontend Build Watcher and Backend Flask Server...

:: Start frontend watch build in a separate terminal window
start "Frontend Build Watcher" cmd /c "cd frontend && npm run build:watch"

:: Start backend Flask server in the current window
echo Starting Flask server on http://localhost:5001...
cd backend
python app.py
