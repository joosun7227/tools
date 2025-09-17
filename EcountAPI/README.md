# Ecount ERP API 도구

Ecount ERP API를 연결하고 테스트하는 도구 모음입니다.

## 📁 파일 구성

### 핵심 파일
- **`verification_test.py`** - 종합 검증 테스트 (Zone → Login → SaleList)

### 설정 파일
- **`requirements.txt`** - 필요한 Python 패키지
- **`README.md`** - 이 파일

## 🚀 사용 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. 테스트 실행
```bash
# 전체 API 검증 테스트 (권장)
python verification_test.py
```

## 🔑 API 정보

- **정식 인증키**: 42a2aba2c2ec5449194dbd12d4e85048b9
- **회사 코드**: 665496
- **사용자 ID**: 황주선
- **Zone**: AA

## 📋 주요 기능

### 종합 검증 (`verification_test.py`)
- **Zone 조회** → **로그인** → **SaleList 생성** 순서로 전체 API 테스트
- 모든 API 연결 상태를 한 번에 확인
- 실제 판매번호 생성까지 완료
- 샘플 데이터로 ERP 연동 테스트

## 🔧 API 엔드포인트

- **Zone 조회**: `http://sboapi.ecount.com/OAPI/V2/Zone` (공통)
- **로그인**: `https://oapiAA.ecount.com/OAPI/V2/OAPILogin` (정식)
- **판매 등록**: `https://oapiAA.ecount.com/OAPI/V2/Sale/SaveSale` (정식)

## ⚠️ 주의사항

- ✅ **정식 인증키** 사용 중 (모든 기능 사용 가능)
- ✅ **정식 URL** 사용 중 (Production 환경)
- ✅ **모든 API 연동 완료** (Zone, Login, Sale)
- ERP에 등록된 창고코드, 상품코드 사용 필요
- 실제 업무 데이터 입력 시 `verification_test.py` 코드를 참고하여 커스터마이징
