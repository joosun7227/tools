"""
종합 검증 테스트
Ecount ERP API의 모든 기능을 종합적으로 테스트합니다.
Zone 조회 → 로그인 → SaleList 생성 순서로 진행합니다.

API 호출 순서가 중요한 이유:
1. Zone 조회: 어떤 서버를 사용할지 결정
2. 로그인: 인증 토큰을 받아서 권한 획득
3. SaleList: 실제 데이터를 생성/수정하는 작업
"""
import requests  # HTTP 요청을 보내기 위한 라이브러리
import json      # JSON 데이터 처리를 위한 라이브러리
from datetime import datetime  # 현재 날짜/시간을 가져오기 위한 라이브러리

def test_zone():
    """Zone 조회 테스트 - 1단계: 서버 영역 확인"""
    print("1. Zone 조회 테스트...")
    
    # 1-1. Zone 조회 API 엔드포인트
    # 모든 회사가 공통으로 사용하는 Zone 조회 서버
    url = "http://sboapi.ecount.com/OAPI/V2/Zone"
    
    # 1-2. 회사 코드만 전송 (Zone 조회는 회사 코드만 필요)
    data = {"COM_CODE": "665496"}
    
    try:
        # 1-3. Zone 조회 요청 전송
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        # 1-4. 응답 확인
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                # 1-5. Zone 정보 추출 (예: "AA")
                zone = result.get('Data', {}).get('ZONE', 'AA')
                print(f"✅ Zone 조회 성공: {zone}")
                return zone  # Zone 값을 반환 (다음 단계에서 사용)
            else:
                print("❌ Zone 조회 실패")
                return None
        else:
            print("❌ Zone 조회 요청 실패")
            return None
    except Exception as e:
        print(f"❌ Zone 조회 오류: {e}")
        return None

def test_login():
    """로그인 테스트 - 2단계: 인증 및 세션 토큰 획득"""
    print("\n2. 로그인 테스트...")
    
    # 2-1. 로그인 API 엔드포인트
    # Production URL: https://oapi{ZONE}.ecount.com/OAPI/V2/OAPILogin
    url = "https://oapiAA.ecount.com/OAPI/V2/OAPILogin"
    
    # 2-2. 로그인에 필요한 모든 정보 준비
    data = {
        "COM_CODE": "665496",  # 회사 코드
        "USER_ID": "황주선",   # 사용자 ID
        "API_CERT_KEY": "42a2aba2c2ec5449194dbd12d4e85048b9",  # 정식 API 인증키
        "LAN_TYPE": "ko-KR",   # 언어 설정
        "ZONE": "AA",           # ZONE 정보 (Zone 조회에서 받은 값)
        "SESSION_ID": "1234567890"
    }
    
    try:
        # 2-3. 로그인 요청 전송
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        # 2-4. 로그인 결과 확인
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                print("✅ 로그인 성공!")
                
                # 2-5. 세션 토큰 추출 시도
                # 세션 토큰이 있으면 다른 API 호출 시 인증에 사용
                if result.get('Data') and 'Datas' in result['Data'] and result['Data']['Datas']:
                    session_id = result['Data']['Datas'].get('SESSION_ID')
                    print(f"세션 ID: {session_id}")
                    return session_id
                else:
                    # 테스트용 인증키는 세션 토큰을 제공하지 않을 수 있음
                    print("세션 토큰 없음 (테스트용 인증키)")
                    return None
            else:
                # 2-6. 로그인 실패 시 오류 메시지 출력
                print(f"❌ 로그인 실패: {result.get('Error', {}).get('Message', 'Unknown error')}")
                return None
        else:
            print("❌ 로그인 요청 실패")
            return None
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return None

def test_sale_list(session_token=None):
    """SaleList 생성 테스트 - 3단계: 실제 데이터 생성"""
    print("\n3. SaleList 생성 테스트...")
    
    # 3-1. 현재 날짜를 YYYYMMDD 형식으로 변환
    # 예: 2025-09-17 → "20250917"
    current_date = datetime.now().strftime('%Y%m%d')
    
    # 3-2. SaleList 데이터 구조 생성
    # Ecount ERP에서 요구하는 정확한 JSON 구조를 만듭니다
    sale_data = {
        'SaleList': [{  # SaleList는 배열 형태
            'BulkDatas': {  # 실제 판매 데이터는 BulkDatas 안에 들어감
                'IO_DATE': current_date,      # 입출고일
                'CUST' : '44522',            # 거래처코드
                'EMP_CD' : '황주선',          # 담당자코드
                'WH_CD': '100',            # 창고코드
                'PROD_CD': '00002415',          # 상품코드
                'QTY': '5',                  # 수량 (문자열로 전송)
                'USER_PRICE_VAT': '1000'              # 단가 (문자열로 전송)
            }
        }]
    }
    
    # 3-3. SaleList API 엔드포인트 (올바른 URL 사용)
    # 세션 ID가 있으면 올바른 판매 API 사용, 없으면 테스트 불가
    if session_token:
        # Production URL: https://oapi{ZONE}.ecount.com/OAPI/V2/Sale/SaveSale?SESSION_ID={SESSION_ID}
        sale_url = f'https://oapiAA.ecount.com/OAPI/V2/Sale/SaveSale?SESSION_ID={session_token}'
        headers = {
            'Content-Type': 'application/json'
            # SESSION_ID는 URL 쿼리 파라미터로 전송 (헤더 불필요)
        }
        print(f"세션 ID로 판매 API 호출: {session_token[:20]}...")
    else:
        print("❌ 세션 ID가 없어서 판매 API 호출 불가")
        print("판매 API는 반드시 세션 ID가 필요합니다.")
        return False
    
    try:
        # 3-5. SaleList 생성 요청 전송
        response = requests.post(sale_url, json=sale_data, headers=headers)
        
        # 3-6. 응답 상태 및 내용 출력 (디버깅용)
        print(f"SaleList 응답 상태: {response.status_code}")
        print(f"SaleList 응답 내용: {response.text}")
        
        # 3-7. 응답 결과 확인
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                print("✅ SaleList 생성 성공!")
                return True
            else:
                # 3-8. API 레벨에서 실패한 경우 오류 메시지 출력
                print(f"❌ SaleList 생성 실패: {result.get('Error', {}).get('Message', 'Unknown error')}")
                return False
        else:
            print("❌ SaleList 요청 실패")
            return False
    except Exception as e:
        print(f"❌ SaleList 오류: {e}")
        return False

def main():
    """종합 검증 테스트 실행 - 전체 API 호출 흐름"""
    print("=== Ecount ERP API 종합 검증 테스트 ===")
    print("이 테스트는 API 호출 순서를 보여줍니다:")
    print("1단계: Zone 조회 → 2단계: 로그인 → 3단계: SaleList 생성")
    
    # 1단계: Zone 조회
    # Zone 정보를 먼저 확인해야 올바른 서버에 접속할 수 있습니다
    zone = test_zone()
    if not zone:
        print("\n❌ Zone 조회 실패로 인해 테스트 중단")
        print("Zone 조회가 실패하면 다른 API도 사용할 수 없습니다.")
        return
    
    # 2단계: 로그인
    # 인증을 받아서 세션 토큰을 획득합니다
    session_token = test_login()
    
    # 3단계: SaleList 생성
    # 실제 데이터를 생성하는 작업을 수행합니다
    sale_success = test_sale_list(session_token)
    
    # 4. 전체 결과 요약
    print("\n=== 검증 결과 요약 ===")
    print(f"Zone 조회: ✅ 성공 ({zone})")
    print(f"로그인: {'✅ 성공' if session_token else '❌ 실패 (테스트용 인증키)'}")
    print(f"SaleList 생성: {'✅ 성공' if sale_success else '❌ 실패'}")

# 6. 스크립트가 직접 실행될 때만 main() 함수를 호출
if __name__ == "__main__":
    main()
