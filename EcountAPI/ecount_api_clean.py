"""
Ecount ERP API - 깔끔한 버전
필수 기능만 포함된 실용적인 API 연동 코드
"""
import requests
import json
from datetime import datetime

def get_zone():
    """Zone 조회"""
    url = "http://sboapi.ecount.com/OAPI/V2/Zone"
    data = {"COM_CODE": "665496"}
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                return result.get('Data', {}).get('ZONE', 'AA')
    except:
        pass
    return None

def login():
    """로그인 및 세션 ID 획득"""
    url = "https://oapiAA.ecount.com/OAPI/V2/OAPILogin"
    data = {
        "COM_CODE": "665496",
        "USER_ID": "황주선",
        "API_CERT_KEY": "42a2aba2c2ec5449194dbd12d4e85048b9",
        "LAN_TYPE": "ko-KR",
        "ZONE": "AA"
    }
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                if result.get('Data') and 'Datas' in result['Data'] and result['Data']['Datas']:
                    return result['Data']['Datas'].get('SESSION_ID')
    except:
        pass
    return None

def create_sale(session_id, sale_data):
    """판매 데이터 생성"""
    if not session_id:
        return False
        
    url = f'https://oapiAA.ecount.com/OAPI/V2/Sale/SaveSale?SESSION_ID={session_id}'
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=sale_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                return result
    except:
        pass
    return False

def get_sample_sale_data():
    """샘플 판매 데이터 생성"""
    current_date = datetime.now().strftime('%Y%m%d')
    
    return {
        'SaleList': [{
            'BulkDatas': {
                'IO_DATE': current_date,
                'CUST': '44522',
                'EMP_CD': '황주선',
                'WH_CD': '100',
                'PROD_CD': '00002415',
                'QTY': '5',
                'USER_PRICE_VAT': '1000'
            }
        }]
    }

def main():
    """메인 실행 함수"""
    # Zone 조회
    zone = get_zone()
    if not zone:
        print("Zone 조회 실패")
        return False
    
    # 로그인
    session_id = login()
    if not session_id:
        print("로그인 실패")
        return False
    
    # 판매 데이터 생성
    sale_data = get_sample_sale_data()
    result = create_sale(session_id, sale_data)
    
    if result:
        print("판매 데이터 생성 성공")
        return True
    else:
        print("판매 데이터 생성 실패")
        return False

if __name__ == "__main__":
    main()
