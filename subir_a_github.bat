@echo off
title Subir Perfil EternoDev a GitHub
echo ========================================================
echo   SUBIENDO PERFIL DE ETERNODEV A GITHUB
echo   Repositorio: https://github.com/Eterno-Dev/eterno-dev.git
echo ========================================================
echo.

cd /d "%~dp0"

echo [+] Comprobando estado de git...
git status

echo.
echo [+] Subiendo a origin main...
echo [!] Si se abre el navegador, confirma el inicio de sesion con tu cuenta Eterno-Dev.
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   PERFIL SUBIDO CON EXITO!
    echo   Ya puedes verlo en vivo en:
    echo   https://github.com/Eterno-Dev
    echo ========================================================
) else (
    echo.
    echo [!] Hubo un error al subir. Revisa tus credenciales de GitHub.
)

echo.
pause
