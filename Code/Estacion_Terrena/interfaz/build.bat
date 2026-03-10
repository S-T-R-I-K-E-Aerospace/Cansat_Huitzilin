@echo off
REM ============================================================
REM STRIKE Aerospace - Build Script
REM ============================================================
REM Este script genera el ejecutable con PyInstaller.
REM Ejecutar DESDE el virtualenv (cansat_env).
REM
REM Uso:
REM   1. Abre una terminal en la carpeta del proyecto
REM   2. Activa el entorno: cansat_env\Scripts\activate
REM   3. Ejecuta: build.bat
REM ============================================================

echo.
echo ============================================================
echo  STRIKE Aerospace - Build del Ejecutable
echo ============================================================
echo.

REM Verificar que PyInstaller está instalado
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller no encontrado. Instalando...
    pip install pyinstaller
)

echo [1/2] Generando ejecutable con PyInstaller...
echo.

pyinstaller ^
    --onedir ^
    --windowed ^
    --name "STRIKE_Mission_Control" ^
    --icon "assets\LogoSTRIKE300.ico" ^
    --add-data "assets;assets" ^
    --noconfirm ^
    --clean ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Fallo al generar el ejecutable.
    pause
    exit /b 1
)

REM Crear las carpetas de datos en el directorio de salida
echo.
echo [2/3] Creando carpeta received_images...
if not exist "dist\STRIKE_Mission_Control\received_images" (
    mkdir "dist\STRIKE_Mission_Control\received_images"
)

echo [3/3] Creando carpeta received_files...
if not exist "dist\STRIKE_Mission_Control\received_files" (
    mkdir "dist\STRIKE_Mission_Control\received_files"
)

echo.
echo ============================================================
echo  BUILD COMPLETADO EXITOSAMENTE
echo ============================================================
echo.
echo  Ejecutable en: dist\STRIKE_Mission_Control\
echo  Archivo:       dist\STRIKE_Mission_Control\STRIKE_Mission_Control.exe
echo.
echo  SIGUIENTE PASO:
echo    - Para probar: ejecuta el .exe directamente
echo    - Para crear instalador: abre installer.iss con Inno Setup
echo.
pause
