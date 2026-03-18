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

// 헤더 이름으로 열 인덱스 찾기 (정확일치 → 포함 순서)
function findCol(headers: string[], keywords: string[], exclude?: string[]): number {
  const norm = (s: string) => s.replace(/\s+/g, "").toLowerCase();
  const excl = (exclude ?? []).map(norm);
  // 정확 일치 우선
  for (const kw of keywords) {
    const idx = headers.findIndex((h) => norm(h) === norm(kw) && !excl.some((e) => norm(h).includes(e)));
    if (idx !== -1) return idx;
  }
  // 포함 일치
  for (const kw of keywords) {
    const idx = headers.findIndex((h) => norm(h).includes(norm(kw)) && !excl.some((e) => norm(h) === e));
    if (idx !== -1) return idx;
  }
  return -1;
}

function str(v: unknown): string {
  return v != null && v !== "" ? String(v).trim() : "";
}

type ParseResult = { products: Product[] } | { error: string; found: string[] };

function parseExcel(buffer: ArrayBuffer): ParseResult {
  const wb = XLSX.read(buffer, { type: "array", codepage: 65001 });
  const ws = wb.Sheets[wb.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json<unknown[]>(ws, { header: 1, defval: null });

  if (rows.length < 2) return { error: "데이터가 없습니다 (헤더 + 데이터 행 필요)", found: [] };

  const headers = (rows[0] as unknown[]).map((h) => str(h));
  const dataRows = rows.slice(1) as (string | number | null)[][];

  // 헤더 이름으로 열 찾기
  const COL_PRODCD   = findCol(headers, ["품목코드"],    ["대표품목코드"]);
  const COL_UNIT     = findCol(headers, ["단위"]);
  const COL_SPEC     = findCol(headers, ["규격정보", "규격"]);
  const COL_STORAGE  = findCol(headers, ["냉동/냉장명", "냉동냉장명", "냉동", "보관"]);
  const COL_COUNTRY  = findCol(headers, ["국가명", "국가"]);
  const COL_BRAND    = findCol(headers, ["브랜드"]);
  const COL_CATEGORY = findCol(headers, ["카테고리명", "카테고리"]);
  const COL_PRICE    = findCol(headers, ["소비자가", "소비자가격"]);
  const COL_REPCD    = findCol(headers, ["대표품목코드"]);
  const COL_REPNM    = findCol(headers, ["대표품목명"]);

  // 필수 열 누락 확인
  const REQUIRED: [string, number][] = [
    ["대표품목코드", COL_REPCD],
    ["대표품목명",   COL_REPNM],
    ["품목코드",     COL_PRODCD],
    ["단위",         COL_UNIT],
    ["소비자가",     COL_PRICE],
  ];
  const missing = REQUIRED.filter(([, idx]) => idx === -1).map(([name]) => name);
  if (missing.length > 0) {
    return {
      error: `필수 열을 찾을 수 없습니다: ${missing.join(", ")}`,
      found: headers.filter(Boolean),
    };
  }

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
  for (const [id, prows] of groups) {
    const first = prows[0];
    const name = str(first[COL_REPNM]);
    const units: ProductUnit[] = prows.map((row) => ({
      prodCd: String(parseInt(String(row[COL_PRODCD]))).padStart(8, "0"),
      unit:   COL_UNIT   !== -1 ? str(row[COL_UNIT])   : "",
      price:  COL_PRICE  !== -1 ? parseInt(String(row[COL_PRICE])) || 0 : 0,
      spec:   COL_SPEC   !== -1 ? str(row[COL_SPEC])   : "",
    }));
    units.sort((a, b) => unitSortKey(a.unit) - unitSortKey(b.unit));

    products.push({
      id,
      name,
      country:  COL_COUNTRY  !== -1 ? str(first[COL_COUNTRY])  : "",
      brand:    COL_BRAND    !== -1 ? str(first[COL_BRAND])    : "",
      category: COL_CATEGORY !== -1 ? str(first[COL_CATEGORY]) : "",
      storage:  COL_STORAGE  !== -1 ? str(first[COL_STORAGE])  : "",
      imageFile: null,
      units,
    });
  }

  products.sort((a, b) => a.id - b.id);
  return { products };
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;
    if (!file) return NextResponse.json({ error: "file required" }, { status: 400 });

    const buffer = await file.arrayBuffer();
    const parsed = parseExcel(buffer);
    if ("error" in parsed) {
      return NextResponse.json({ error: parsed.error, found: parsed.found }, { status: 400 });
    }
    const newProducts = parsed.products;
    if (newProducts.length === 0) {
      return NextResponse.json({ error: "유효한 품목 데이터가 없습니다 (대표품목코드 + 소비자가 > 0 행 필요)" }, { status: 400 });
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
