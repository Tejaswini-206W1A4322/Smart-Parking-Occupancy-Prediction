@echo off
echo ==============================================
echo Smart Parking App - Windows Setup & Run Script
echo ==============================================

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting the application...
streamlit run app.py --server.port 8503

pause
