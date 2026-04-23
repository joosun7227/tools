import { NextRequest, NextResponse } from "next/server";
import { put, head } from "@vercel/blob";
import { readFileSync } from "fs";
import path from "path";

const BLOB_TOKEN = process.env.BLOB_READ_WRITE_TOKEN!;
const BLOB_BASE  = process.env.NEXT_PUBLIC_BLOB_STORE_URL ?? "";

async function loadProducts(): Promise<Record<string, unknown>[]> {
  // Blob에서 먼저 시도, 없으면 로컬 파일
  try {
    const blobMeta = await head("data/products.json", { token: BLOB_TOKEN });
    const res = await fetch(blobMeta.url);
    return await res.json();
  } catch {
    const local = path.join(process.cwd(), "data", "products.json");
    return JSON.parse(readFileSync(local, "utf-8"));
  }
}

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const file = formData.get("file") as File | null;

  if (!file) {
    return NextResponse.json({ error: "file required" }, { status: 400 });
  }

  // 파일명 그대로 사용 (예: 142.jpg → products/142.jpg)
  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
  const pathname = `products/${safeName}`;

  // 1. 이미지 Blob 업로드
  const blob = await put(pathname, file, {
    access: "public",
    allowOverwrite: true,
    contentType: file.type || "image/jpeg",
    token: BLOB_TOKEN,
  });

  // 2. 품목 ID 추출 (파일명에서 확장자 제거 후 숫자 확인)
  const stem = safeName.replace(/\.[^.]+$/, "");
  const productId = Number(stem);

  if (!isNaN(productId) && productId > 0) {
    try {
      const products = await loadProducts();
      const idx = products.findIndex((p) => Number((p as { id: number }).id) === productId);
      if (idx !== -1) {
        (products[idx] as { imageFile: string }).imageFile = safeName;
        // Blob의 products.json 업데이트
        await put("data/products.json", JSON.stringify(products), {
          access: "public",
          allowOverwrite: true,
          contentType: "application/json",
          token: BLOB_TOKEN,
        });
      }
    } catch (e) {
      console.error("[upload] products.json 업데이트 실패:", e);
      // 이미지 업로드는 성공했으므로 에러 무시
    }
  }

  return NextResponse.json({ url: blob.url, pathname, blobBase: BLOB_BASE });
}
