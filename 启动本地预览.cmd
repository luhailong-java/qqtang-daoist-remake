@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 goto bundled
node scripts\serve.mjs
goto done
:bundled
if not exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" goto missing
"%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" scripts\serve.mjs
goto done
:missing
echo 请先安装 Node.js 22 或更新版本，然后重新打开本文件。
:done
pause
