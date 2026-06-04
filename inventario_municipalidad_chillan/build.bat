@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Compilador — Inventario Municipalidad de Chillán

set PY=python

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║   Compilador de Inventario Municipalidad de Chillán  ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: ── Verificar directorio correcto ─────────────────────────────────────────────
if not exist "main.py" (
    echo [ERROR] No se encontro main.py
    echo         Ejecuta este script desde la carpeta raiz del proyecto.
    pause
    exit /b 1
)
if not exist "config.txt" (
    echo [ERROR] No se encontro config.txt
    pause
    exit /b 1
)
if not exist "assets\Bannermuni.png" (
    echo [ERROR] No se encontro assets\Bannermuni.png
    pause
    exit /b 1
)
if not exist "assets\iconoMuni.png" (
    echo [ERROR] No se encontro assets\iconoMuni.png
    pause
    exit /b 1
)
if not exist "inventario.spec" (
    echo [ERROR] No se encontro inventario.spec
    pause
    exit /b 1
)

:: ── Verificar Python ──────────────────────────────────────────────────────────
%PY% --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

:: ── Verificar dependencias de compilacion ─────────────────────────────────────
echo [1/5] Verificando dependencias...
%PY% -c "import PyInstaller" > nul 2>&1
if errorlevel 1 (
    echo       Instalando PyInstaller...
    %PY% -m pip install --quiet pyinstaller pyinstaller-hooks-contrib
    if errorlevel 1 goto :error_dependencias
)

%PY% -c "import wmi, psutil, requests" > nul 2>&1
if errorlevel 1 (
    echo       Instalando dependencias del proyecto...
    %PY% -m pip install --quiet wmi psutil requests
    if errorlevel 1 goto :error_dependencias
)

echo       OK
echo.
goto :limpiar

:error_dependencias
echo [ERROR] Fallo la instalacion/verificacion de dependencias.
pause
exit /b 1

:limpiar
:: ── Limpiar compilaciones anteriores ─────────────────────────────────────────
echo [2/5] Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo       OK
echo.

:: ── Compilar ─────────────────────────────────────────────────────────────────
echo [3/5] Compilando en modo ONEDIR...
echo.
%PY% -m PyInstaller inventario.spec --noconfirm --clean
if errorlevel 1 (
    echo.
    echo [ERROR] La compilacion fallo. Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

:: ── Verificar resultado ───────────────────────────────────────────────────────
if not exist "dist\InventarioMunicipalidad\InventarioMunicipalidad.exe" (
    echo [ERROR] No se genero el .exe esperado.
    pause
    exit /b 1
)

:: ── Generar .zip listo para distribuir ───────────────────────────────────────
echo [4/5] Generando .zip para distribucion...
echo.

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd"') do set fecha=%%I
set ZIP_NAME=InventarioMunicipalidad_%fecha%.zip

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -Path 'dist\InventarioMunicipalidad' -DestinationPath 'dist\%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo [AVISO] No se pudo generar el .zip automaticamente.
    echo         Puedes comprimir manualmente la carpeta dist\InventarioMunicipalidad
) else (
    echo       ZIP generado: dist\%ZIP_NAME%
)
echo.

:: ── Resumen final ─────────────────────────────────────────────────────────────
echo [5/5] Compilacion exitosa.
echo.
echo ══════════════════════════════════════════════════════════
echo.
echo   Carpeta lista : dist\InventarioMunicipalidad\
echo   ZIP para subir: dist\%ZIP_NAME%
echo.
echo   Instrucciones para los PCs de la municipalidad:
echo     1. Descargar y descomprimir el .zip una sola vez
echo     2. Entrar a la carpeta InventarioMunicipalidad
echo     3. Doble clic en InventarioMunicipalidad.exe
echo     4. Aceptar permisos de administrador si Windows lo solicita
echo.
echo   No requiere Python instalado en el PC destino.
echo   No descarga dependencias en el PC destino.
echo ══════════════════════════════════════════════════════════
echo.

explorer "dist"
pause
