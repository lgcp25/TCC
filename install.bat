@echo off
title Instalador Vaporeon Pentester Suite (Windows)
color 0A

echo [*] Iniciando a instalacao das dependencias do Vaporeon para Windows...
echo.

echo [*] Verificando instalacao do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERRO: Python nao encontrado! Instale o Python marcando a caixa "Add Python to PATH".
    pause
    exit /b
)

echo [*] Instalando bibliotecas do Python (Flet)...
pip install flet

echo [*] Verificando Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] AVISO: Docker nao detectado. Para executar as ferramentas (Nmap/SQLmap), instale o Docker Desktop.
) else (
    echo [+] Docker detectado no sistema!
)

echo.
echo [+] Instalacao concluida com sucesso!
echo     Para abrir o painel, digite: python app/main.py
pause
