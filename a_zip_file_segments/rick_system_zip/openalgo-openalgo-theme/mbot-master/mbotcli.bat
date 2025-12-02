@echo off
setlocal

REM Navigate to the directory containing the script
cd /d %~dp0

REM Activate virtual environment if it exists
if exist "mbot\venv\Scripts\activate" (
	call mbot\venv\Scripts\activate
) else (
	echo Could not find the virtual environment.
	echo Please run the setup script to create the virtual environment
	echo and install the required packages.
	echo Exiting...
	exit /b 1
)

REM Run the CLI
python mbot\src\mbotcli.py %*

endlocal
