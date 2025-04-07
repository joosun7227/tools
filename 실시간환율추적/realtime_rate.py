from selenium import webdriver  # 웹 자동화
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk  # GUI
from tkinter import ttk, messagebox  # 알림창 추가
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time
import threading
import datetime

# 환율 기록 저장 리스트
time_labels = []
kb_rates = []
ibk_rates = []

# ===== 알림 관련 변수 =====
alert_threshold = None  # 기준 환율값
alerted_kb = False  # KB 알림 상태
alerted_ibk = False  # IBK 알림 상태

# 국민은행 환율 가져오는 함수
def fetch_kb_exchange_rate():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://obank.kbstar.com/quics?page=C101423")
    time.sleep(3)

    try:
        element = driver.find_element(By.CSS_SELECTOR, "td.tRight")
        exchange_rate = element.text.replace(",", "")
    except:
        exchange_rate = "0"

    driver.quit()
    return float(exchange_rate)

# 기업은행 환율 가져오는 함수
def fetch_ibk_exchange_rate():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.ibk.co.kr/fxtr/excChangeList.ibk")
    time.sleep(3)

    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "td.ar.last")
        if elements:
            exchange_rate = elements[-1].text.strip().replace(",", "")
        else:
            exchange_rate = "0"
    except:
        exchange_rate = "0"

    driver.quit()
    return float(exchange_rate)

# 그래프 업데이트 함수
def update_graph():
    ax.clear()
    ax.plot(time_labels, kb_rates, label='KB', marker='o', markersize=2)
    ax.plot(time_labels, ibk_rates, label='IBK', marker='o', markersize=2)
    ax.set_title("USD/WON")
    ax.set_ylabel("won")
    ax.set_xlabel("realtime")
    ax.legend()
    ax.grid(True)
    canvas.draw()

# 알림 기준 설정 함수
def set_threshold():
    global alert_threshold, alerted_kb, alerted_ibk
    try:
        value = float(entry.get())
        alert_threshold = value
        alerted_kb = False
        alerted_ibk = False
        messagebox.showinfo("설정 완료", f"{alert_threshold}원 이하로 떨어지면 알림을 줄게!")
    except:
        messagebox.showerror("입력 오류", "숫자로 입력해줘!")

# 데이터 수집 + 알림 + GUI 업데이트 함수
def update_data():
    global alerted_kb, alerted_ibk

    while True:
        kb = fetch_kb_exchange_rate()
        ibk = fetch_ibk_exchange_rate()
        now = datetime.datetime.now().strftime("%M:%S")

        kb_rates.append(kb)
        ibk_rates.append(ibk)
        time_labels.append(now)

        if len(kb_rates) > 30: #30개 까지 표시
            kb_rates.pop(0)
            ibk_rates.pop(0)
            time_labels.pop(0)

        label.config(text=f"💰 KB: {kb}원\n🏦 IBK: {ibk}원")

        # ✅ 알림 기능
        if alert_threshold:
            if kb <= alert_threshold and not alerted_kb:
                messagebox.showwarning("KB 알림", f"💰 KB 환율이 {kb}원으로 떨어졌어!")
                alerted_kb = True
            if ibk <= alert_threshold and not alerted_ibk:
                messagebox.showwarning("IBK 알림", f"🏦 IBK 환율이 {ibk}원으로 떨어졌어!")
                alerted_ibk = True

        update_graph()
        time.sleep(10)

# ========== GUI 구성 ==========
root = tk.Tk()
root.title("실시간환율그래프")
root.geometry("420x300")
root.attributes("-topmost", True)

# 환율 라벨
label = tk.Label(root, text="값 불러오는 중...", font=("Arial", 12))
label.pack(pady=5)

# 기준값 입력 UI
frame = tk.Frame(root)
frame.pack(pady=3)

tk.Label(frame, text="📉 알림 기준 환율:").pack(side="left")
entry = tk.Entry(frame, width=8)
entry.pack(side="left", padx=5)
btn = tk.Button(frame, text="설정", command=set_threshold)
btn.pack(side="left")

# 그래프 영역
fig, ax = plt.subplots(figsize=(3.8, 1.5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# 데이터 쓰레드 시작
thread = threading.Thread(target=update_data, daemon=True)
thread.start()

# GUI 루프 시작
root.mainloop()