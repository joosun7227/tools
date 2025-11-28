import tkinter as tk  # GUI(창)를 만들기 위한 tkinter 모듈을 가져옴
from tkinter import messagebox  # 알림창을 띄우기 위한 messagebox 모듈을 가져옴
from datetime import datetime  # 현재 시간(시/분/초)을 가져오기 위해 datetime 모듈에서 datetime 클래스를 가져옴
from math import sin, cos, pi  # 삼각함수(원 위에 바늘 좌표 계산용)와 pi(원주율)를 사용하기 위해 가져옴

WORK_MIN = 55  # 집중 시간(분)을 55분으로 설정
BREAK_MIN = 5  # 휴식 시간(분)을 5분으로 설정

WORK_SEC = WORK_MIN * 60  # 집중 시간을 초 단위로 변환 (50분 * 60초)
BREAK_SEC = BREAK_MIN * 60  # 휴식 시간을 초 단위로 변환 (10분 * 60초)

current_mode = None  # 현재 모드를 저장하는 변수 (None = 대기, "work" = 집중, "break" = 휴식)
remaining_seconds = 0  # 뽀모도로 타이머에서 현재 남아 있는 시간을 초 단위로 저장하는 변수
timer_id = None  # 뽀모도로 타이머에 사용되는 after() 함수의 ID를 저장하는 변수 (취소할 때 필요)
is_paused = False  # 현재 타이머가 일시정지 상태인지 아닌지 저장하는 변수 (True = 멈춤)

clock_radius = 120  # 아날로그 시계의 반지름 기본값을 120으로 설정
canvas_size = clock_radius * 2 + 40  # 시계를 그릴 캔버스의 전체 크기(가로, 세로)를 계산 (여유 40픽셀)
clock_center_x = canvas_size // 2  # 시계 중심의 x좌표 (가로의 중앙)
clock_center_y = canvas_size // 2  # 시계 중심의 y좌표 (세로의 중앙)


def format_time(seconds):  # 초 단위 시간을 "MM:SS" 문자열로 바꿔주는 함수 정의
    minutes = seconds // 60  # 전체 초에서 60으로 나눠 분 단위를 구함
    sec = seconds % 60  # 나머지로 초 단위를 구함
    return f"{minutes:02d}:{sec:02d}"  # 두 자리 숫자로 0 채우기 해서 "MM:SS" 형태 문자열로 반환


def update_labels():  # 현재 모드와 남은 시간을 화면 라벨에 반영하는 함수 정의
    if current_mode is None:  # 아직 모드가 설정되지 않은 대기 상태라면
        mode_text = "대기 중"  # 모드 라벨에 "대기 중" 이라고 표시
        time_text = "00:00"  # 남은 시간 라벨에는 "00:00" 표시
        bg_color = "#222222"  # 배경색은 어두운 회색으로 설정
    elif current_mode == "work":  # 현재 모드가 집중 모드라면
        mode_text = "⏰ 집중 시간"  # 모드 라벨에 "집중 시간" 텍스트를 표시
        time_text = format_time(remaining_seconds)  # 남은 시간을 "MM:SS" 형식으로 표시
        bg_color = "#000f64"  # 집중 모드 배경색은 파란색 계열로 지정
    else:  # 그 외의 경우는 휴식 모드라고 간주 ("break")
        mode_text = "😌 휴식 시간"  # 모드 라벨에 "휴식 시간" 텍스트를 표시
        time_text = format_time(remaining_seconds)  # 남은 시간을 "MM:SS" 형식으로 표시
        bg_color = "#227900"  # 휴식 모드 배경색은 초록/민트 계열로 지정

    root.configure(bg=bg_color)  # 메인 창의 배경색을 현재 모드에 맞는 색으로 설정
    mode_label.config(text=mode_text, bg=bg_color)  # 모드 라벨에 텍스트와 배경색 적용
    timer_label.config(text=f"남은 뽀모도로 시간: {time_text}", bg=bg_color)  # 뽀모도로 남은 시간 라벨 업데이트
    current_time_label.config(bg=bg_color)  # 현재 시간 라벨의 배경색도 동일하게 설정
    button_frame.config(bg=bg_color)  # 버튼들이 들어있는 프레임 배경색도 변경
    size_frame.config(bg=bg_color)  # 시계 크기 조절 슬라이더가 있는 프레임 배경색도 변경
    clock_canvas.config(bg=bg_color)  # 시계를 그리는 캔버스의 배경색도 변경


def draw_clock_face():  # 시계의 테두리와 눈금을 그리는 함수 정의
    clock_canvas.delete("face")  # 기존에 "face" 태그로 그려진 도형들을 모두 삭제 (초기화)
    r = clock_radius  # 반지름 변수를 사용하기 쉽게 r로 가져옴

    # 시계 테두리 원 그리기
    clock_canvas.create_oval(  # 원(시계 테두리)를 그림
        clock_center_x - r,  # 왼쪽 x 좌표 = 중심 x - 반지름
        clock_center_y - r,  # 위쪽 y 좌표 = 중심 y - 반지름
        clock_center_x + r,  # 오른쪽 x 좌표 = 중심 x + 반지름
        clock_center_y + r,  # 아래쪽 y 좌표 = 중심 y + 반지름
        outline="white",  # 테두리 색깔을 흰색으로 설정
        width=3,  # 테두리 선 두께를 3으로 설정
        fill="#111111",  # 시계 안쪽 배경색을 어두운 색으로 채움
        tags="face"  # 나중에 지울 수 있도록 "face" 태그를 붙임
    )

    # 12개의 시각 눈금(1~12시 위치)에 짧은 선 그리기
    for i in range(12):  # 0부터 11까지 반복 (12개 눈금)
        angle_deg = i * 30  # 각도(도 단위) = 시각 * 30도 (360도 / 12시간)
        angle_rad = (angle_deg - 90) * pi / 180  # 0도 기준을 위쪽(12시 방향)으로 맞추기 위해 -90도 하고 라디안으로 변환

        inner_r = r - 15  # 눈금 시작점 반지름 (원 안쪽으로 15만큼 들어간 위치)
        outer_r = r - 5  # 눈금 끝점 반지름 (원 안쪽으로 5만큼 들어간 위치)

        x1 = clock_center_x + inner_r * cos(angle_rad)  # 시작점 x좌표 = 중심 x + inner_r * cos(각도)
        y1 = clock_center_y + inner_r * sin(angle_rad)  # 시작점 y좌표 = 중심 y + inner_r * sin(각도)
        x2 = clock_center_x + outer_r * cos(angle_rad)  # 끝점 x좌표 = 중심 x + outer_r * cos(각도)
        y2 = clock_center_y + outer_r * sin(angle_rad)  # 끝점 y좌표 = 중심 y + outer_r * sin(각도)

        clock_canvas.create_line(  # 눈금 선을 그림
            x1, y1, x2, y2,  # 선의 시작점(x1,y1)과 끝점(x2,y2)
            fill="white",  # 선 색깔은 흰색
            width=2,  # 선 두께는 2
            tags="face"  # "face" 태그를 붙여 나중에 전체를 한 번에 지울 수 있게 함
        )


def update_clock():  # 아날로그 시계(현재 시간 바늘)를 계속 업데이트하는 함수 정의
    now = datetime.now()  # 현재 날짜와 시간을 가져옴
    hour = now.hour % 12  # 24시간 형식에서 12시간 형식으로 바꾸기 위해 12로 나눈 나머지 사용
    minute = now.minute  # 현재 분을 가져옴
    second = now.second  # 현재 초를 가져옴

    current_time_label.config(text=f"현재 시각: {now.strftime('%H:%M:%S')}")  # "현재 시각: HH:MM:SS" 형태로 라벨에 표시

    clock_canvas.delete("hands")  # 이전에 그려진 시계 바늘들을 모두 삭제 ("hands" 태그를 가진 것들 삭제)

    r = clock_radius  # 현재 설정된 시계 반지름을 r 변수로 가져옴

    # 시침(시간 바늘) 각도 계산 (시간 + 분 비율을 포함해서 부드럽게 이동)
    hour_angle = ((hour + minute / 60) * 30) - 90  # 한 시간당 30도, 기준을 위쪽(12시)으로 맞추기 위해 -90도
    hour_rad = hour_angle * pi / 180  # 도(degree)를 라디안(radian)으로 변환

    # 분침(분 바늘) 각도 계산
    minute_angle = (minute * 6) - 90  # 한 분당 6도(360/60), 기준 위쪽으로 맞추기 위해 -90도
    minute_rad = minute_angle * pi / 180  # 라디안으로 변환

    # 초침(초 바늘) 각도 계산
    second_angle = (second * 6) - 90  # 한 초당 6도, 기준 위쪽으로 맞추기 위해 -90도
    second_rad = second_angle * pi / 180  # 라디안으로 변환

    # 시침(길이: 반지름의 약 55%) 끝점 좌표 계산
    hx = clock_center_x + (r * 0.55) * cos(hour_rad)  # 시침 끝점의 x좌표 계산
    hy = clock_center_y + (r * 0.55) * sin(hour_rad)  # 시침 끝점의 y좌표 계산

    # 분침(길이: 반지름의 약 75%) 끝점 좌표 계산
    mx = clock_center_x + (r * 0.75) * cos(minute_rad)  # 분침 끝점의 x좌표 계산
    my = clock_center_y + (r * 0.75) * sin(minute_rad)  # 분침 끝점의 y좌표 계산

    # 초침(길이: 반지름의 약 85%) 끝점 좌표 계산
    sx = clock_center_x + (r * 0.85) * cos(second_rad)  # 초침 끝점의 x좌표 계산
    sy = clock_center_y + (r * 0.85) * sin(second_rad)  # 초침 끝점의 y좌표 계산

    # 시침 그리기
    clock_canvas.create_line(
        clock_center_x, clock_center_y,  # 선 시작점: 시계 중심
        hx, hy,  # 선 끝점: 시침 끝 좌표
        fill="white",  # 시침 색깔은 흰색
        width=4,  # 시침 두께는 4
        capstyle=tk.ROUND,  # 선 끝 모양을 둥글게 설정
        tags="hands"  # "hands" 태그를 붙여 나중에 지우기 쉽게 함
    )

    # 분침 그리기
    clock_canvas.create_line(
        clock_center_x, clock_center_y,  # 시작점: 시계 중심
        mx, my,  # 끝점: 분침 끝 좌표
        fill="white",  # 분침 색깔은 흰색
        width=3,  # 분침 두께는 3
        capstyle=tk.ROUND,  # 끝을 둥글게 설정
        tags="hands"  # "hands" 태그 붙이기
    )

    # 초침 그리기
    clock_canvas.create_line(
        clock_center_x, clock_center_y,  # 시작점: 시계 중심
        sx, sy,  # 끝점: 초침 끝 좌표
        fill="red",  # 초침 색깔은 빨간색으로 강조
        width=2,  # 초침 두께는 2
        capstyle=tk.ROUND,  # 끝을 둥글게 설정
        tags="hands"  # "hands" 태그 붙이기
    )

    # 시계 중심에 작은 원(축) 그리기
    clock_canvas.create_oval(
        clock_center_x - 5, clock_center_y - 5,  # 작은 원의 왼쪽 위 좌표
        clock_center_x + 5, clock_center_y + 5,  # 작은 원의 오른쪽 아래 좌표
        fill="white",  # 안을 흰색으로 채움
        outline="white",  # 테두리도 흰색
        tags="hands"  # 이것도 "hands" 태그를 붙여서 같이 갱신되게 함
    )

    root.after(1000, update_clock)  # 1초(1000ms) 후에 다시 update_clock 함수를 호출해서 계속 갱신되게 함


def update_clock_face_size():  # 시계 크기가 변경될 때 캔버스와 시계 얼굴을 다시 그리는 함수 정의
    global canvas_size, clock_center_x, clock_center_y  # 전역 변수들을 수정한다고 선언
    canvas_size = clock_radius * 2 + 40  # 캔버스의 크기를 반지름 기반으로 다시 계산
    clock_center_x = canvas_size // 2  # 시계 중심 x좌표를 캔버스 중앙으로 재설정
    clock_center_y = canvas_size // 2  # 시계 중심 y좌표를 캔버스 중앙으로 재설정
    clock_canvas.config(width=canvas_size, height=canvas_size)  # 캔버스 크기를 새 값으로 변경
    draw_clock_face()  # 새로운 크기에 맞게 시계 얼굴(원과 눈금)을 다시 그림


def on_size_change(value):  # 슬라이더(Scale)가 움직일 때 호출되는 콜백 함수 정의
    global clock_radius  # 전역 변수 clock_radius를 수정한다고 선언
    clock_radius = int(float(value))  # 슬라이더에서 넘어온 문자열 값을 정수로 변환해서 반지름으로 사용
    update_clock_face_size()  # 반지름이 바뀌었으니 시계 크기를 다시 그리도록 함수 호출


def change_mode(new_mode):  # 모드를 변경하고 알림을 띄우는 함수 정의
    global current_mode, remaining_seconds, is_paused  # 전역 변수들을 수정한다고 선언
    current_mode = new_mode  # 현재 모드를 전달받은 모드로 변경
    is_paused = False  # 모드가 변경될 때는 일시정지 상태를 해제해 둠

    if new_mode == "work":  # 새 모드가 집중 모드라면
        remaining_seconds = WORK_SEC  # 남은 시간을 50분(초 단위)로 설정
        update_labels()  # 화면 라벨들을 갱신
        messagebox.showinfo("알림", "집중 모드로 전환됐어! 50분 집중 시작 ✨")  # 알림창 띄우기
    elif new_mode == "break":  # 새 모드가 휴식 모드라면
        remaining_seconds = BREAK_SEC  # 남은 시간을 10분(초 단위)로 설정
        update_labels()  # 화면 라벨 갱신
        messagebox.showinfo("알림", "휴식 모드로 전환됐어! 10분 편하게 쉬자 😌")  # 알림창 띄우기
    elif new_mode is None:  # 새 모드가 대기 상태(None)라면
        remaining_seconds = 0  # 남은 시간을 0으로 초기화
        update_labels()  # 화면 라벨 갱신
        messagebox.showinfo("알림", "대기 모드로 돌아왔어. 언제든 다시 시작해도 돼 😊")  # 알림창 띄우기
    else:  # 혹시 다른 값이 들어오는 경우를 대비한 기본 처리 (현재는 사용 안 함)
        update_labels()  # 그냥 라벨만 갱신


def countdown():  # 뽀모도로 타이머가 1초씩 줄어들도록 동작하는 함수 정의
    global remaining_seconds, timer_id  # 전역 변수를 사용한다고 선언
    update_labels()  # 현재 남은 시간과 모드에 맞게 라벨을 갱신

    if is_paused:  # 만약 현재가 일시정지 상태라면
        return  # 더 이상 타이머를 진행하지 않고 함수 종료

    if remaining_seconds > 0:  # 남은 시간이 0보다 크다면
        remaining_seconds -= 1  # 남은 시간을 1초 줄임
        timer_id = root.after(1000, countdown)  # 1초 후에 countdown 함수를 다시 호출하도록 예약
    else:  # 남은 시간이 0이 된 경우 (해당 모드가 끝난 경우)
        if current_mode == "work":  # 지금까지가 집중 모드였다면
            change_mode("break")  # 휴식 모드로 전환 (알림 포함)
        elif current_mode == "break":  # 지금까지가 휴식 모드였다면
            change_mode("work")  # 다시 집중 모드로 전환 (알림 포함)
        # 모드가 바뀐 뒤에 다시 타이머를 시작해 줘야 하므로
        timer_id = root.after(1000, countdown)  # 1초 후에 countdown 다시 실행 예약


def start_or_resume():  # 시작 / 재시작 버튼이 눌렸을 때 실행되는 함수 정의
    global timer_id, is_paused  # 전역 변수 사용한다고 선언
    if current_mode is None:  # 아직 한 번도 시작하지 않은 대기 상태라면
        change_mode("work")  # 집중 모드로 전환하면서 알림도 띄움
    else:  # 이미 한 번은 시작한 상태라면
        is_paused = False  # 일시정지 상태를 해제
        update_labels()  # 라벨을 한 번 갱신

    if timer_id is not None:  # 기존에 동작 중이던 타이머가 있다면
        root.after_cancel(timer_id)  # 그 타이머를 먼저 취소해서 중복 실행을 막음

    timer_id = root.after(1000, countdown)  # 1초 후에 countdown 함수를 실행하도록 예약


def pause_timer():  # 일시정지 버튼이 눌렸을 때 실행되는 함수 정의
    global is_paused, timer_id  # 전역 변수 사용 선언
    is_paused = True  # 일시정지 상태로 변경
    if timer_id is not None:  # 타이머가 예약되어 있다면
        root.after_cancel(timer_id)  # 예약된 타이머를 취소해서 카운트를 멈춤
        timer_id = None  # 타이머 ID를 None으로 초기화해서 더 이상 동작 중이 아님을 표시


def reset_timer():  # 초기화 버튼이 눌렸을 때 실행되는 함수 정의
    global current_mode, remaining_seconds, is_paused, timer_id  # 전역 변수 사용 선언
    if timer_id is not None:  # 만약 타이머가 동작 중이었다면
        root.after_cancel(timer_id)  # 타이머를 취소해서 완전히 정지
        timer_id = None  # 타이머 ID를 초기화

    current_mode = None  # 모드를 대기 상태(None)로 설정
    remaining_seconds = 0  # 남은 시간을 0초로 설정
    is_paused = False  # 일시정지 상태도 해제
    change_mode(None)  # 모드를 None으로 변경하면서 대기 모드 알림도 띄우고 라벨 갱신


# ----------------- 여기서부터는 실제 창(UI) 만드는 부분 -----------------

root = tk.Tk()  # 메인 창(윈도우) 객체를 생성
root.title("뽀모도로 타이머 (아날로그 시계)")  # 창의 제목을 설정
root.geometry("450x520")  # 창의 기본 크기를 가로 450, 세로 520으로 설정
root.resizable(True, True)  # 창 크기를 사용자가 조절할 수 있도록 허용
root.configure(bg="#222222")  # 기본 배경색을 어두운 회색으로 설정

mode_label = tk.Label(  # 현재 모드를 보여주는 라벨 생성
    root,  # 부모 위젯은 메인 창
    text="대기 중",  # 초기 텍스트는 "대기 중"
    font=("맑은 고딕", 18, "bold"),  # 글꼴은 맑은 고딕, 크기 18, 굵게
    bg="#222222",  # 배경색은 메인 배경과 같은 색
    fg="white"  # 글자색은 흰색
)
mode_label.pack(pady=10)  # 라벨을 위에서부터 배치하고 위아래로 10픽셀의 여백을 둠

current_time_label = tk.Label(  # 현재 시각(HH:MM:SS)을 보여줄 라벨 생성
    root,  # 부모 위젯은 메인 창
    text="현재 시각: --:--:--",  # 초기 텍스트
    font=("Consolas", 14),  # 글꼴은 Consolas, 크기 14
    bg="#222222",  # 배경색은 메인 배경과 동일
    fg="white"  # 글자색은 흰색
)
current_time_label.pack(pady=5)  # 라벨을 배치하고 위아래로 5픽셀 여백을 둠

clock_canvas = tk.Canvas(  # 아날로그 시계를 그릴 캔버스 생성
    root,  # 부모 위젯은 메인 창
    width=canvas_size,  # 캔버스 가로 크기를 미리 계산된 값으로 설정
    height=canvas_size,  # 캔버스 세로 크기를 미리 계산된 값으로 설정
    bg="#222222",  # 캔버스 배경색도 메인 배경색과 동일
    highlightthickness=0  # 캔버스 외곽선(테두리) 두께를 0으로 해서 테두리를 안 보이게 함
)
clock_canvas.pack(pady=10)  # 캔버스를 배치하고 위아래로 10픽셀 여백을 둠

timer_label = tk.Label(  # 뽀모도로 남은 시간을 보여줄 라벨 생성
    root,  # 부모 위젯은 메인 창
    text="남은 뽀모도로 시간: 00:00",  # 초기 텍스트
    font=("맑은 고딕", 14),  # 글꼴은 맑은 고딕, 크기 14
    bg="#222222",  # 배경색은 메인 배경색과 동일
    fg="white"  # 글자색은 흰색
)
timer_label.pack(pady=5)  # 라벨 배치 후 위아래 여백 5픽셀

button_frame = tk.Frame(root, bg="#222222")  # 시작/일시정지/초기화 버튼들을 담을 프레임 생성
button_frame.pack(pady=10)  # 프레임을 배치하고 위아래로 10픽셀 여백을 둠

start_button = tk.Button(  # 시작 / 재시작 버튼 생성
    button_frame,  # 부모는 버튼 프레임
    text="▶ 시작 / 재시작",  # 버튼에 표시될 텍스트
    command=start_or_resume,  # 버튼을 눌렀을 때 실행될 함수 지정
    width=14,  # 버튼 가로 크기
    height=2  # 버튼 세로 크기
)
start_button.grid(row=0, column=0, padx=5)  # 프레임 안에서 그리드(0행 0열)에 배치, 좌우 여백 5픽셀

pause_button = tk.Button(  # 일시정지 버튼 생성
    button_frame,  # 부모는 버튼 프레임
    text="⏸ 일시정지",  # 버튼에 표시될 텍스트
    command=pause_timer,  # 버튼 눌렀을 때 실행될 함수 지정
    width=14,  # 버튼 가로 크기
    height=2  # 버튼 세로 크기
)
pause_button.grid(row=0, column=1, padx=5)  # 0행 1열에 배치, 좌우 여백 5픽셀

reset_button = tk.Button(  # 초기화 버튼 생성
    button_frame,  # 부모는 버튼 프레임
    text="🔁 초기화",  # 버튼 텍스트
    command=reset_timer,  # 버튼 눌렀을 때 실행될 함수 지정
    width=14,  # 가로 크기
    height=2  # 세로 크기
)
reset_button.grid(row=0, column=2, padx=5)  # 0행 2열에 배치, 좌우 여백 5픽셀

size_frame = tk.Frame(root, bg="#222222")  # 시계 크기 조절 슬라이더를 담을 프레임 생성
size_frame.pack(pady=10)  # 프레임 배치하고 위아래 여백 10픽셀

size_label = tk.Label(  # 시계 크기 설명 라벨 생성
    size_frame,  # 부모는 시계 크기 프레임
    text="시계 크기 조절",  # 라벨에 표시될 텍스트
    font=("맑은 고딕", 12),  # 글꼴과 크기 설정
    bg="#222222",  # 배경색
    fg="white"  # 글자색
)
size_label.pack(side="left", padx=5)  # 왼쪽에 배치하고 좌우 여백 5픽셀

size_scale = tk.Scale(  # 시계 크기를 조절할 슬라이더(Scale) 위젯 생성
    size_frame,  # 부모는 시계 크기 프레임
    from_=80,  # 최소 반지름 값 80
    to=200,  # 최대 반지름 값 200
    orient="horizontal",  # 슬라이더 방향은 가로
    length=200,  # 슬라이더 전체 길이
    command=on_size_change,  # 값이 바뀔 때마다 호출될 함수 지정
    bg="#222222",  # 배경색
    fg="white",  # 글자색
    highlightthickness=0,  # 포커스 테두리 두께 0으로 설정
    troughcolor="#444444"  # 슬라이더 홈 색깔을 약간 밝은 회색으로 설정
)
size_scale.set(clock_radius)  # 슬라이더 초기값을 현재 반지름 값으로 설정
size_scale.pack(side="left", padx=5)  # 슬라이더를 라벨 옆에 배치하고 좌우 여백 5픽셀

draw_clock_face()  # 처음 실행 시 시계 얼굴(원과 눈금)을 한 번 그림
update_labels()  # 처음 라벨 상태(대기 모드)를 화면에 반영
update_clock()  # 현재 시간을 기반으로 아날로그 시계를 업데이트하는 루프를 시작

root.mainloop()  # tkinter 이벤트 루프 시작 (창을 계속 표시하고 사용자 입력을 받는 부분)
