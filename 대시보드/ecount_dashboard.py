# 대시보드 폴더에서
# 가상환경 dash
# .\dash\Scripts\Activate 가상환경 접속


# 📁 파일명: ecount_dashboard.py

import streamlit as st         # Streamlit UI
import pandas as pd            # 데이터프레임 처리
import requests                # API 요청
import datetime                # 날짜 계산
import altair as alt           # 차트 시각화

# ✅ 이카운트 API 키
API_KEY = "3ec38855d98c84e6fa1b92a612b58c5474"

# ✅ 이카운트 일자별 매출 데이터 불러오기 함수
def get_sales_data(start_date, end_date):
    # 이카운트 테스트 API URL
    url = "https://sboapi.ecount.com/ECERP/OAPI/OAPIView"

    # 요청 파라미터 세팅
    params = {
        "KEY": API_KEY,                           # 발급받은 API 키
        "SERVICE": "Sales/TransactionList",       # 매출 내역 서비스
        "LANG": "ko-KR",                          # 언어
        "Start_Date": start_date.strftime("%Y%m%d"),  # 시작일
        "End_Date": end_date.strftime("%Y%m%d")       # 종료일
    }

    try:
        # API 요청
        response = requests.get(url, params=params)
        data = response.json()

        # 결과 리스트 추출
        rows = data.get("list", [])

        # 리스트가 없거나 비었으면 빈 데이터프레임 반환
        if not rows:
            return pd.DataFrame()

        # 데이터프레임으로 변환
        df = pd.DataFrame(rows)

        # 날짜, 금액 컬럼 이름이 맞는지 확인 후 변환
        df["일자"] = pd.to_datetime(df["TR_DATE"], format="%Y%m%d")   # 일자 변환
        df["매출"] = df["TOT_SALE_AMT"].astype(float)                # 매출금액 변환

        return df[["일자", "매출"]]  # 필요한 컬럼만 반환

    except Exception as e:
        st.error(f"❌ API 오류 발생: {e}")
        return pd.DataFrame()

# ✅ Streamlit 대시보드 UI 설정
st.set_page_config(page_title="예주나라 매출 대시보드", layout="wide")
st.title("📊 예주나라 일자별 매출 대시보드")

# 날짜 입력 UI
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("조회 시작일", value=datetime.date.today() - datetime.timedelta(days=7))
with col2:
    end_date = st.date_input("조회 종료일", value=datetime.date.today())

# 버튼 눌렀을 때 데이터 조회
if st.button("📥 매출 데이터 조회"):
    with st.spinner("잠시만 기다려줘... 데이터 불러오는 중..."):
        sales_df = get_sales_data(start_date, end_date)

        # 데이터가 없을 경우
        if sales_df.empty:
            st.warning("데이터가 없거나 불러오는 데 실패했어.")
        else:
            st.success("✅ 매출 데이터 불러오기 성공!")

            # 일자별 합산
            daily_sales = sales_df.groupby("일자")["매출"].sum().reset_index()

            # 📈 Altair로 그래프 그리기
            chart = alt.Chart(daily_sales).mark_line(point=True).encode(
                x="일자:T",
                y="매출:Q",
                tooltip=["일자", "매출"]
            ).properties(
                title="🗓️ 일자별 매출 그래프",
                width=800,
                height=400
            )

            # 시각화 및 표 출력
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(daily_sales)