@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo AICA L2 퀴즈 로컬 서버 (http://localhost:8765)
echo 종료: Ctrl+C
python -m http.server 8765
