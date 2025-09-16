"""
SaleList 업로드
Ecount ERP에 판매 데이터를 업로드합니다.
"""
import requests
import json
from datetime import datetime

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
    
    # 샘플 데이터 생성
    if sale_data is None:
        current_date = datetime.now().strftime('%Y%m%d')
        sale_data = {
            'SaleList': [{
                'BulkDatas': {
                    'IO_DATE': current_date,
                    'WH_CD': '00009',
                    'PROD_CD': '00001',
                    'PROD_DES': '업로드 테스트 상품',
                    'QTY': '1',
                    'PRICE': '1000'
                }
            }]
        }
    
    print("업로드할 데이터:")
    print(json.dumps(sale_data, ensure_ascii=False, indent=2))
    
    sale_url = 'http://sboapi.ecount.com/OAPI/V2/SaleList'
    
    # 헤더 설정
    if session_token:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {session_token}'
        }
        print(f"세션 토큰 사용: {session_token[:20]}...")
    else:
        headers = {
            'Content-Type': 'application/json',
            'API_CERT_KEY': '37eb6e022031f4fa7b0705b8ced3dac534'
        }
        print("API 키 사용")
    
    try:
        response = requests.post(sale_url, json=sale_data, headers=headers)
        print(f"\n응답 상태: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                print("✅ SaleList 업로드 성공!")
                return True
            else:
                print(f"❌ SaleList 업로드 실패: {result.get('Error', {}).get('Message', 'Unknown error')}")
                return False
        else:
            print("❌ SaleList 요청 실패")
            return False
    except Exception as e:
        print(f"❌ SaleList 업로드 오류: {e}")
        return False

def create_custom_sale_data(io_date, wh_cd, prod_cd, prod_des, qty, price):
    """
    커스텀 SaleList 데이터를 생성합니다.
    
    Args:
        io_date: 입출고일 (YYYYMMDD)
        wh_cd: 창고코드
        prod_cd: 상품코드
        prod_des: 상품명
        qty: 수량
        price: 단가
    
    Returns:
        dict: SaleList 데이터
    """
    return {
        'SaleList': [{
            'BulkDatas': {
                'IO_DATE': io_date,
                'WH_CD': wh_cd,
                'PROD_CD': prod_cd,
                'PROD_DES': prod_des,
                'QTY': str(qty),
                'PRICE': str(price)
            }
        }]
    }

def main():
    """메인 함수"""
    print("=== SaleList 업로드 도구 ===")
    
    # 1. 샘플 데이터로 업로드 테스트
    print("\n1. 샘플 데이터 업로드 테스트...")
    success = upload_sale_list()
    
    if success:
        print("\n✅ 샘플 데이터 업로드 성공!")
    else:
        print("\n❌ 샘플 데이터 업로드 실패")
    
    # 2. 커스텀 데이터 생성 예시
    print("\n2. 커스텀 데이터 생성 예시...")
    custom_data = create_custom_sale_data(
        io_date="20250917",
        wh_cd="00009", 
        prod_cd="TEST001",
        prod_des="커스텀 테스트 상품",
        qty=5,
        price=2000
    )
    
    print("커스텀 데이터:")
    print(json.dumps(custom_data, ensure_ascii=False, indent=2))
    
    print("\n=== 업로드 도구 완료 ===")

if __name__ == "__main__":
    main()
