import { NextRequest, NextResponse } from "next/server";
import { put } from "@vercel/blob";

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const file = formData.get("file") as File | null;
  const productId = formData.get("productId") as string | null;

  if (!file || !productId) {
    return NextResponse.json({ error: "file and productId required" }, { status: 400 });
  }

  const ext = file.name.split(".").pop()?.toLowerCase() ?? "jpg";
  const pathname = `products/${productId}.${ext}`;

  const blob = await put(pathname, file, { access: "public", allowOverwrite: true });

  return NextResponse.json({ url: blob.url });
}
