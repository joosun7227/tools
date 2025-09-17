@echo off
title EMP 데스크탑 컨트롤러
echo EMP 데스크탑 컨트롤러 시작 중...
echo.

REM 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

REM Python 스크립트 실행
python emp_controller.py

REM 오류가 발생한 경우 대기
if errorlevel 1 (
    echo.
    echo 오류가 발생했습니다. 로그를 확인해주세요.
    pause
)

exit /b 0
