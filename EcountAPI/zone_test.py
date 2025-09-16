"""
Zone 조회 테스트
Ecount ERP API의 Zone 정보를 조회합니다.

Zone이란? 
- Ecount ERP에서 회사별로 할당된 서버 영역을 의미합니다
- Zone 정보를 먼저 조회해야 올바른 API 서버에 접속할 수 있습니다
- 예: Zone "AA"이면 실제 API는 oapiAA.ecount.com을 사용합니다
"""
import requests  # HTTP 요청을 보내기 위한 라이브러리

def test_zone():
    print("=== Zone 조회 테스트 ===")
    
    # 1. API 엔드포인트 URL 설정
    # 이 URL은 모든 회사의 Zone 정보를 조회하는 공통 엔드포인트입니다
    url = "http://sboapi.ecount.com/OAPI/V2/Zone"
    
    # 2. 요청할 데이터 준비
    # COM_CODE: 회사 코드 (예주나라의 고유 식별자)
    data = {"COM_CODE": "665496"}
    
    try:
        # 3. HTTP POST 요청 전송
        # requests.post()로 POST 방식으로 데이터를 전송합니다
        # json=data: 데이터를 JSON 형태로 변환해서 전송
        # headers: HTTP 헤더에 Content-Type을 application/json으로 설정
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        # 4. 응답 상태 코드 확인
        # 200: 성공, 404: 페이지 없음, 500: 서버 오류 등
        print(f"응답 상태 코드: {response.status_code}")
        
        # 5. 응답 내용 출력 (디버깅용)
        # response.text: 서버에서 받은 응답을 텍스트로 변환
        print(f"응답 내용: {response.text}")
        
        # 6. HTTP 상태 코드가 200(성공)인지 확인
        if response.status_code == 200:
            # 7. JSON 응답을 Python 딕셔너리로 변환
            # response.json(): JSON 문자열을 Python 객체로 변환
            result = response.json()
            
            # 8. API 응답의 Status 필드가 "200"인지 확인
            # Ecount API는 HTTP 상태코드와 별도로 자체 Status 필드를 사용합니다
            if result.get('Status') == '200':
                # 9. Zone 정보 추출
                # result['Data']['ZONE']에서 Zone 값을 가져옵니다
                # get() 메서드로 안전하게 접근 (키가 없으면 기본값 반환)
                zone = result.get('Data', {}).get('ZONE', 'Unknown')
                print(f"✅ Zone 조회 성공: {zone}")
                return zone  # Zone 값을 반환
            else:
                print("❌ Zone 조회 실패")
                return None
        else:
            print("❌ 요청 실패")
            return None
            
    except Exception as e:
        # 10. 예외 처리
        # 네트워크 오류, JSON 파싱 오류 등을 처리합니다
        print(f"❌ 오류 발생: {e}")
        return None

# 11. 스크립트가 직접 실행될 때만 test_zone() 함수를 호출
# 다른 파일에서 import할 때는 실행되지 않습니다
if __name__ == "__main__":
    test_zone()
