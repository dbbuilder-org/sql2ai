@echo off
REM SQLReleaseNotes2 - Test Generator
setlocal enabledelayedexpansion
color 0A

echo ===============================================================================
echo                       TEST PROCEDURE GENERATOR
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
echo - Mode: %PREVIEW_FLAG%
set /p CONFIRM="Continue? (Y/n): "
if /i "%CONFIRM%"=="n" echo Cancelled & pause & exit /b 0
echo.

REM Run test module
echo.
echo Running test module...
echo Command: python ..\sqlreleasenotes.py test --new-db %NEW_DB% --old-db %OLD_DB% %PREVIEW_FLAG%
echo.
python ..\sqlreleasenotes.py test --new-db %NEW_DB% --old-db %OLD_DB% %PREVIEW_FLAG%
if !errorlevel! neq 0 (
    echo ERROR: Test procedure generation failed
    echo Check logs for details
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo                             EXECUTION COMPLETE
echo ===============================================================================
echo.
echo Test procedure generation completed successfully!
echo.
echo Generated Files:
echo   - Test Procedures: output\tests\TEST_PROCEDURES_*.sql
echo   - Test Runner: output\tests\TEST_RUNNER_*.sql
echo.
echo Check the output\tests directory for the generated files.
echo.
pause
