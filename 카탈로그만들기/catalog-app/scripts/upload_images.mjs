// 스크립트: public/images/ 의 모든 이미지를 Vercel Blob에 업로드
import { put, list } from "@vercel/blob";
import { readFileSync, readdirSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const IMAGE_DIR = path.join(__dirname, "../public/images");
const TOKEN = "vercel_blob_rw_4Cg4QXoKlCl6ovc0_fMqPE39GBg4MuhyI6Oub0eoslrniWz";
const CONCURRENCY = 5; // 동시 업로드 수

async function getExistingBlobs() {
  const existing = new Set();
  let cursor;
  do {
    const result = await list({ prefix: "products/", token: TOKEN, cursor, limit: 1000 });
    for (const b of result.blobs) {
      existing.add(path.basename(b.pathname));
    }
    cursor = result.cursor;
  } while (cursor);
  return existing;
}

async function uploadFile(filename) {
  const filePath = path.join(IMAGE_DIR, filename);
  const data = readFileSync(filePath);
  const ext = path.extname(filename).toLowerCase().slice(1);
  const contentType = ext === "png" ? "image/png" : "image/jpeg";
  await put(`products/${filename}`, data, {
    access: "public",
    token: TOKEN,
    allowOverwrite: true,
    contentType,
  });
}

async function runWithConcurrency(tasks, limit) {
  let i = 0;
  let done = 0;
  const total = tasks.length;
  async function worker() {
    while (i < tasks.length) {
      const task = tasks[i++];
      await task();
      done++;
      if (done % 50 === 0 || done === total) {
        process.stdout.write(`\r진행: ${done}/${total}`);
      }
    }
  }
  await Promise.all(Array.from({ length: limit }, worker));
}

async function main() {
  const files = readdirSync(IMAGE_DIR).filter(f => /\.(jpg|jpeg|png)$/i.test(f));
  console.log(`총 이미지: ${files.length}개`);

  console.log("기존 Blob 목록 조회 중...");
  const existing = await getExistingBlobs();
  console.log(`이미 업로드됨: ${existing.size}개`);

  const toUpload = files.filter(f => !existing.has(f));
  console.log(`업로드 필요: ${toUpload.length}개\n`);

  if (toUpload.length === 0) {
    console.log("모두 이미 업로드되어 있습니다!");
    return;
  }

  const tasks = toUpload.map(f => () => uploadFile(f));
  await runWithConcurrency(tasks, CONCURRENCY);

  console.log(`\n\n완료! ${toUpload.length}개 업로드됨`);
}

main().catch(e => { console.error("\n에러:", e.message); process.exit(1); });
