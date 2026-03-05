import { NextResponse } from "next/server";
import { readFileSync } from "fs";
import path from "path";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const dataPath = path.join(process.cwd(), "data", "products.json");
    const metaPath = path.join(process.cwd(), "data", "meta.json");
    const products = JSON.parse(readFileSync(dataPath, "utf-8"));
    const meta = JSON.parse(readFileSync(metaPath, "utf-8"));
    return NextResponse.json({ products, meta });
  } catch {
    return NextResponse.json({ error: "데이터 로드 실패" }, { status: 500 });
  }
}
