@echo off
REM SQLReleaseNotes2 - Master Runner
setlocal enabledelayedexpansion
color 0A

echo ===============================================================================
echo                    SQL RELEASE NOTES SYSTEM - MASTER RUNNER
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

REM Get database names
set /p NEW_DB="Enter NEW database name (format: MyApp_v2_1): "
set /p OLD_DB="Enter OLD database name (format: MyApp_v2_0): "

if "%NEW_DB%"=="" echo ERROR: New database name required & pause & exit /b 1
if "%OLD_DB%"=="" echo ERROR: Old database name required & pause & exit /b 1

REM Target database option
set /p TARGET_DB="Enter TARGET database name for SQL execution (default: %NEW_DB%): "
if "%TARGET_DB%"=="" set TARGET_DB=%NEW_DB%

REM Preview mode option
set /p PREVIEW_MODE="Run in PREVIEW mode? (y/N): "
if /i "%PREVIEW_MODE%"=="y" (
    set PREVIEW_FLAG=--preview
    echo Preview mode ENABLED
) else (
    set PREVIEW_FLAG=
    echo Full mode ENABLED
)

echo.
echo Configuration:
echo - New DB: %NEW_DB%
echo - Old DB: %OLD_DB%
echo - Target DB: %TARGET_DB%
echo - Mode: %PREVIEW_FLAG%
set /p CONFIRM="Continue? (Y/n): "
if /i "%CONFIRM%"=="n" echo Cancelled & pause & exit /b 0
echo.
echo ===============================================================================
echo                           STARTING EXECUTION
echo ===============================================================================

REM Run all modules
echo.
echo Running all modules...
echo Command: python ..\sqlreleasenotes.py all --new-db %NEW_DB% --old-db %OLD_DB% --target-db %TARGET_DB% %PREVIEW_FLAG%
echo.
python ..\sqlreleasenotes.py all --new-db %NEW_DB% --old-db %OLD_DB% --target-db %TARGET_DB% %PREVIEW_FLAG%
if !errorlevel! neq 0 (
    echo ERROR: Execution failed
    echo Check logs for details
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo                             EXECUTION COMPLETE
echo ===============================================================================
echo.
echo All modules have completed successfully!
echo.
echo Generated Files:
echo   - Release Notes: output\release\RELEASE_NOTES_*.md
echo   - SQL Scripts: output\release\RELEASE_SQL_*.md  
echo   - Metadata: output\metadata\METADATA_SCRIPT_*.sql
echo   - Test Procedures: output\tests\TEST_PROCEDURES_*.sql
echo   - Test Runner: output\tests\TEST_RUNNER_*.sql
echo.
echo Log Files:
echo   - All logs are in the output\logs directory
echo.
echo Check the respective directories for the generated files.
echo.
echo ===============================================================================
echo                               SUMMARY
echo ===============================================================================
echo.
echo Databases Compared: %OLD_DB% --^> %NEW_DB%
echo SQL Execution Target: %TARGET_DB%
echo Mode: %PREVIEW_FLAG%
echo Status: SUCCESS
echo.
pause
