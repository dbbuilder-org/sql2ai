@echo off
REM SQLReleaseNotes2 - SQL Execution
setlocal enabledelayedexpansion
color 0A

echo ===============================================================================
echo                       SQL EXECUTION
echo ===============================================================================
echo.

REM Check prerequisites
if not exist "..\venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv venv
    echo Then: pip install -r requirements.txt
    pause & exit /b 1
)

if not exist "..\.env" (
    echo ERROR: .env file not found
    echo Please copy .env.example to .env and configure it
    pause & exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

REM Get target database name
set /p TARGET_DB="Enter TARGET database name: "
if "%TARGET_DB%"=="" echo ERROR: Target database name required & pause & exit /b 1

REM Get SQL files
echo.
echo Enter the paths to SQL files to execute (separated by spaces):
echo Example: output\metadata\file1.sql output\tests\file2.sql
set /p SQL_FILES="SQL files: "
if "%SQL_FILES%"=="" echo ERROR: SQL files required & pause & exit /b 1

echo.
echo Configuration:
echo - Target DB: %TARGET_DB%
echo - SQL Files: %SQL_FILES%
set /p CONFIRM="Continue? (Y/n): "
if /i "%CONFIRM%"=="n" echo Cancelled & pause & exit /b 0
echo.

REM Run sqlexec module
echo.
echo Running SQL execution module...
echo Command: python ..\sqlreleasenotes.py sqlexec --target-db %TARGET_DB% --files %SQL_FILES%
echo.
python ..\sqlreleasenotes.py sqlexec --target-db %TARGET_DB% --files %SQL_FILES%
if !errorlevel! neq 0 (
    echo ERROR: SQL execution failed
    echo Check logs for details
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo                             EXECUTION COMPLETE
echo ===============================================================================
echo.
echo SQL execution completed successfully!
echo.
echo Log Files:
echo   - Execution logs are in the output\logs\sqlexec_* directory
echo.
pause
