"use client";
import { useState, useMemo } from "react";
import ProductCard from "@/components/ProductCard";
import CartDrawer from "@/components/CartDrawer";
import { useCartStore } from "@/store/cartStore";
import type { Product, Meta } from "@/lib/types";

const PAGE_SIZE = 24;

interface Props {
  products: Product[];
  meta: Meta;
}

export default function CatalogClient({ products, meta }: Props) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [country, setCountry] = useState("");
  const [storage, setStorage] = useState("");
  const [page, setPage] = useState(1);
  const [cartOpen, setCartOpen] = useState(false);
  const { items } = useCartStore();
  const cartCount = items.reduce((s, i) => s + i.qty, 0);

  const filtered = useMemo(() => {
    return products.filter((p) => {
      if (search && !p.name.toLowerCase().includes(search.toLowerCase()) && !p.brand.toLowerCase().includes(search.toLowerCase())) return false;
      if (category && p.category !== category) return false;
      if (country && p.country !== country) return false;
      if (storage && p.storage !== storage) return false;
      return true;
    });
  }, [products, search, category, country, storage]);

  const paginated = useMemo(() => filtered.slice(0, page * PAGE_SIZE), [filtered, page]);

  const resetFilters = () => { setSearch(""); setCategory(""); setCountry(""); setStorage(""); setPage(1); };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <h1 className="text-xl font-bold text-emerald-700 shrink-0">그라미스 카탈로그</h1>
          <div className="flex-1">
            <input type="text" placeholder="상품명, 브랜드 검색..." value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full border border-gray-200 rounded-full px-4 py-1.5 text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>
          <button onClick={() => setCartOpen(true)}
            className="relative shrink-0 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full w-10 h-10 flex items-center justify-center transition-colors"
          >
            <span className="text-xl">🛒</span>
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                {cartCount > 99 ? "99+" : cartCount}
              </span>
            )}
          </button>
        </div>
      </header>
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex gap-2 mb-4 flex-wrap items-center">
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            className="border border-gray-200 rounded-full px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">전체 카테고리</option>
            {meta.categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={country} onChange={(e) => { setCountry(e.target.value); setPage(1); }}
            className="border border-gray-200 rounded-full px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">전체 국가</option>
            {meta.countries.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={storage} onChange={(e) => { setStorage(e.target.value); setPage(1); }}
            className="border border-gray-200 rounded-full px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">전체 보관</option>
            {meta.storages.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          {(search || category || country || storage) && (
            <button onClick={resetFilters} className="text-sm text-gray-400 hover:text-red-500 px-2">필터 초기화 ×</button>
          )}
          <span className="ml-auto text-sm text-gray-400">{filtered.length.toLocaleString()}개 상품</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
          {paginated.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
        {paginated.length === 0 && (
          <div className="text-center py-20 text-gray-400">검색 결과가 없습니다.</div>
        )}
        {paginated.length < filtered.length && (
          <div className="flex justify-center mt-8">
            <button onClick={() => setPage((p) => p + 1)}
              className="bg-white border border-gray-200 hover:border-emerald-400 text-gray-600 hover:text-emerald-600 px-8 py-2.5 rounded-full text-sm font-medium transition-colors"
            >
              더 보기 ({filtered.length - paginated.length}개 남음)
            </button>
          </div>
        )}
      </div>
      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
    </div>
  );
}
