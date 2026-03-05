import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "그라미스 상품 카탈로그",
  description: "그라미스 동남아 식품 온라인 카탈로그",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
