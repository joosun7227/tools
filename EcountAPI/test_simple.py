"""
Zone 조회 테스트
Ecount ERP API의 Zone 정보를 조회합니다.
"""
import requests

def test_zone():
    print("=== Zone 조회 테스트 ===")
    
    url = "http://sboapi.ecount.com/OAPI/V2/Zone"
    data = {"COM_CODE": "665496"}
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == '200':
                zone = result.get('Data', {}).get('ZONE', 'Unknown')
                print(f"✅ Zone 조회 성공: {zone}")
                return zone
            else:
                print("❌ Zone 조회 실패")
                return None
        else:
            print("❌ 요청 실패")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    test_zone()
