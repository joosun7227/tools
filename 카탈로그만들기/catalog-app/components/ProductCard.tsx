"use client";
import { useCartStore } from "@/store/cartStore";
import type { Product } from "@/lib/types";

const STORAGE_COLOR: Record<string, string> = {
  "Dry 상온보관": "bg-amber-100 text-amber-700",
  "Frozen 냉동보관": "bg-blue-100 text-blue-700",
  "Cool 냉장보관": "bg-cyan-100 text-cyan-700",
};

export default function ProductCard({ product }: { product: Product }) {
  const { add, items } = useCartStore();
  const inCart = items.find((i) => i.id === product.id);
  const imgSrc = product.imageFile
    ? `/api/image/${encodeURIComponent(product.imageFile)}`
    : null;

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
          />
        ) : (
          <div className="text-gray-300 text-5xl select-none">📦</div>
        )}
        <span className={`absolute top-2 right-2 text-xs px-2 py-0.5 rounded-full font-medium ${STORAGE_COLOR[product.storage] ?? "bg-gray-100 text-gray-500"}`}>
          {product.storage.split(" ")[0]}
        </span>
      </div>

      <div className="p-3 flex flex-col flex-1">
        <p className="text-xs text-gray-400 mb-0.5">{product.brand || product.country}</p>
        <p className="text-sm font-semibold text-gray-800 leading-tight line-clamp-2 flex-1">{product.name}</p>
        <p className="text-xs text-gray-400 mt-1 mb-2">{product.spec}</p>

        <div className="flex items-center justify-between mt-auto">
          <span className="text-base font-bold text-emerald-600">
            {product.price.toLocaleString()}원
          </span>
          <button
            onClick={() => add(product)}
            className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
              inCart
                ? "bg-emerald-600 text-white"
                : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
            }`}
          >
            {inCart ? `${inCart.qty}개 담음` : "담기"}
          </button>
        </div>
      </div>
    </div>
  );
}
