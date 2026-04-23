# 카탈로그만들기 (예주나라 발주 앱)

예주나라 상품 카탈로그 + 발주 시스템. 프로덕션: **https://yejoo-order.com**

## 전체 구조

```
카탈로그만들기/
├── 품목정보.xlsx                   ← 원본 마스터 데이터 (ERP에서 추출)
├── scripts/
│   └── prepare_data.py             ← xlsx → products.json / meta.json 변환
├── update_translations.py          ← 신규 상품 자동 번역 (Google Translate)
├── gen_translations.py             ← 번역 엑셀 기반 매칭 (레거시, 경로 하드코딩 주의)
├── translate_missing.py            ← 누락 번역 채우기 (레거시, 경로 하드코딩 주의)
└── catalog-app/                    ← Next.js 프론트+백엔드 (Vercel 배포 대상)
    ├── app/
    │   ├── page.tsx                ← 메인 카탈로그 (SSR, Blob→로컬 폴백)
    │   ├── admin/                  ← 관리자 페이지
    │   ├── cart/ order/            ← 장바구니, 주문서
    │   └── api/
    │       ├── admin/ image/
    │       ├── inquiry/            ← 문의
    │       ├── order/ecount/       ← 주문 시 Ecount ERP로 판매 전표 생성
    │       └── products/
    ├── components/
    │   ├── CatalogClient.tsx       ← 목록/필터/페이징
    │   ├── ProductCard.tsx         ← 단위(BOX/PACK/EA…) 선택 버튼
    │   ├── CartDrawer.tsx LangSwitcher.tsx InquiryButton.tsx
    ├── data/                       ← products.json, meta.json, translations.json
    ├── public/images/              ← 상품 이미지 (원본, Blob에도 복사)
    ├── scripts/                    ← 운영 스크립트 (Node)
    │   ├── upload_data.mjs         ← data/*.json → Vercel Blob 업로드
    │   ├── upload_images.mjs       ← public/images/* → Blob products/
    │   └── list_data_blobs.mjs     ← Blob 현황 조회
    ├── lib/types.ts uiText.ts
    ├── store/                      ← Zustand (cart/lang/translations/loading)
    ├── .env.local                  ← Blob 토큰, Ecount 자격증명 (커밋 금지)
    ├── .vercel/project.json        ← Vercel 프로젝트 링크 (커밋 금지)
    └── vercel.json                 ← icn1 리전 고정
```

## 데이터 파이프라인

```
품목정보.xlsx (ERP export)
        │
        ▼  scripts/prepare_data.py
data/products.json  +  data/meta.json
        │
        ▼  update_translations.py  (신규 ID만 en/th/vi 자동번역)
data/translations.json
        │
        ▼  catalog-app/scripts/upload_data.mjs
Vercel Blob (data/*.json)
        │
        ▼  force-dynamic + no-store fetch
yejoo-order.com 즉시 반영
```

### 단위 그루핑 규칙 (`prepare_data.py`)

- **대표품목코드(col 27)** 기준으로 같은 상품의 여러 단위(BOX/PACK/EA 등)를 한 카드에 묶음
- 대표품목코드가 없으면 품목코드로, 대표품목명이 없으면 품목명으로 채움
- 필터: 대표품목코드 존재 여부만 체크 (**가격 0원도 포함** — 2026-04-23 변경)
- `UNIT_ORDER = ["BOX", "PACK", "BUNDLE", "KG", "EA", "포"]` 순으로 정렬 → BOX가 기본 선택됨
- 이미지 매칭: `public/images/{대표품목명}.{png|jpg}` 또는 `{대표품목명}-Photoroom.*`

## Vercel 배포 정보

| 항목 | 값 |
|------|-----|
| 프로젝트명 | `catalog-app` |
| 조직 | `joosun7227s-projects` (team_yBxEM91rphDFuHx1G01VfCKv) |
| projectId | `prj_JvtWv8sZQWwX8QESgqhsf5QPRfAT` |
| 커스텀 도메인 | https://yejoo-order.com |
| 프리뷰 URL | `catalog-app-joosun7227s-projects.vercel.app` (Deployment Protection 유효) |
| 리전 | icn1 (서울) |
| 빌드 | Next.js 15.5.7 / React 19 / Tailwind 4 / Turbopack |
| 로컬 개발 포트 | 3009 (`npm run dev`) |
| GitHub 리포지토리 | `joosun7227/tools` (경로: `도구모음집/카탈로그만들기/catalog-app/`) |

### Vercel Blob 저장소
- Token: `.env.local`의 `BLOB_READ_WRITE_TOKEN`
- Public URL: `https://4cg4qxoklcl6ovc0.public.blob.vercel-storage.com`
- 구조:
  - `data/products.json` `data/meta.json` `data/translations.json` `data/inquiries.json`
  - `products/*.{png,jpg}` — 상품 이미지

### 외부 연동
- **Ecount ERP** (`/api/order/ecount/route.ts`)
  - 기본 계정(`ECOUNT_*`): com_code 665496, user_id `거래처미등록`, wh_cd 100
  - 장성지사(`ECOUNT_2_*`): com_code 670393, user_id MASTER7, wh_cd 400
  - 주문 시 자동으로 판매 전표 생성
- **구글 자동번역** (deep_translator, `ko → en/th/vi`)

## 자주 하는 작업

### 1) 신규 품목정보 반영 (xlsx 업데이트 후)

```bash
cd 도구모음집/카탈로그만들기
python scripts/prepare_data.py          # products.json + meta.json 재생성
cd catalog-app
node scripts/upload_data.mjs             # Blob 업로드 → 즉시 반영
```

### 2) 신규 상품 자동 번역

```bash
cd 도구모음집/카탈로그만들기
python update_translations.py            # 빈 en/th/vi 슬롯 채움 (1~2분)
# upload_data.mjs의 files 배열에 "translations.json" 추가 후 실행
```

### 3) 이미지 추가

```bash
cd 도구모음집/카탈로그만들기/catalog-app
# public/images/ 에 새 이미지 복사 후:
node scripts/upload_images.mjs           # 신규 이미지만 Blob에 업로드
```

### 4) 코드 수정 → 배포

GitHub `joosun7227/tools` main 브랜치에 푸시하면 Vercel이 자동 배포 (연결 후).
수동: `cd catalog-app && vercel deploy --prod`.

## 트러블슈팅 메모

- **Vercel CLI 로그인 문제**: 현재 CLI에 잘못된 계정(`joosun7227-3821`)으로 로그인된 경우 `npx vercel logout` 후 본 프로젝트 소유 계정(`joosun7227`)으로 재로그인 필요. `vercel whoami` 로 현재 계정 확인.
- **.venv 파이썬 깨짐**: `.venv/Scripts/python.exe`의 shebang이 존재하지 않는 `C:\Python312`를 가리켜 실행 불가. 시스템 python (3.11, `AppData/Local/Microsoft/WindowsApps/python.exe`)으로 실행하면 됨. `deep_translator`는 `python -m pip install --user deep_translator`로 유저사이트에 설치됨.
- **Blob 우선 폴백**: [app/page.tsx](catalog-app/app/page.tsx)가 Blob을 먼저 읽고 없으면 로컬을 씀. Blob에 파일이 한 번이라도 올라가면 **로컬만 바꿔선 프로덕션 반영 안 됨** — 반드시 Blob 재업로드 필요.
- **가격 0원 단위 노출**: [prepare_data.py](scripts/prepare_data.py)에서 `& (df[col_price] > 0)` 필터를 제거한 상태(2026-04-23). EA/PACK 중 가격이 0인 것도 옵션 버튼으로 표시됨.
- **단위 필터**: [ProductCard.tsx](catalog-app/components/ProductCard.tsx)에서 "BOX가 있으면 BOX만" 필터는 **제거된 상태**. 모든 단위가 버튼으로 보임.

## 현재 상태 스냅샷 (2026-04-23 기준)

- 프로덕션 라이브 상품 수: **1,502개** (대표품목 그루핑)
- 전체 단위 행: 2,890개 (EA/PACK 포함, 가격 0원 포함)
- 번역 커버리지: 1,513개 ID (en/th/vi 채움), 최근 추가 49개 ID는 **한국어만** — 자동번역 대기
- 이미지 매칭: 781개 (총 상품의 약 52%)
- Blob 업로드 시각:
  - products.json (752 KB)
  - meta.json (1.6 KB)
  - translations.json (333 KB, 신규 49개 미반영 버전)

## 미완료/향후 할 일

1. 신규 49개 상품 자동 번역 후 translations.json Blob 재업로드
2. 로컬 변경사항(2026-03-19 이후 2달치) 커밋 및 GitHub push
3. Vercel ↔ GitHub 연결 (Vercel 대시보드 → Project → Settings → Git → Connect → `joosun7227/tools`, Root Directory = `도구모음집/카탈로그만들기/catalog-app`)
4. 이미지가 없는 721개 상품 이미지 수급
