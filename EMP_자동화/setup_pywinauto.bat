@echo off
echo pywinauto 환경 설정 중...
echo.

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python 버전:
python --version
echo.

REM 새로운 가상환경 생성
echo 가상환경 생성 중...
python -m venv pywinauto_env

REM 가상환경 활성화
echo 가상환경 활성화 중...
call pywinauto_env\Scripts\activate.bat

REM pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM pywinauto 설치
echo pywinauto 설치 중...
pip install -r requirements.txt

echo.
echo ====================================
echo pywinauto 환경 설정 완료!
echo ====================================
echo.
echo 사용법:
echo 1. 활성화: pywinauto_env\Scripts\activate
echo 2. 비활성화: deactivate
echo.
pause
