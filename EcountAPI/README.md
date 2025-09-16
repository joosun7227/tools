# Ecount ERP API 도구

Ecount ERP API를 연결하고 테스트하는 도구 모음입니다.

## 📁 파일 구성

### 핵심 테스트 파일
- **`zone_test.py`** - Zone 조회 테스트
- **`login_test.py`** - 로그인 테스트  
- **`verification_test.py`** - 종합 검증 테스트 (Zone → Login → SaleList)
- **`sale_upload.py`** - SaleList 업로드 도구

### 설정 파일
- **`requirements.txt`** - 필요한 Python 패키지
- **`README.md`** - 이 파일

## 🚀 사용 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. 개별 테스트 실행
```bash
# Zone 조회만 테스트
python zone_test.py

# 로그인만 테스트  
python login_test.py

# 종합 검증 테스트
python verification_test.py

# SaleList 업로드 테스트
python sale_upload.py
```

## 🔑 API 정보

- **테스트 인증키**: 37eb6e022031f4fa7b0705b8ced3dac534
- **회사 코드**: 665496
- **사용자 ID**: 황주선
- **테스트 URL**: http://sboapi.ecount.com

## 📋 주요 기능

### 1. Zone 조회 (`zone_test.py`)
- 회사 코드로 Zone 정보 조회
- API 검증의 첫 단계

### 2. 로그인 (`login_test.py`)
- API 인증 및 세션 토큰 획득
- 테스트용 인증키로 제한적 기능

### 3. 종합 검증 (`verification_test.py`)
- Zone 조회 → 로그인 → SaleList 순서로 테스트
- 전체 API 검증 완료

### 4. SaleList 업로드 (`sale_upload.py`)
- 판매 데이터 업로드
- 샘플 데이터 및 커스텀 데이터 지원
- 세션 토큰 또는 API 키 사용

## 🔧 API 엔드포인트

- **Zone 조회**: `http://sboapi.ecount.com/OAPI/V2/Zone`
- **로그인**: `http://sboapi.ecount.com/OAPI/V2/OAPILogin`
- **SaleList**: `http://sboapi.ecount.com/OAPI/V2/SaleList`

## ⚠️ 주의사항

- 현재 테스트용 인증키 사용 중
- 정식 인증키 발급 후 전체 기능 사용 가능
- ERP에서 웹자료올리기 설정 필요
