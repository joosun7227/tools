"use client";
import { useState } from "react";
import { useCartStore } from "@/store/cartStore";
import type { Product, Lang } from "@/lib/types";

const BLOB_BASE = process.env.NEXT_PUBLIC_BLOB_STORE_URL ?? "";

const STORAGE_COLOR: Record<string, string> = {
  "Dry 상온보관": "bg-amber-100 text-amber-700",
  "Frozen 냉동보관": "bg-blue-100 text-blue-700",
  "Cool 냉장보관": "bg-cyan-100 text-cyan-700",
};

function BoldQty({ spec }: { spec: string }) {
  const result: React.ReactNode[] = [];
  const regex = /(\d+)(EA)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = regex.exec(spec)) !== null) {
    if (m.index > last) result.push(spec.slice(last, m.index));
    result.push(<strong key={m.index}>{m[1]}</strong>);
    result.push(m[2]);
    last = m.index + m[0].length;
  }
  if (last < spec.length) result.push(spec.slice(last));
  return <>{result}</>;
}

interface ProductCardProps {
  product: Product;
  lang?: Lang;
  translatedName?: string;
}

export default function ProductCard({ product, lang = "ko", translatedName }: ProductCardProps) {
  const { add, items } = useCartStore();
  const [selectedIdx, setSelectedIdx] = useState(0);
  const selectedUnit = product.units[selectedIdx];
  const inCart = items.find((i) => i.id === selectedUnit.prodCd);
  const [imgErr, setImgErr] = useState(false);
  // blob 이미지 우선, 없으면 public/images 폴백
  const blobSrc = BLOB_BASE ? `${BLOB_BASE}/products/${product.id}.jpg` : null;
  const staticSrc = product.imageFile ? `/images/${encodeURIComponent(product.imageFile)}` : null;
  const imgSrc = imgErr ? staticSrc : (blobSrc ?? staticSrc);

  // Display name: use translatedName if available, fallback to product.name
  const displayName = (lang !== "ko" && translatedName) ? translatedName : product.name;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-shadow">
      <div className="relative bg-gray-50 h-44 flex items-center justify-center p-3">
        {imgSrc ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imgSrc}
            alt={product.name}
            className="max-h-full max-w-full object-contain"
            loading="lazy"
            onError={() => { if (!imgErr) setImgErr(true); }}
          />
        ) : (
          <div className="text-gray-300 text-5xl select-none">📦</div>
        )}
        <span className={`absolute top-2 right-2 text-xs px-2 py-0.5 rounded-full font-medium ${STORAGE_COLOR[product.storage] ?? "bg-gray-100 text-gray-500"}`}>
          {product.storage.split(" ")[0]}
        </span>
      </div>

      <div className="p-3 flex flex-col flex-1 gap-1">
        <p className="text-xs text-gray-400">{product.brand || product.country}</p>
        <p className="text-sm font-semibold text-gray-800 leading-snug line-clamp-2">{displayName}</p>
        <p className="text-sm text-gray-600 leading-snug"><BoldQty spec={selectedUnit.spec} /></p>

        {product.units.length > 1 && (
          <div className="flex gap-1 flex-wrap mt-1">
            {product.units.map((u, i) => (
              <button
                key={u.prodCd}
                onClick={() => setSelectedIdx(i)}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  i === selectedIdx
                    ? "bg-emerald-600 text-white border-emerald-600"
                    : "bg-white text-gray-500 border-gray-200 hover:border-emerald-400"
                }`}
              >
                {u.unit}
              </button>
            ))}
          </div>
        )}

        <button
          onClick={() => add({
            productId: product.id,
            name: product.name,
            prodCd: selectedUnit.prodCd,
            unit: selectedUnit.unit,
            price: selectedUnit.price,
            spec: selectedUnit.spec,
          })}
          className={`mt-auto w-full py-2.5 rounded-xl font-bold text-sm tracking-wide transition-colors ${
            inCart
              ? "bg-emerald-600 text-white"
              : "bg-gray-900 hover:bg-gray-700 text-white"
          }`}
        >
          {inCart ? `Order (${inCart.qty})` : "Order"}
        </button>
      </div>
    </div>
  );
}
