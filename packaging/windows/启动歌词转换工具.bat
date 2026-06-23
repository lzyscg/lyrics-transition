@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"
set PYTHONUTF8=1
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo 正在启动歌词转换工具...
echo.
echo 浏览器会自动打开 http://localhost:8501
echo 使用期间请不要关闭这个窗口。关闭窗口后，工具也会停止。
echo.

start "" cmd /c "timeout /t 3 >nul && start "" http://localhost:8501"
"%~dp0python\python.exe" -m streamlit run "%~dp0app.py" --server.address 127.0.0.1 --server.headless true --server.port 8501 --browser.gatherUsageStats false

echo.
echo 工具已停止。按任意键关闭窗口。
pause >nul
