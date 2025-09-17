"""
EMP 프로그램 경로 테스트 도구
EMP 프로그램이 올바르게 설치되어 있는지 확인하는 유틸리티

작성자: 예주나라
작성일: 2025-09-17
"""

import os
import sys
import subprocess
import psutil
from pathlib import Path

def test_emp_installation():
    """EMP 설치 상태 확인"""
    print("=" * 60)
    print("EMP 프로그램 설치 상태 확인")
    print("=" * 60)
    
    # 기본 경로 확인
    emp_path = r"C:\Users\jusun\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\EMP - (주)난소프트\EMP - Enhanced Management Plus.appref-ms"
    
    print(f"1. EMP 경로 확인:")
    print(f"   경로: {emp_path}")
    
    if os.path.exists(emp_path):
        print("   ✓ EMP 바로가기 파일이 존재합니다.")
        
        # 파일 정보 확인
        try:
            stat = os.stat(emp_path)
            print(f"   파일 크기: {stat.st_size} bytes")
            print(f"   수정 날짜: {stat.st_mtime}")
        except Exception as e:
            print(f"   파일 정보 읽기 실패: {e}")
            
    else:
        print("   ✗ EMP 바로가기 파일을 찾을 수 없습니다.")
        
        # 대안 경로 찾기
        print("\n2. 대안 경로 검색:")
        possible_paths = [
            r"C:\Users\jusun\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            r"C:\Users\Public\Desktop",
            r"C:\Users\jusun\Desktop"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"   검색 중: {path}")
                try:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if 'emp' in file.lower() and file.endswith('.appref-ms'):
                                full_path = os.path.join(root, file)
                                print(f"   ✓ 발견: {full_path}")
                except Exception as e:
                    print(f"   검색 오류: {e}")
    
    print("\n3. 실행 중인 EMP 프로세스 확인:")
    found_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                if proc.info['name'] and 'emp' in proc.info['name'].lower():
                    found_processes.append(proc.info)
                elif proc.info['exe'] and 'emp' in proc.info['exe'].lower():
                    found_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        if found_processes:
            print(f"   ✓ {len(found_processes)}개의 EMP 관련 프로세스 발견:")
            for i, proc in enumerate(found_processes, 1):
                print(f"   {i}. PID: {proc['pid']}, 이름: {proc['name']}")
                if proc['exe']:
                    print(f"      실행 파일: {proc['exe']}")
        else:
            print("   ✗ 실행 중인 EMP 프로세스를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"   프로세스 검색 오류: {e}")
    
    print("\n4. ClickOnce 애플리케이션 캐시 확인:")
    clickonce_cache = r"C:\Users\jusun\AppData\Local\Apps\2.0"
    
    if os.path.exists(clickonce_cache):
        print(f"   ClickOnce 캐시 경로: {clickonce_cache}")
        try:
            # EMP 관련 폴더 찾기
            for root, dirs, files in os.walk(clickonce_cache):
                for dir_name in dirs:
                    if 'emp' in dir_name.lower():
                        full_path = os.path.join(root, dir_name)
                        print(f"   ✓ EMP 캐시 폴더: {full_path}")
                        
                for file_name in files:
                    if 'emp' in file_name.lower() and file_name.endswith('.exe'):
                        full_path = os.path.join(root, file_name)
                        print(f"   ✓ EMP 실행 파일: {full_path}")
                        
        except Exception as e:
            print(f"   캐시 검색 오류: {e}")
    else:
        print("   ✗ ClickOnce 캐시 폴더를 찾을 수 없습니다.")
    
    print("\n5. 시작 메뉴 검색:")
    start_menu_paths = [
        r"C:\Users\jusun\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    ]
    
    for start_path in start_menu_paths:
        if os.path.exists(start_path):
            print(f"   검색 중: {start_path}")
            try:
                for root, dirs, files in os.walk(start_path):
                    for file in files:
                        if '난소프트' in file or 'emp' in file.lower():
                            full_path = os.path.join(root, file)
                            print(f"   ✓ 관련 파일: {full_path}")
            except Exception as e:
                print(f"   검색 오류: {e}")

def test_dependencies():
    """필요한 Python 패키지 확인"""
    print("\n" + "=" * 60)
    print("Python 패키지 의존성 확인")
    print("=" * 60)
    
    required_packages = ['psutil', 'pyautogui', 'pywin32', 'Pillow']
    
    for package in required_packages:
        try:
            if package == 'pywin32':
                import win32gui
                print(f"   ✓ {package}: 설치됨")
            elif package == 'Pillow':
                import PIL
                print(f"   ✓ {package}: 설치됨")
            else:
                __import__(package)
                print(f"   ✓ {package}: 설치됨")
        except ImportError:
            print(f"   ✗ {package}: 설치되지 않음")
            print(f"      설치 명령: pip install {package}")

def test_system_info():
    """시스템 정보 확인"""
    print("\n" + "=" * 60)
    print("시스템 정보")
    print("=" * 60)
    
    print(f"   Python 버전: {sys.version}")
    print(f"   운영체제: {os.name}")
    print(f"   현재 작업 디렉토리: {os.getcwd()}")
    print(f"   사용자명: {os.getenv('USERNAME', 'Unknown')}")
    print(f"   컴퓨터명: {os.getenv('COMPUTERNAME', 'Unknown')}")

if __name__ == "__main__":
    try:
        print("EMP 데스크탑 컨트롤러 - 시스템 검사 도구")
        print("이 도구는 EMP 프로그램과 필요한 구성 요소를 확인합니다.\n")
        
        test_system_info()
        test_emp_installation()
        test_dependencies()
        
        print("\n" + "=" * 60)
        print("검사 완료")
        print("=" * 60)
        print("위 정보를 참고하여 문제를 해결하거나 개발자에게 문의하세요.")
        
    except Exception as e:
        print(f"\n시스템 검사 중 오류 발생: {e}")
    
    input("\n엔터를 눌러 종료...")
