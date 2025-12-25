@echo off
echo Building SSMS-AI MVP...
echo.

REM Navigate to src directory
cd /d "%~dp0src"

REM Restore NuGet packages
echo Restoring NuGet packages...
nuget restore SSMS-AI.sln
if errorlevel 1 (
    echo Failed to restore NuGet packages
    pause
    exit /b 1
)

REM Build the solution
echo.
echo Building solution...
msbuild SSMS-AI.sln /p:Configuration=Debug /p:Platform="Any CPU" /p:DeployExtension=false
if errorlevel 1 (
    echo Build failed
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo VSIX package location: src\SSMS-AI.SSMS\bin\Debug\
echo.
pause
