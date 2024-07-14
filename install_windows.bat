@echo off
echo Installing dependencies for AlwaysOnTopApp...

:: Check for Python installation
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Downloading and installing Python...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)

:: Create a virtual environment
echo Creating a virtual environment...
python -m venv venv

:: Activate the virtual environment
call venv\Scripts\activate

:: Upgrade pip in the virtual environment
python -m pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
python -m pip install tk watchdog

echo Dependencies installed successfully.
echo To activate the virtual environment, run "venv\Scripts\activate".
pause
