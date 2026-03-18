import { readFileSync } from "fs";
import path from "path";
import { list } from "@vercel/blob";
import CatalogClient from "@/components/CatalogClient";
import type { Product, Meta, Translations } from "@/lib/types";

export const dynamic = "force-dynamic";

async function getBlobJson<T>(prefix: string): Promise<T | null> {
  const token = process.env.BLOB_READ_WRITE_TOKEN;
  if (!token) return null;
  try {
    const { blobs } = await list({ prefix, token });
    if (blobs.length === 0) return null;
    const res = await fetch(blobs[0].url, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export default async function CatalogPage() {
  const dataDir = path.join(process.cwd(), "data");

  const [products, meta, translations, blobProductIds] = await Promise.all([
    getBlobJson<Product[]>("data/products.json").then(
      (d) => d ?? (JSON.parse(readFileSync(path.join(dataDir, "products.json"), "utf-8")) as Product[])
    ),
    getBlobJson<Meta>("data/meta.json").then(
      (d) => d ?? (JSON.parse(readFileSync(path.join(dataDir, "meta.json"), "utf-8")) as Meta)
    ),
    getBlobJson<Translations>("data/translations.json").then(
      (d) => d ?? (JSON.parse(readFileSync(path.join(dataDir, "translations.json"), "utf-8")) as Translations)
    ),
    // blob에 실제 업로드된 상품 이미지 ID 목록
    list({ prefix: "products/", token: process.env.BLOB_READ_WRITE_TOKEN ?? "" })
      .then(({ blobs }) =>
        blobs
          .map((b) => { const m = b.pathname.match(/^products\/(\d+)\.\w+$/); return m ? parseInt(m[1]) : null; })
          .filter((id): id is number => id !== null)
      )
      .catch(() => [] as number[]),
  ]);

  return (
    <CatalogClient
      products={products}
      meta={meta}
      translations={translations}
      blobProductIds={blobProductIds}
    />
  );
}
