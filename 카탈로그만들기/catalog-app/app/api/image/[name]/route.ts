import { NextResponse } from "next/server";
import { readFileSync, existsSync } from "fs";

const IMAGE_DIR = "C:/Users/User/OneDrive/문서/3yejoo/그라미스Gromise/2.쇼핑몰/쇼핑몰_상품구성/그라미스상품사진/그라미스상품사진_최종본_260128";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ name: string }> }
) {
  const { name } = await params;
  const decoded = decodeURIComponent(name);
  const filePath = IMAGE_DIR + "/" + decoded;

  if (!existsSync(filePath)) {
    return new NextResponse(null, { status: 404 });
  }

  const buffer = readFileSync(filePath);
  return new NextResponse(buffer, {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=86400",
    },
  });
}
