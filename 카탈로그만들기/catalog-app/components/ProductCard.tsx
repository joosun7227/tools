"use client";
import { useState } from "react";
import { useCartStore } from "@/store/cartStore";
import type { Product, Lang } from "@/lib/types";

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
  isNew?: boolean;
}

export default function ProductCard({ product, lang = "ko", translatedName, isNew = false }: ProductCardProps) {
  const { add, setQty, items } = useCartStore();
  const [selectedIdx, setSelectedIdx] = useState(0);
  const selectedUnit = product.units[selectedIdx];
  const inCart = items.find((i) => i.id === selectedUnit.prodCd);

  const imgSrc = product.imageFile ? `/images/${encodeURIComponent(product.imageFile)}` : null;
  const [failed, setFailed] = useState(false);

  const displayName = (lang !== "ko" && translatedName) ? translatedName : product.name;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-shadow">
      <div className="relative bg-gray-50 h-44 flex items-center justify-center p-3">
        {imgSrc && !failed ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imgSrc}
            alt={product.name}
            className="max-h-full max-w-full object-contain"
            loading="lazy"
            onError={() => setFailed(true)}
          />
        ) : (
          <div className="text-gray-300 text-5xl select-none">📦</div>
        )}
        {isNew && (
          <span className="absolute top-2 left-2 text-xs px-2 py-0.5 rounded-full font-bold bg-amber-400 text-white">
            NEW
          </span>
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

        {inCart ? (
          <div className="mt-auto flex items-center gap-1 bg-emerald-600 rounded-xl px-2 py-1.5">
            <button
              onClick={() => setQty(inCart.id, inCart.qty - 1)}
              className="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold flex items-center justify-center text-base shrink-0"
            >
              -
            </button>
            <input
              type="number"
              inputMode="numeric"
              min={1}
              value={inCart.qty}
              onChange={(e) => {
                const v = parseInt(e.target.value);
                if (!isNaN(v) && v >= 1) setQty(inCart.id, v);
              }}
              className="flex-1 text-center text-sm font-bold bg-transparent text-white focus:outline-none min-w-0"
            />
            <button
              onClick={() => setQty(inCart.id, inCart.qty + 1)}
              className="w-7 h-7 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold flex items-center justify-center text-base shrink-0"
            >
              +
            </button>
          </div>
        ) : (
          <button
            onClick={() => add({
              productId: product.id,
              name: product.name,
              prodCd: selectedUnit.prodCd,
              unit: selectedUnit.unit,
              price: selectedUnit.price,
              spec: selectedUnit.spec,
            })}
            className="mt-auto w-full py-2.5 rounded-xl font-bold text-sm tracking-wide transition-colors bg-gray-900 hover:bg-gray-700 text-white"
          >
            Order
          </button>
        )}
      </div>
    </div>
  );
}
