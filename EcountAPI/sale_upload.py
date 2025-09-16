"""
SaleList 업로드 도구
Ecount ERP에 판매 데이터를 업로드하는 실용적인 도구입니다.

SaleList란?
- Ecount ERP에서 판매 데이터를 관리하는 기능입니다
- 상품의 입출고, 판매, 재고 관리를 위한 데이터입니다
- API를 통해 자동으로 판매 데이터를 입력할 수 있습니다
"""
import requests  # HTTP 요청을 보내기 위한 라이브러리
import json      # JSON 데이터 처리를 위한 라이브러리
from datetime import datetime  # 현재 날짜/시간을 가져오기 위한 라이브러리

def upload_sale_list(sale_data=None, session_token=None):
    """
    SaleList 데이터를 Ecount ERP에 업로드합니다.
    
    Args:
        sale_data: 업로드할 판매 데이터 (None이면 샘플 데이터 사용)
        session_token: 세션 토큰 (None이면 API 키 사용)
    
    Returns:
        bool: 업로드 성공 여부
    """
    print("=== SaleList 업로드 ===")
    
    # 1. 데이터 준비
    # sale_data가 없으면 기본 샘플 데이터를 생성합니다
    if sale_data is None:
        # 1-1. 현재 날짜를 YYYYMMDD 형식으로 변환
        current_date = datetime.now().strftime('%Y%m%d')
        
        # 1-2. Ecount ERP가 요구하는 정확한 JSON 구조로 데이터 생성
        sale_data = {
            'SaleList': [{  # SaleList는 배열 형태 (여러 상품을 한 번에 업로드 가능)
                'BulkDatas': {  # 실제 판매 데이터는 BulkDatas 안에 들어감
                    'IO_DATE': current_date,      # 입출고일 (YYYYMMDD)
                    'WH_CD': '00009',            # 창고코드 (예주나라의 창고)
                    'PROD_CD': '00001',          # 상품코드 (상품의 고유 식별자)
                    'PROD_DES': '업로드 테스트 상품',  # 상품명
                    'QTY': '1',                  # 수량 (문자열로 전송해야 함)
                    'PRICE': '1000'              # 단가 (문자열로 전송해야 함)
                }
            }]
        }
    
    # 1-3. 업로드할 데이터를 보기 좋게 출력 (디버깅용)
    print("업로드할 데이터:")
    print(json.dumps(sale_data, ensure_ascii=False, indent=2))
    
    # 2. API 엔드포인트 설정
    sale_url = 'http://sboapi.ecount.com/OAPI/V2/SaleList'
    
    # 3. 인증 방식 결정 및 헤더 설정
    if session_token:
        # 3-1. 세션 토큰이 있으면 Bearer 토큰 방식 사용
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {session_token}'  # Bearer 토큰 인증
        }
        print(f"세션 토큰 사용: {session_token[:20]}...")
    else:
        # 3-2. 세션 토큰이 없으면 API 키 방식 사용
        headers = {
            'Content-Type': 'application/json',
            'API_CERT_KEY': '37eb6e022031f4fa7b0705b8ced3dac534'  # API 키 인증
        }
        print("API 키 사용")
    
    try:
        # 4. HTTP POST 요청으로 SaleList 데이터 전송
        # requests.post()로 POST 방식으로 JSON 데이터를 서버에 전송
        response = requests.post(sale_url, json=sale_data, headers=headers)
        
        # 5. 응답 상태 및 내용 확인 (디버깅용)
        print(f"\n응답 상태: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        # 6. 응답 결과 처리
        if response.status_code == 200:
            # 6-1. JSON 응답을 Python 딕셔너리로 변환
            result = response.json()
            
            # 6-2. Ecount API의 Status 필드 확인
            if result.get('Status') == '200':
                print("✅ SaleList 업로드 성공!")
                return True
            else:
                # 6-3. API 레벨에서 실패한 경우 오류 메시지 출력
                print(f"❌ SaleList 업로드 실패: {result.get('Error', {}).get('Message', 'Unknown error')}")
                return False
        else:
            print("❌ SaleList 요청 실패")
            return False
    except Exception as e:
        # 7. 예외 처리
        # 네트워크 오류, JSON 파싱 오류 등을 처리
        print(f"❌ SaleList 업로드 오류: {e}")
        return False

def create_custom_sale_data(io_date, wh_cd, prod_cd, prod_des, qty, price):
    """
    커스텀 SaleList 데이터를 생성합니다.
    실제 업무에서 사용할 수 있는 데이터를 만들 때 사용합니다.
    
    Args:
        io_date: 입출고일 (YYYYMMDD 형식, 예: "20250917")
        wh_cd: 창고코드 (예: "00009")
        prod_cd: 상품코드 (예: "PROD001")
        prod_des: 상품명 (예: "테스트 상품")
        qty: 수량 (숫자, 예: 5)
        price: 단가 (숫자, 예: 2000)
    
    Returns:
        dict: Ecount ERP가 요구하는 SaleList 데이터 구조
    """
    # 1. Ecount ERP가 요구하는 정확한 JSON 구조로 데이터 생성
    return {
        'SaleList': [{  # SaleList는 배열 (여러 상품 동시 업로드 가능)
            'BulkDatas': {  # 실제 데이터는 BulkDatas 안에
                'IO_DATE': io_date,      # 입출고일
                'WH_CD': wh_cd,          # 창고코드
                'PROD_CD': prod_cd,      # 상품코드
                'PROD_DES': prod_des,    # 상품명
                'QTY': str(qty),         # 수량 (문자열로 변환)
                'PRICE': str(price)      # 단가 (문자열로 변환)
            }
        }]
    }

def main():
    """메인 함수 - 업로드 도구 실행"""
    print("=== SaleList 업로드 도구 ===")
    print("이 도구는 Ecount ERP에 판매 데이터를 업로드합니다.")
    
    # 1. 샘플 데이터로 업로드 테스트
    print("\n1. 샘플 데이터 업로드 테스트...")
    print("기본 샘플 데이터를 사용해서 업로드를 시도합니다.")
    
    success = upload_sale_list()  # sale_data=None이므로 기본 샘플 데이터 사용
    
    if success:
        print("\n✅ 샘플 데이터 업로드 성공!")
        print("API 연결이 정상적으로 작동합니다.")
    else:
        print("\n❌ 샘플 데이터 업로드 실패")
        print("API 연결에 문제가 있거나 권한이 부족할 수 있습니다.")
    
    # 2. 커스텀 데이터 생성 예시
    print("\n2. 커스텀 데이터 생성 예시...")
    print("실제 업무에서 사용할 수 있는 데이터 구조를 보여줍니다.")
    
    # 2-1. 커스텀 데이터 생성
    custom_data = create_custom_sale_data(
        io_date="20250917",           # 입출고일
        wh_cd="00009",                # 창고코드
        prod_cd="TEST001",            # 상품코드
        prod_des="커스텀 테스트 상품",    # 상품명
        qty=5,                        # 수량
        price=2000                    # 단가
    )
    
    # 2-2. 생성된 커스텀 데이터 출력
    print("커스텀 데이터:")
    print(json.dumps(custom_data, ensure_ascii=False, indent=2))
    
    print("\n=== 업로드 도구 완료 ===")
    print("이제 create_custom_sale_data() 함수를 사용해서")
    print("실제 업무 데이터를 생성하고 upload_sale_list()로 업로드할 수 있습니다.")

# 3. 스크립트가 직접 실행될 때만 main() 함수를 호출
if __name__ == "__main__":
    main()
