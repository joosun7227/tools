import { NextRequest, NextResponse } from "next/server";
import { readFileSync } from "fs";
import path from "path";
import { put, list } from "@vercel/blob";
import * as XLSX from "xlsx";
import type { Product, ProductUnit, Meta } from "@/lib/types";

const PRODUCTS_BLOB = "data/products.json";
const META_BLOB = "data/meta.json";
const UNIT_ORDER = ["BOX", "PACK", "BUNDLE", "KG", "EA", "포"];

function unitSortKey(u: string) {
  const idx = UNIT_ORDER.indexOf(u);
  return idx === -1 ? UNIT_ORDER.length : idx;
}

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

async function saveBlobJson(blobPath: string, data: unknown) {
  const token = process.env.BLOB_READ_WRITE_TOKEN;
  if (!token) throw new Error("BLOB_READ_WRITE_TOKEN not set");
  await put(blobPath, JSON.stringify(data, null, 2), {
    access: "public",
    addRandomSuffix: false,
    token,
    contentType: "application/json",
  });
}

function getLocalProducts(): Product[] {
  return JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf-8"));
}

function parseExcel(buffer: ArrayBuffer): Product[] {
  const wb = XLSX.read(buffer, { type: "array" });
  const ws = wb.Sheets[wb.SheetNames[0]];
  // header:1 → 2D array, row[0] is header
  const rows = XLSX.utils.sheet_to_json<unknown[]>(ws, { header: 1, defval: null });

  // 헤더 행 제거 (첫 행)
  const dataRows = rows.slice(1) as (string | number | null)[][];

  // 열 인덱스 (prepare_data.py 기준)
  const COL_PRODCD   = 0;
  const COL_UNIT     = 3;
  const COL_SPEC     = 4;
  const COL_STORAGE  = 11;
  const COL_COUNTRY  = 12;
  const COL_BRAND    = 13;
  const COL_CATEGORY = 14;
  const COL_PRICE    = 18;
  const COL_REPCD    = 26;
  const COL_REPNM    = 27;

  // 대표품목코드 기준 그루핑
  const groups = new Map<number, (string | number | null)[][]>();
  for (const row of dataRows) {
    const repCd = row[COL_REPCD];
    const price = row[COL_PRICE];
    if (repCd == null || repCd === "" || Number(price) <= 0) continue;
    const id = parseInt(String(repCd));
    if (isNaN(id)) continue;
    if (!groups.has(id)) groups.set(id, []);
    groups.get(id)!.push(row);
  }

  const products: Product[] = [];
  for (const [id, rows] of groups) {
    const first = rows[0];
    const name = first[COL_REPNM] != null ? String(first[COL_REPNM]).trim() : "";
    const units: ProductUnit[] = rows.map((row) => ({
      prodCd: String(parseInt(String(row[COL_PRODCD]))).padStart(8, "0"),
      unit: row[COL_UNIT] != null ? String(row[COL_UNIT]).trim() : "",
      price: parseInt(String(row[COL_PRICE])) || 0,
      spec: row[COL_SPEC] != null ? String(row[COL_SPEC]).trim() : "",
    }));
    units.sort((a, b) => unitSortKey(a.unit) - unitSortKey(b.unit));

    products.push({
      id,
      name,
      country:  first[COL_COUNTRY]  != null ? String(first[COL_COUNTRY]).trim()  : "",
      brand:    first[COL_BRAND]    != null ? String(first[COL_BRAND]).trim()    : "",
      category: first[COL_CATEGORY] != null ? String(first[COL_CATEGORY]).trim() : "",
      storage:  first[COL_STORAGE]  != null ? String(first[COL_STORAGE]).trim()  : "",
      imageFile: null,
      units,
    });
  }

  products.sort((a, b) => a.id - b.id);
  return products;
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;
    if (!file) return NextResponse.json({ error: "file required" }, { status: 400 });

    const buffer = await file.arrayBuffer();
    const newProducts = parseExcel(buffer);
    if (newProducts.length === 0) {
      return NextResponse.json({ error: "유효한 품목 데이터가 없습니다" }, { status: 400 });
    }

    // 기존 products 로드 (blob 우선 → local fallback)
    const existing: Product[] = (await getBlobJson<Product[]>(PRODUCTS_BLOB)) ?? getLocalProducts();
    const existingMap = new Map(existing.map((p) => [p.id, p]));

    let added = 0, updated = 0;
    for (const np of newProducts) {
      const ex = existingMap.get(np.id);
      if (ex) {
        // 기존 imageFile 유지, 나머지 업데이트
        existingMap.set(np.id, { ...np, imageFile: ex.imageFile });
        updated++;
      } else {
        existingMap.set(np.id, np);
        added++;
      }
    }

    const merged = Array.from(existingMap.values()).sort((a, b) => a.id - b.id);

    // meta 업데이트
    const categories = [...new Set(merged.map((p) => p.category).filter(Boolean))].sort();
    const countries  = [...new Set(merged.map((p) => p.country).filter(Boolean))].sort();
    const storages   = [...new Set(merged.map((p) => p.storage).filter(Boolean))].sort();
    const meta: Meta = { categories, countries, storages };

    await Promise.all([
      saveBlobJson(PRODUCTS_BLOB, merged),
      saveBlobJson(META_BLOB, meta),
    ]);

    return NextResponse.json({
      ok: true,
      total: merged.length,
      added,
      updated,
    });
  } catch (err) {
    console.error("POST /api/admin/products error:", err);
    return NextResponse.json({ error: "처리 중 오류가 발생했습니다" }, { status: 500 });
  }
}
