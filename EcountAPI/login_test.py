"""
로그인 테스트
Ecount ERP API 로그인을 테스트합니다.

로그인이란?
- API를 사용하기 위해 인증을 받는 과정입니다
- 성공하면 세션 토큰(SESSION_TOKEN)을 받아서 다른 API를 호출할 수 있습니다
- 테스트용 인증키로는 제한적인 기능만 사용 가능합니다
"""
import requests  # HTTP 요청을 보내기 위한 라이브러리

def test_login():
    print("=== 로그인 테스트 ===")
    
    # 1. 로그인 API 엔드포인트 URL 설정
    # OAPILogin: Ecount ERP의 로그인 전용 API
    url = "http://sboapi.ecount.com/OAPI/V2/OAPILogin"
    
    # 2. 로그인에 필요한 데이터 준비
    data = {
        "COM_CODE": "665496",  # 회사 코드 (예주나라)
        "USER_ID": "황주선",   # 사용자 ID (로그인할 사용자명)
        "API_CERT_KEY": "37eb6e022031f4fa7b0705b8ced3dac534",  # API 인증키
        "LAN_TYPE": "ko-KR"    # 언어 설정 (한국어)
    }
    
    try:
        # 3. HTTP POST 요청으로 로그인 시도
        # POST 방식으로 인증 정보를 서버에 전송합니다
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        # 4. HTTP 응답 상태 코드 확인
        # 200: 성공, 401: 인증 실패, 500: 서버 오류 등
        print(f"응답 상태 코드: {response.status_code}")
        
        # 5. 서버 응답 내용 출력 (디버깅용)
        # 로그인 성공/실패 여부와 오류 메시지를 확인할 수 있습니다
        print(f"응답 내용: {response.text}")
        
        # 6. HTTP 상태 코드가 200(성공)인지 확인
        if response.status_code == 200:
            # 7. JSON 응답을 Python 딕셔너리로 변환
            # 서버에서 받은 JSON 데이터를 Python에서 사용할 수 있게 변환
            result = response.json()
            
            # 8. Ecount API의 자체 Status 필드 확인
            # HTTP 200이어도 API 레벨에서 실패할 수 있습니다
            if result.get('Status') == '200':
                print("✅ 로그인 성공!")
                
                # 9. 세션 토큰 추출 시도
                # 세션 토큰이 있으면 다른 API 호출 시 사용할 수 있습니다
                if result.get('Data') and 'Datas' in result['Data'] and result['Data']['Datas']:
                    # Data.Datas.SESSION_TOKEN 경로에서 토큰 추출
                    session_token = result['Data']['Datas'].get('SESSION_TOKEN')
                    print(f"세션 토큰: {session_token}")
                    return session_token  # 세션 토큰 반환
                else:
                    # 테스트용 인증키는 세션 토큰을 제공하지 않을 수 있습니다
                    print("세션 토큰 없음 (테스트용 인증키)")
                    return None
            else:
                # 10. API 레벨에서 실패한 경우 오류 메시지 출력
                # Error.Message에서 구체적인 실패 이유를 확인할 수 있습니다
                print(f"❌ 로그인 실패: {result.get('Error', {}).get('Message', 'Unknown error')}")
                return None
        else:
            print("❌ 요청 실패")
            return None
            
    except Exception as e:
        # 11. 예외 처리
        # 네트워크 오류, JSON 파싱 오류, 타임아웃 등을 처리합니다
        print(f"❌ 오류 발생: {e}")
        return None

# 12. 스크립트가 직접 실행될 때만 test_login() 함수를 호출
if __name__ == "__main__":
    test_login()
