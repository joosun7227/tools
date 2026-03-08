import { NextResponse } from "next/server";
import { list } from "@vercel/blob";
import JSZip from "jszip";

export const maxDuration = 60;

export async function GET() {
  // blob 스토리지에서 products/ 폴더의 모든 파일 목록 가져오기
  const { blobs } = await list({ prefix: "products/" });

  if (blobs.length === 0) {
    return NextResponse.json({ error: "다운로드할 이미지가 없습니다." }, { status: 404 });
  }

  const zip = new JSZip();
  const folder = zip.folder("images")!;

  // 모든 이미지 병렬 fetch
  await Promise.all(
    blobs.map(async (blob) => {
      try {
        const res = await fetch(blob.url);
        if (!res.ok) return;
        const buf = await res.arrayBuffer();
        const filename = blob.pathname.replace("products/", "");
        folder.file(filename, buf);
      } catch {
        // 개별 파일 실패는 무시
      }
    })
  );

  const zipBuffer = await zip.generateAsync({ type: "arraybuffer", compression: "DEFLATE" });

  return new NextResponse(zipBuffer as ArrayBuffer, {
    headers: {
      "Content-Type": "application/zip",
      "Content-Disposition": `attachment; filename="product-images.zip"`,
    },
  });
}
