import { list, put } from "@vercel/blob";
import { readFileSync, writeFileSync, existsSync } from "fs";
import path from "path";
import { NextResponse } from "next/server";

export interface Inquiry {
  id: string;
  name: string;
  phone: string;
  memo: string;
  createdAt: string;
}

const BLOB_KEY = "data/inquiries.json";
const LOCAL_PATH = path.join(process.cwd(), "data", "inquiries.json");
const token = process.env.BLOB_READ_WRITE_TOKEN;

async function readInquiries(): Promise<Inquiry[]> {
  // Try Blob first
  if (token) {
    try {
      const { blobs } = await list({ prefix: BLOB_KEY, token });
      if (blobs.length > 0) {
        const res = await fetch(blobs[0].url, { cache: "no-store" });
        if (res.ok) return await res.json();
      }
    } catch {
      // fall through
    }
  }
  // Fallback: local file
  if (existsSync(LOCAL_PATH)) {
    return JSON.parse(readFileSync(LOCAL_PATH, "utf-8"));
  }
  return [];
}

async function writeInquiries(data: Inquiry[]): Promise<void> {
  const json = JSON.stringify(data, null, 2);
  if (token) {
    await put(BLOB_KEY, json, {
      access: "public",
      contentType: "application/json",
      token,
      allowOverwrite: true,
    });
    return;
  }
  // Fallback: local file (dev only)
  writeFileSync(LOCAL_PATH, json, "utf-8");
}

export async function GET() {
  try {
    const inquiries = await readInquiries();
    return NextResponse.json(inquiries);
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { name, phone, memo } = body as { name: string; phone: string; memo: string };

    if (!name && !phone) {
      return NextResponse.json({ error: "성명 또는 연락처를 입력하세요." }, { status: 400 });
    }

    const existing = await readInquiries();
    const newItem: Inquiry = {
      id: Date.now().toString(),
      name: (name ?? "").trim(),
      phone: (phone ?? "").trim(),
      memo: (memo ?? "").trim(),
      createdAt: new Date(Date.now() + 9 * 60 * 60 * 1000).toISOString(),
    };

    await writeInquiries([newItem, ...existing]);
    return NextResponse.json({ success: true });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
