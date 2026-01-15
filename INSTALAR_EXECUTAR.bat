@echo off
chcp 65001 >nul 2>&1
title Sistema de Peticoes PCR - Instalador

echo.
echo ====================================================
echo    SISTEMA DE PETICOES AUTOMATICAS - PCR
echo    Instalador Automatico
echo ====================================================
echo.

REM Verificar se Python já está instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python encontrado!
    goto :instalar_dependencias
)

echo [INFO] Python nao encontrado. Iniciando instalacao automatica...
echo.

REM Baixar instalador do Python
echo [1/3] Baixando Python 3.11.7...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'}"

if not exist python_installer.exe (
    echo [ERRO] Falha ao baixar Python!
    pause
    exit /b 1
)

echo [2/3] Instalando Python...
echo      (Instalacao silenciosa - aguarde 1-2 minutos)
start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

del python_installer.exe

echo [3/3] Verificando instalacao...
timeout /t 5 /nobreak >nul
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi instalado corretamente!
    echo Por favor, reinicie o computador e tente novamente.
    pause
    exit /b 1
)

echo [OK] Python instalado com sucesso!
echo.

:instalar_dependencias
echo ====================================================
echo [INFO] Instalando bibliotecas necessarias...
echo       (Isso pode levar 2-3 minutos na primeira vez)
echo ====================================================
echo.

python -m pip install --upgrade pip --quiet
python -m pip install streamlit pandas boto3 python-dotenv awswrangler reportlab openpyxl xlrd --quiet

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo [OK] Instalacao concluida!
echo.

:executar
echo ====================================================
echo [INFO] Iniciando aplicacao...
echo       O navegador sera aberto automaticamente.
echo.
echo       Para fechar: Pressione CTRL+C
echo ====================================================
echo.

streamlit run main.py --theme.base=light

pause