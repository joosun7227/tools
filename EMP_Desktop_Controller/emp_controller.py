"""
EMP (Enhanced Management Plus) 데스크탑 컨트롤러
난소프트 EMP 프로그램을 데스크탑에서 자동화 및 제어하는 도구

작성자: 예주나라
작성일: 2025-09-17
"""

import os
import sys
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import pyautogui
import psutil
from datetime import datetime
import json
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emp_controller.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class EMPController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EMP 데스크탑 컨트롤러")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # EMP 프로그램 경로
        self.emp_path = r"C:\Users\jusun\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\EMP - (주)난소프트\EMP - Enhanced Management Plus.appref-ms"
        
        # 설정 파일
        self.config_file = "emp_config.json"
        self.config = self.load_config()
        
        # 프로그램 상태
        self.emp_process = None
        self.is_running = False
        self.automation_thread = None
        
        # GUI 초기화
        self.setup_gui()
        self.update_status()
        
        # 자동 새로고침 타이머
        self.auto_refresh_timer()
        
    def load_config(self):
        """설정 파일 로드"""
        default_config = {
            "auto_start": False,
            "check_interval": 5,
            "window_position": {"x": 100, "y": 100},
            "window_size": {"width": 1200, "height": 800},
            "automation_settings": {
                "auto_login": False,
                "login_delay": 3,
                "auto_refresh": False,
                "refresh_interval": 30
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본값과 병합
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                return default_config
        except Exception as e:
            logging.error(f"설정 파일 로드 실패: {e}")
            return default_config
    
    def save_config(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"설정 파일 저장 실패: {e}")
    
    def setup_gui(self):
        """GUI 인터페이스 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 상태 표시 섹션
        status_frame = ttk.LabelFrame(main_frame, text="EMP 상태", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(status_frame, text="프로그램 상태:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="확인 중...", foreground="orange")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="프로세스 ID:").grid(row=1, column=0, sticky=tk.W)
        self.pid_label = ttk.Label(status_frame, text="N/A")
        self.pid_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 제어 버튼 섹션
        control_frame = ttk.LabelFrame(main_frame, text="프로그램 제어", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="EMP 시작", command=self.start_emp)
        self.start_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="EMP 종료", command=self.stop_emp)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.restart_btn = ttk.Button(control_frame, text="EMP 재시작", command=self.restart_emp)
        self.restart_btn.grid(row=0, column=2, padx=5)
        
        self.refresh_btn = ttk.Button(control_frame, text="상태 새로고침", command=self.update_status)
        self.refresh_btn.grid(row=0, column=3, padx=(5, 0))
        
        # 자동화 섹션
        automation_frame = ttk.LabelFrame(main_frame, text="자동화 기능", padding="5")
        automation_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 자동 로그인
        self.auto_login_var = tk.BooleanVar(value=self.config["automation_settings"]["auto_login"])
        auto_login_check = ttk.Checkbutton(automation_frame, text="자동 로그인", variable=self.auto_login_var, command=self.on_config_change)
        auto_login_check.grid(row=0, column=0, sticky=tk.W)
        
        # 자동 새로고침
        self.auto_refresh_var = tk.BooleanVar(value=self.config["automation_settings"]["auto_refresh"])
        auto_refresh_check = ttk.Checkbutton(automation_frame, text="자동 새로고침", variable=self.auto_refresh_var, command=self.on_config_change)
        auto_refresh_check.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 창 조작 버튼
        window_frame = ttk.LabelFrame(main_frame, text="창 조작", padding="5")
        window_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(window_frame, text="창 최대화", command=self.maximize_window).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(window_frame, text="창 최소화", command=self.minimize_window).grid(row=0, column=1, padx=5)
        ttk.Button(window_frame, text="창 복원", command=self.restore_window).grid(row=0, column=2, padx=5)
        ttk.Button(window_frame, text="창 위치 조정", command=self.adjust_window_position).grid(row=0, column=3, padx=(5, 0))
        
        # 로그 표시 섹션
        log_frame = ttk.LabelFrame(main_frame, text="활동 로그", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 하단 버튼
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(bottom_frame, text="설정", command=self.open_settings).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="로그 지우기", command=self.clear_log).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(bottom_frame, text="종료", command=self.on_closing).pack(side=tk.RIGHT)
        
        # 창 닫기 이벤트 바인딩
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 로그 파일에도 기록
        logging.info(message)
        
    def clear_log(self):
        """로그 창 지우기"""
        self.log_text.delete(1.0, tk.END)
        
    def find_emp_process(self):
        """EMP 프로세스 찾기"""
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] and 'emp' in proc.info['name'].lower():
                    return proc
                if proc.info['exe'] and 'emp' in proc.info['exe'].lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
        
    def update_status(self):
        """상태 업데이트"""
        try:
            process = self.find_emp_process()
            if process:
                self.emp_process = process
                self.is_running = True
                self.status_label.config(text="실행 중", foreground="green")
                self.pid_label.config(text=str(process.pid))
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                self.restart_btn.config(state="normal")
            else:
                self.emp_process = None
                self.is_running = False
                self.status_label.config(text="중지됨", foreground="red")
                self.pid_label.config(text="N/A")
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.restart_btn.config(state="disabled")
        except Exception as e:
            self.log_message(f"상태 업데이트 오류: {e}")
            
    def start_emp(self):
        """EMP 프로그램 시작"""
        try:
            if os.path.exists(self.emp_path):
                self.log_message("EMP 프로그램 시작 중...")
                subprocess.Popen(['cmd', '/c', f'start "" "{self.emp_path}"'], shell=True)
                
                # 잠시 대기 후 상태 업데이트
                self.root.after(3000, self.update_status)
                
                # 자동 로그인이 활성화되어 있으면 실행
                if self.auto_login_var.get():
                    self.root.after(5000, self.perform_auto_login)
                    
            else:
                messagebox.showerror("오류", f"EMP 프로그램을 찾을 수 없습니다:\n{self.emp_path}")
                
        except Exception as e:
            self.log_message(f"EMP 시작 오류: {e}")
            messagebox.showerror("오류", f"EMP 시작 중 오류가 발생했습니다:\n{e}")
            
    def stop_emp(self):
        """EMP 프로그램 종료"""
        try:
            if self.emp_process:
                self.log_message("EMP 프로그램 종료 중...")
                self.emp_process.terminate()
                
                # 강제 종료가 필요한 경우
                try:
                    self.emp_process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    self.emp_process.kill()
                    self.log_message("EMP 프로그램 강제 종료됨")
                
                self.update_status()
            else:
                messagebox.showinfo("정보", "실행 중인 EMP 프로세스를 찾을 수 없습니다.")
                
        except Exception as e:
            self.log_message(f"EMP 종료 오류: {e}")
            messagebox.showerror("오류", f"EMP 종료 중 오류가 발생했습니다:\n{e}")
            
    def restart_emp(self):
        """EMP 프로그램 재시작"""
        self.log_message("EMP 프로그램 재시작 중...")
        self.stop_emp()
        self.root.after(2000, self.start_emp)
        
    def perform_auto_login(self):
        """자동 로그인 수행"""
        try:
            self.log_message("자동 로그인 시도 중...")
            # 여기에 실제 로그인 자동화 코드를 추가
            # 예: 특정 좌표 클릭, 키보드 입력 등
            
            # 예시 코드 (실제 EMP 화면에 맞게 조정 필요)
            time.sleep(2)
            # pyautogui.click(x=400, y=300)  # 로그인 필드 클릭
            # pyautogui.write('username')
            # pyautogui.press('tab')
            # pyautogui.write('password')
            # pyautogui.press('enter')
            
            self.log_message("자동 로그인 완료")
            
        except Exception as e:
            self.log_message(f"자동 로그인 오류: {e}")
            
    def maximize_window(self):
        """창 최대화"""
        try:
            if self.is_running:
                # Windows API를 사용하여 창 최대화
                import win32gui
                import win32con
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if 'emp' in window_title.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    win32gui.ShowWindow(windows[0], win32con.SW_MAXIMIZE)
                    self.log_message("창 최대화 완료")
                else:
                    self.log_message("EMP 창을 찾을 수 없습니다")
            else:
                messagebox.showinfo("정보", "EMP가 실행되고 있지 않습니다.")
                
        except ImportError:
            messagebox.showerror("오류", "pywin32 모듈이 필요합니다.\npip install pywin32")
        except Exception as e:
            self.log_message(f"창 최대화 오류: {e}")
            
    def minimize_window(self):
        """창 최소화"""
        try:
            if self.is_running:
                import win32gui
                import win32con
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if 'emp' in window_title.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    win32gui.ShowWindow(windows[0], win32con.SW_MINIMIZE)
                    self.log_message("창 최소화 완료")
                else:
                    self.log_message("EMP 창을 찾을 수 없습니다")
            else:
                messagebox.showinfo("정보", "EMP가 실행되고 있지 않습니다.")
                
        except ImportError:
            messagebox.showerror("오류", "pywin32 모듈이 필요합니다.\npip install pywin32")
        except Exception as e:
            self.log_message(f"창 최소화 오류: {e}")
            
    def restore_window(self):
        """창 복원"""
        try:
            if self.is_running:
                import win32gui
                import win32con
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if 'emp' in window_title.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    win32gui.ShowWindow(windows[0], win32con.SW_RESTORE)
                    self.log_message("창 복원 완료")
                else:
                    self.log_message("EMP 창을 찾을 수 없습니다")
            else:
                messagebox.showinfo("정보", "EMP가 실행되고 있지 않습니다.")
                
        except ImportError:
            messagebox.showerror("오료", "pywin32 모듈이 필요합니다.\npip install pywin32")
        except Exception as e:
            self.log_message(f"창 복원 오류: {e}")
            
    def adjust_window_position(self):
        """창 위치 조정"""
        try:
            if self.is_running:
                import win32gui
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if 'emp' in window_title.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    # 설정된 위치와 크기로 창 조정
                    x = self.config["window_position"]["x"]
                    y = self.config["window_position"]["y"]
                    width = self.config["window_size"]["width"]
                    height = self.config["window_size"]["height"]
                    
                    win32gui.SetWindowPos(windows[0], 0, x, y, width, height, 0)
                    self.log_message(f"창 위치 조정 완료: ({x}, {y}), 크기: {width}x{height}")
                else:
                    self.log_message("EMP 창을 찾을 수 없습니다")
            else:
                messagebox.showinfo("정보", "EMP가 실행되고 있지 않습니다.")
                
        except ImportError:
            messagebox.showerror("오류", "pywin32 모듈이 필요합니다.\npip install pywin32")
        except Exception as e:
            self.log_message(f"창 위치 조정 오류: {e}")
            
    def auto_refresh_timer(self):
        """자동 새로고침 타이머"""
        if self.auto_refresh_var.get() and self.is_running:
            # 여기에 새로고침 로직 추가
            self.log_message("자동 새로고침 실행")
            
        # 다음 체크 스케줄
        interval = self.config["automation_settings"]["refresh_interval"] * 1000
        self.root.after(interval, self.auto_refresh_timer)
        
    def on_config_change(self):
        """설정 변경 시 호출"""
        self.config["automation_settings"]["auto_login"] = self.auto_login_var.get()
        self.config["automation_settings"]["auto_refresh"] = self.auto_refresh_var.get()
        self.save_config()
        
    def open_settings(self):
        """설정 창 열기"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("설정")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # 설정 UI 구성
        ttk.Label(settings_window, text="창 위치 X:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        x_entry = ttk.Entry(settings_window)
        x_entry.insert(0, str(self.config["window_position"]["x"]))
        x_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(settings_window, text="창 위치 Y:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        y_entry = ttk.Entry(settings_window)
        y_entry.insert(0, str(self.config["window_position"]["y"]))
        y_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(settings_window, text="창 너비:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        width_entry = ttk.Entry(settings_window)
        width_entry.insert(0, str(self.config["window_size"]["width"]))
        width_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(settings_window, text="창 높이:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        height_entry = ttk.Entry(settings_window)
        height_entry.insert(0, str(self.config["window_size"]["height"]))
        height_entry.grid(row=3, column=1, padx=10, pady=5)
        
        def save_settings():
            try:
                self.config["window_position"]["x"] = int(x_entry.get())
                self.config["window_position"]["y"] = int(y_entry.get())
                self.config["window_size"]["width"] = int(width_entry.get())
                self.config["window_size"]["height"] = int(height_entry.get())
                self.save_config()
                messagebox.showinfo("성공", "설정이 저장되었습니다.")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("오류", "숫자만 입력해주세요.")
        
        ttk.Button(settings_window, text="저장", command=save_settings).grid(row=4, column=0, columnspan=2, pady=20)
        
    def on_closing(self):
        """프로그램 종료 시 호출"""
        self.save_config()
        self.root.destroy()
        
    def run(self):
        """프로그램 실행"""
        self.log_message("EMP 데스크탑 컨트롤러 시작")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        controller = EMPController()
        controller.run()
    except Exception as e:
        print(f"프로그램 실행 오류: {e}")
        input("엔터를 눌러 종료...")
