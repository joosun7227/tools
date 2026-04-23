import type { Metadata } from "next"; // Next.js의 메타데이터 타입만 가져옴
import "./globals.css"; // 전체 사이트에 공통 적용할 CSS 파일 불러옴

const SITE_URL = "https://yejoo-order.com"; // 사이트 기본 주소 저장

export const metadata: Metadata = { // Next.js가 읽는 사이트 메타정보 객체 시작
  metadataBase: new URL(SITE_URL), // 상대경로를 절대경로로 바꿀 때 기준이 되는 기본 URL
  title: { // 페이지 제목 설정
    default: "예주나라 — 동남아식품 도매 1위 | 태국·베트남·인도네시아 식품", // 기본 제목
    template: "%s | 예주나라", // 하위 페이지 제목 형식
  },
  description: // 사이트 설명
    "동남아식품의 No.1 예주나라. 태국식품, 베트남식품, 인도네시아음식, 수입식품 도매 전문. 아시아마트 동남아식품 도매의 선두주자. 동남아식품수입, 수입식품도매, 태국음식, 베트남음식, 동남아마트.",
  keywords: [ // 검색 키워드 목록
    "동남아식품",
    "태국식품",
    "베트남식품",
    "수입식품",
    "태국음식",
    "베트남음식",
    "인도네시아음식",
    "아시아마트",
    "동남아식품수입",
    "동남아식품도매",
    "동남아마트",
    "수입식품도매",
    "예주나라",
    "동남아식품전문",
    "수입식품전문",
    "태국과자",
    "베트남쌀국수",
    "동남아음료",
    "아시아식품",
    "식품수입도매",
  ],
  authors: [{ name: "예주나라", url: SITE_URL }], // 작성자 정보
  creator: "예주나라", // 만든 주체
  publisher: "예주나라", // 발행 주체
  openGraph: { // 카카오톡, 페이스북 등 공유용 정보
    type: "website", // 웹사이트 타입
    locale: "ko_KR", // 한국어/한국 지역
    url: SITE_URL, // 대표 URL
    siteName: "예주나라", // 사이트 이름
    title: "예주나라 — 동남아식품 도매 1위 | 태국·베트남·인도네시아 식품", // 공유 제목
    description: // 공유 설명
      "동남아식품의 No.1 예주나라. 태국·베트남·인도네시아 수입식품 도매 전문. 아시아마트 동남아식품 도매의 선두주자.",
    images: [ // 공유 이미지 목록
      {
        url: "/og-image.png", // 공유 이미지 경로
        width: 1200, // 이미지 너비
        height: 630, // 이미지 높이
        alt: "예주나라 동남아식품 도매", // 이미지 설명
      },
    ],
  },
  twitter: { // 트위터 공유용 정보
    card: "summary_large_image", // 큰 이미지 카드 형식
    title: "예주나라 — 동남아식품 도매 1위", // 트위터 제목
    description: "태국·베트남·인도네시아 수입식품 도매 전문 예주나라", // 트위터 설명
  },
  robots: { // 검색엔진 크롤링 허용 여부
    index: true, // 검색엔진에 색인 허용
    follow: true, // 링크 따라가기 허용
    googleBot: { // 구글봇 전용 설정
      index: true, // 구글 색인 허용
      follow: true, // 구글 링크 따라가기 허용
      "max-image-preview": "large", // 큰 이미지 미리보기 허용
      "max-snippet": -1, // 텍스트 요약 길이 제한 없음
    },
  },
  alternates: { // 대표 URL 설정
    canonical: SITE_URL, // 표준 URL
  },
  verification: { // 검색엔진 인증 코드 넣는 곳
    // 네이버 서치어드바이저 등록 시 아래 값을 채워주세요
    // naver: "YOUR_NAVER_CODE",
    // google: "YOUR_GOOGLE_CODE",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) { // 전체 페이지를 감싸는 기본 레이아웃 함수
  return ( // 화면 구조 반환
    <html lang="ko"> {/* 문서 언어를 한국어로 설정 */}
      <head> {/* head 영역 시작 */}
        <script
          type="application/ld+json" // 구조화 데이터(JSON-LD) 타입
          dangerouslySetInnerHTML={{ // script 안에 JSON 문자열을 직접 넣음
            __html: JSON.stringify({ // 객체를 JSON 문자열로 변환
              "@context": "https://schema.org", // 스키마 규칙 주소
              "@type": "Organization", // 조직 타입
              name: "예주나라", // 조직명
              url: SITE_URL, // 조직 대표 URL
              description: // 조직 설명
                "동남아식품의 No.1 예주나라. 태국식품, 베트남식품, 인도네시아음식, 수입식품 도매 전문.",
              contactPoint: { // 연락처 정보
                "@type": "ContactPoint", // 연락처 타입
                telephone: "+82-10-8587-7227", // 전화번호
                contactType: "customer service", // 고객센터 성격
                availableLanguage: ["Korean"], // 지원 언어
              },
              sameAs: [], // SNS 주소 넣는 자리
            }),
          }}
        />
      </head>
      <body className="bg-gray-50 min-h-screen">{children}</body> {/* 공통 body와 각 페이지 내용 */}
    </html>
  );
}