import { NextRequest, NextResponse } from "next/server";
import { readFileSync } from "fs";
import path from "path";

const BLOB_PATH = "data/translations.json";

async function getBlobTranslations(): Promise<Record<string, { ko: string; th: string; vi: string; en: string }> | null> {
  const token = process.env.BLOB_READ_WRITE_TOKEN;
  if (!token) return null;

  try {
    // List blobs to find translations.json
    const { list } = await import("@vercel/blob");
    const { blobs } = await list({ prefix: BLOB_PATH, token });
    if (blobs.length === 0) return null;

    const blobUrl = blobs[0].url;
    const res = await fetch(blobUrl, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

async function saveBlobTranslations(data: Record<string, { ko: string; th: string; vi: string; en: string }>) {
  const token = process.env.BLOB_READ_WRITE_TOKEN;
  if (!token) throw new Error("BLOB_READ_WRITE_TOKEN not set");

  const { put } = await import("@vercel/blob");
  const content = JSON.stringify(data, null, 2);
  await put(BLOB_PATH, content, {
    access: "public",
    addRandomSuffix: false,
    token,
    contentType: "application/json",
  });
}

function getLocalTranslations(): Record<string, { ko: string; th: string; vi: string; en: string }> {
  const filePath = path.join(process.cwd(), "data", "translations.json");
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

export async function GET() {
  try {
    // Try Blob first, fallback to local
    const blobData = await getBlobTranslations();
    const data = blobData ?? getLocalTranslations();
    return NextResponse.json(data);
  } catch (err) {
    console.error("GET /api/admin/translation error:", err);
    return NextResponse.json({ error: "Failed to load translations" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { productId?: string; lang?: string; value?: string; bulk?: Record<string, { ko: string; th: string; vi: string; en: string }> };

    // Load current translations
    const blobData = await getBlobTranslations();
    const current = blobData ?? getLocalTranslations();

    if (body.bulk) {
      // Bulk update: merge provided data
      const merged = { ...current, ...body.bulk };
      await saveBlobTranslations(merged);
      return NextResponse.json({ ok: true, updated: Object.keys(body.bulk).length });
    }

    // Single update
    const { productId, lang, value } = body;
    if (!productId || !lang || value === undefined) {
      return NextResponse.json({ error: "productId, lang, value required" }, { status: 400 });
    }
    if (!["ko", "th", "vi", "en"].includes(lang)) {
      return NextResponse.json({ error: "Invalid lang" }, { status: 400 });
    }

    if (!current[productId]) {
      current[productId] = { ko: "", th: "", vi: "", en: "" };
    }
    current[productId][lang as "ko" | "th" | "vi" | "en"] = value;

    await saveBlobTranslations(current);
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("POST /api/admin/translation error:", err);
    return NextResponse.json({ error: "Failed to save translation" }, { status: 500 });
  }
}
