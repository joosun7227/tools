import { list } from "@vercel/blob";
const TOKEN = "vercel_blob_rw_4Cg4QXoKlCl6ovc0_fMqPE39GBg4MuhyI6Oub0eoslrniWz";
const { blobs } = await list({ prefix: "data/", token: TOKEN });
for (const b of blobs) {
  console.log(`${b.pathname}  ${b.size}B  ${b.uploadedAt}`);
}
console.log(`total: ${blobs.length}`);
