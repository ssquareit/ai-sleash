@echo off
title Sleash Build
echo ============================================
echo   Sleash Browser — Build Script
echo ============================================
echo.

:: Check PyInstaller is available
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller not found. Run: pip install pyinstaller
    pause & exit /b 1
)

:: Check assets/icon.ico exists
if not exist "assets\icon.ico" (
    echo [WARNING] assets\icon.ico not found.
    echo           A default icon will be used.
    echo.
)

:: Create output dirs
if not exist "dist\installer" mkdir "dist\installer"

echo [1/2] Building exe with PyInstaller...
pyinstaller sleash.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed.
    pause & exit /b 1
)

echo.
echo [2/2] PyInstaller done!
echo       Output folder: dist\Sleash\
echo.
echo ============================================
echo  NEXT STEP — Create the installer:
echo    1. Download Inno Setup from:
echo       https://jrsoftware.org/isdl.php
echo    2. Open installer.iss in Inno Setup
echo    3. Press Ctrl+F9 to compile
echo    4. Installer saved to: dist\installer\
echo ============================================
echo.
pause
