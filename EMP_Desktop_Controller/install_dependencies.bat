@echo off
echo EMP 데스크탑 컨트롤러 의존성 설치 중...
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

echo pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo 설치 완료!
echo emp_controller.py를 실행하여 프로그램을 시작할 수 있습니다.
echo.
pause
