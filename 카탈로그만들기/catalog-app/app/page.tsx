import { readFileSync } from "fs";
import path from "path";
import { list } from "@vercel/blob";
import CatalogClient from "@/components/CatalogClient";
import type { Product, Meta, Translations } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function CatalogPage() {
  const dataPath = path.join(process.cwd(), "data", "products.json");
  const metaPath = path.join(process.cwd(), "data", "meta.json");
  const translationsPath = path.join(process.cwd(), "data", "translations.json");
  const products: Product[] = JSON.parse(readFileSync(dataPath, "utf-8"));
  const meta: Meta = JSON.parse(readFileSync(metaPath, "utf-8"));
  const translations: Translations = JSON.parse(readFileSync(translationsPath, "utf-8"));

  // blob에 실제 업로드된 상품 ID 목록 (없으면 빈 Set)
  let blobProductIds: number[] = [];
  try {
    const { blobs } = await list({ prefix: "products/", token: process.env.BLOB_READ_WRITE_TOKEN });
    blobProductIds = blobs
      .map((b) => {
        const match = b.pathname.match(/^products\/(\d+)\.\w+$/);
        return match ? parseInt(match[1]) : null;
      })
      .filter((id): id is number => id !== null);
  } catch {
    // blob 토큰 없거나 실패 시 무시
  }

  return (
    <CatalogClient
      products={products}
      meta={meta}
      translations={translations}
      blobProductIds={blobProductIds}
    />
  );
}
