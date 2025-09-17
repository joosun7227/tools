# Ecount ERP API 도구

Ecount ERP API를 연결하고 테스트하는 도구 모음입니다.

## 📁 파일 구성

### 핵심 파일
- **`verification_test.py`** - 종합 검증 테스트 (Zone → Login → SaleList)
- **`sale_upload.py`** - 실제 업무용 판매 데이터 업로드 도구

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

# 실제 판매 데이터 업로드
python sale_upload.py
```

## 🔑 API 정보

- **정식 인증키**: 42a2aba2c2ec5449194dbd12d4e85048b9
- **회사 코드**: 665496
- **사용자 ID**: 황주선
- **테스트 URL**: http://sboapi.ecount.com

## 📋 주요 기능

### 1. 종합 검증 (`verification_test.py`)
- **Zone 조회** → **로그인** → **SaleList 생성** 순서로 전체 API 테스트
- 모든 API 연결 상태를 한 번에 확인
- 실제 판매번호 생성까지 완료

### 2. 판매 데이터 업로드 (`sale_upload.py`)
- 실제 업무용 판매 데이터 업로드 도구
- 샘플 데이터 및 커스텀 데이터 지원
- 세션 ID를 사용한 안전한 데이터 전송

## 🔧 API 엔드포인트

- **Zone 조회**: `http://sboapi.ecount.com/OAPI/V2/Zone`
- **로그인**: `https://oapiAA.ecount.com/OAPI/V2/OAPILogin`
- **판매 등록**: `https://oapiAA.ecount.com/OAPI/V2/Sale/SaveSale`

## ⚠️ 주의사항

- ✅ 정식 인증키 사용 중 (모든 기능 사용 가능)
- ERP에 등록된 창고코드, 상품코드 사용 필요
- 필수 항목은 ERP 입력화면 설정에 따라 달라질 수 있음
