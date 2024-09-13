@echo off
setlocal

:: Đường dẫn URL đến tệp Python cài đặt và script cần tải xuống
set fileUrl=https://raw.githubusercontent.com/dungviet224/muamenmen/main/update.py
set pythonInstallerUrl=https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe
set tempDir=%TEMP%
set pythonInstallerFile=%tempDir%\python-3.12.5-amd64.exe
set updateFilePath=%tempDir%\update.py

:: Kiểm tra phiên bản Python
python --version 2>NUL | find "Python 3.12.5" >NUL
if %errorlevel% neq 0 (
    echo Python chưa được cài đặt hoặc phiên bản không đúng, đang tải xuống Python...
    curl -L -o "%pythonInstallerFile%" %pythonInstallerUrl%
    echo Đang chạy trình cài đặt Python...
    start /wait "" "%pythonInstallerFile%"
    
    :: Kiểm tra lại sau khi cài đặt
    python --version 2>NUL | find "Python 3.12.5" >NUL
    if %errorlevel% neq 0 exit /b
    start "" "%~f0"
    exit /b
)

:: Tải xuống script update.py nếu cần thiết
if not exist "%updateFilePath%" (
    curl -L -o "%updateFilePath%" %fileUrl%
)

:: Chạy script đã tải xuống
start "" "python" "%updateFilePath%"
exit /b
