[바코드 스캐너 매칭 프로그램 사용법]
해당폴더 위치까지 와서 py파일을 실행시켜야 합니다!


1) master_template.xlsx를 열어 '품목코드/품목명/단위/바코드'를 회사 기준으로 채우세요.
   - '실제바코드'는 비워두세요. (스캔 중 자동으로 채워집니다)

2) Python 3.9+ 환경에 필요한 패키지 설치:
   pip install -r requirements.txt

3) 프로그램 실행:
   python barcode_checker.py

4) 사용 흐름:
   - '바코드 입력' 칸에 스캐너로 바코드를 찍으면 자동 입력됩니다.
   - 등록바코드 또는 실제바코드 중 하나라도 일치하면 '일치'로 기록되고
     품목명/단위/바코드번호가 화면에 뜹니다.
   - 일치하지 않으면 검색창이 뜨고, 품목을 선택하면 해당 품목의 '실제바코드'에
     스캔된 번호가 저장됩니다.
   - 30건마다 자동 저장됩니다. (메뉴 → 지금저장 수동저장도 가능)

5) 생성/업데이트 파일:
   - master_updated.xlsx : 실제바코드 컬럼이 업데이트된 기준표
   - scan_log.xlsx       : 스캔 이력 (시간, 바코드, 결과, 품목코드/명)

6) EXE 만들기(선택):
   pip install pyinstaller
   pyinstaller --onefile barcode_checker.py
