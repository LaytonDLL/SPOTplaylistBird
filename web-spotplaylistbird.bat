@echo off
SETLOCAL EnableDelayedExpansion

REM Launcher Universal para Windows
REM ----------------------------------------------------------------------
REM Este script tenta localizar a pasta do projeto automaticamente se não estiver
REM sendo executado de dentro dela. Ideal para atalhos.

echo ==================================================
echo 🔍 SPOTplaylistBird - Launcher Automático (Windows)
echo ==================================================

REM 1. Verificar se já estamos no diretório
IF EXIST "run_windows.bat" (
    echo ✅ Executando de dentro do projeto.
    goto :START
)

REM 2. Procurar automaticamente
echo 🔍 Procurando pasta do projeto no sistema...

SET FOUND_DIR=

REM Lista de diretórios Base para buscar
SET SEARCH_BASE="%USERPROFILE%\Desktop" "%USERPROFILE%\Downloads" "%USERPROFILE%\Documents" "%USERPROFILE%" "%OneDrive%\Desktop" "%OneDrive%\Documents"

REM Lista de nomes de pasta possíveis
SET SEARCH_NAMES="SPOTplaylistBird" "spotify-playlist-filler" "web-spotplaylistbird" "spotify-playlist-filler-main" "spotify-playlist-filler-master"

FOR %%D IN (%SEARCH_BASE%) DO (
    IF EXIST %%D (
        FOR %%N IN (%SEARCH_NAMES%) DO (
            REM Verificar pasta direta: Base\Nome
            IF EXIST "%%~D\%%~N\run_windows.bat" (
                SET FOUND_DIR="%%~D\%%~N"
                goto :FOUND
            )
            REM Verificar subpasta: Base\Nome\SPOTplaylistBird
            IF EXIST "%%~D\%%~N\SPOTplaylistBird\run_windows.bat" (
                SET FOUND_DIR="%%~D\%%~N\SPOTplaylistBird"
                goto :FOUND
            )
        )
    )
)

:NOT_FOUND
echo ❌ Erro Crítico: Pasta do projeto não encontrada!
echo    Certifique-se que extraiu o ZIP na Área de Trabalho, Downloads ou Documentos.
pause
exit /b 1

:FOUND
echo 🚀 Encontrado em: !FOUND_DIR!
cd /d !FOUND_DIR!

:START
echo ⏳ Iniciando em 5 segundos... (Pressione uma tecla para pular)
timeout /t 5

echo 🔥 Iniciando...
call run_windows.bat
