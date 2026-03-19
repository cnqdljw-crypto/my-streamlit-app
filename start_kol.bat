@echo off
title YouTube KOL 分析工具

cd /d %~dp0

echo 启动 Streamlit 网站...
start cmd /k "streamlit run app.py --server.port 8501"

timeout /t 5 >nul

echo 启动 ngrok 映射端口...
start cmd /k "C:\ngrok\ngrok.exe http 8501"

echo.
echo ==========================
echo 本地地址:
echo http://localhost:8501
echo ==========================
echo.

pause