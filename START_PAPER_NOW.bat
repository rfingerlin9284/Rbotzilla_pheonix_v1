@echo off
REM FASTEST PATH TO LIVE - WINDOWS BATCH
REM Copy and run this to start paper trading immediately

cd /d c:\Users\RFing\temp_access_RICK_LIVE_CLEAN

REM Set environment
set ENVIRONMENT=practice

echo.
echo =====================================
echo STARTING PAPER MODE TRADING
echo =====================================
echo Directory: %cd%
echo Environment: %ENVIRONMENT%
echo Time: %date% %time%
echo =====================================
echo.

REM Start the system
python oanda_trading_engine.py

REM If it crashes
if errorlevel 1 (
    echo.
    echo ERROR - System failed to start
    echo Check logs:
    echo   type engine_output.log
    echo   type narration.jsonl
    pause
    exit /b 1
)
