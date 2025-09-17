@echo off
title EMP 시스템 검사 도구
echo EMP 데스크탑 컨트롤러 - 시스템 검사 도구
echo ========================================
echo.

REM 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python이 설치되어 있습니다.
echo.

REM 시스템 검사 실행
echo 시스템 검사를 시작합니다...
echo.
python test_emp_path.py

echo.
echo 검사가 완료되었습니다.
pause
exit /b 0
