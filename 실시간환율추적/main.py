from selenium import webdriver  # 웹브라우저 자동 제어 도구
from selenium.webdriver.common.by import By  # HTML 요소 탐색 도구
from selenium.webdriver.chrome.service import Service  # 크롬 드라이버 서비스
from webdriver_manager.chrome import ChromeDriverManager  # 크롬 드라이버 자동 설치
import tkinter as tk  # GUI 생성 도구
import time  # 시간 관련 기능

# 국민은행 환율 가져오는 함수
def fetch_kb_exchange_rate():
    service = Service(ChromeDriverManager().install())  # 크롬 드라이버 서비스 설정
    options = webdriver.ChromeOptions()  # 크롬 옵션 설정
    options.add_argument("headless")  # 브라우저 창 안 띄우고 실행
    driver = webdriver.Chrome(service=service, options=options)  # 드라이버 실행

    driver.get("https://obank.kbstar.com/quics?page=C101423")  # 국민은행 환율 페이지 접속
    time.sleep(3)  # 페이지 로딩 대기

    try:
        element = driver.find_element(By.CSS_SELECTOR, "td.tRight")  # 첫 번째 환율 요소 찾기
        exchange_rate = element.text  # 텍스트 추출
    except Exception as e:
        exchange_rate = "불러오기 실패"  # 에러 시 메시지 처리

    driver.quit()  # 브라우저 종료
    return exchange_rate  # 환율 반환

# 기업은행 환율 가져오는 함수 (맨 마지막 매매기준율만 가져오기)
def fetch_ibk_exchange_rate():
    service = Service(ChromeDriverManager().install())  # 크롬 드라이버 서비스 설정
    options = webdriver.ChromeOptions()  # 크롬 옵션 설정
    options.add_argument("headless")  # 브라우저 창 없이 실행
    driver = webdriver.Chrome(service=service, options=options)  # 드라이버 실행

    driver.get("https://www.ibk.co.kr/fxtr/excChangeList.ibk")  # 기업은행 환율 페이지 접속
    time.sleep(3)  # 페이지 로딩 대기

    try:
        # class가 'ar last'인 모든 td 요소 찾기 (매매기준율 값들)
        elements = driver.find_elements(By.CSS_SELECTOR, "td.ar.last")

        if elements:
            exchange_rate = elements[-1].text.strip()  # 제일 마지막 값을 추출
        else:
            exchange_rate = "값 없음"  # 값이 없는 경우
    except Exception as e:
        exchange_rate = "불러오기 실패"  # 에러 처리

    driver.quit()  # 브라우저 종료
    return exchange_rate  # 환율 반환

# GUI 라벨 업데이트 함수
def update_gui():
    kb_rate = fetch_kb_exchange_rate()  # 국민은행 환율 가져오기
    ibk_rate = fetch_ibk_exchange_rate()  # 기업은행 환율 가져오기

    # GUI 라벨에 표시할 텍스트 설정
    label.config(text=f"💰 KB 환율: {kb_rate}원\n🏦 IBK 환율: {ibk_rate}원")
    root.after(10000, update_gui)  # 10초마다 업데이트 반복

# GUI 창 설정
root = tk.Tk()
root.title("은행별 환율 실시간 확인")  # 창 제목
root.geometry("260x100")  # 창 크기 설정
root.attributes("-topmost", True)  # 항상 맨 앞에 창 고정

# 라벨 생성 및 배치
label = tk.Label(root, text="값 불러오는 중...", font=("Arial", 14))
label.pack(pady=15)  # 위쪽 여백

# 프로그램 시작 시 첫 환율 불러오기
update_gui()

# GUI 이벤트 루프 실행
root.mainloop()