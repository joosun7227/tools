import { put } from "@vercel/blob";
import { readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "../data");
const TOKEN = "vercel_blob_rw_4Cg4QXoKlCl6ovc0_fMqPE39GBg4MuhyI6Oub0eoslrniWz";

const files = ["products.json", "meta.json"];
for (const f of files) {
  const body = readFileSync(path.join(DATA_DIR, f));
  const res = await put(`data/${f}`, body, {
    access: "public",
    token: TOKEN,
    allowOverwrite: true,
    contentType: "application/json; charset=utf-8",
    addRandomSuffix: false,
  });
  console.log(`uploaded ${f} -> ${res.url} (${body.length}B)`);
}
