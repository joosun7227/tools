"use client";
import { useState, useMemo } from "react";
import ProductCard from "@/components/ProductCard";
import CartDrawer from "@/components/CartDrawer";
import LangSwitcher from "@/components/LangSwitcher";
import { useCartStore } from "@/store/cartStore";
import { useLangStore } from "@/store/langStore";
import type { Product, Meta, Translations } from "@/lib/types";

const PAGE_SIZE = 100;

interface Props {
  products: Product[];
  meta: Meta;
  translations: Translations;
}

export default function CatalogClient({ products, meta, translations }: Props) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [country, setCountry] = useState("");
  const [storage, setStorage] = useState("");
  const [page, setPage] = useState(1);
  const [cartOpen, setCartOpen] = useState(false);
  const { items } = useCartStore();
  const { lang } = useLangStore();
  const cartCount = items.reduce((s, i) => s + i.qty, 0);

  const filtered = useMemo(() => {
    return products.filter((p) => {
      if (search) {
        const t = translations[String(p.id)];
        const displayName = (t && lang !== "ko" && t[lang]) ? t[lang] : (t?.ko || p.name);
        if (
          !displayName.toLowerCase().includes(search.toLowerCase()) &&
          !p.name.toLowerCase().includes(search.toLowerCase()) &&
          !p.brand.toLowerCase().includes(search.toLowerCase())
        ) return false;
      }
      if (category && p.category !== category) return false;
      if (country && p.country !== country) return false;
      if (storage && p.storage !== storage) return false;
      return true;
    });
  }, [products, search, category, country, storage, translations, lang]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated = useMemo(
    () => filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [filtered, page]
  );

  const resetFilters = () => { setSearch(""); setCategory(""); setCountry(""); setStorage(""); setPage(1); };
  const goToPage = (p: number) => {
    setPage(p);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-3 py-2.5 flex items-center gap-2">
          <h1 className="text-base font-bold text-emerald-700 shrink-0">예주나라</h1>
          <div className="flex-1 min-w-0">
            <input type="text" placeholder="상품명, 브랜드 검색..." value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full border border-gray-200 rounded-full px-3 py-2 text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>
          <LangSwitcher />
          <button onClick={() => setCartOpen(true)}
            className="relative shrink-0 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full w-10 h-10 flex items-center justify-center transition-colors"
          >
            <span className="text-lg">🛒</span>
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                {cartCount > 99 ? "99+" : cartCount}
              </span>
            )}
          </button>
        </div>
        {/* 필터 바 */}
        <div className="max-w-7xl mx-auto px-3 pb-2 flex gap-2 overflow-x-auto scrollbar-none">
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            className="border border-gray-200 rounded-full px-3 py-1.5 text-xs bg-white focus:outline-none focus:border-emerald-400 shrink-0"
          >
            <option value="">전체 카테고리</option>
            {meta.categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={country} onChange={(e) => { setCountry(e.target.value); setPage(1); }}
            className="border border-gray-200 rounded-full px-3 py-1.5 text-xs bg-white focus:outline-none focus:border-emerald-400 shrink-0"
          >
            <option value="">전체 국가</option>
            {meta.countries.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={storage} onChange={(e) => { setStorage(e.target.value); setPage(1); }}
            className="border border-gray-200 rounded-full px-3 py-1.5 text-xs bg-white focus:outline-none focus:border-emerald-400 shrink-0"
          >
            <option value="">전체 보관</option>
            {meta.storages.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          {(search || category || country || storage) && (
            <button onClick={resetFilters} className="text-xs text-gray-400 hover:text-red-500 px-2 shrink-0">초기화 ×</button>
          )}
          <span className="ml-auto text-xs text-gray-400 shrink-0 self-center">{filtered.length.toLocaleString()}개</span>
        </div>
      </header>
      <div className="max-w-7xl mx-auto px-3 py-3">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
          {paginated.map((p) => {
            const t = translations[String(p.id)];
            const translatedName = t && lang !== "ko" && t[lang] ? t[lang] : undefined;
            return (
              <ProductCard
                key={p.id}
                product={p}
                lang={lang}
                translatedName={translatedName}
              />
            );
          })}
        </div>

        {paginated.length === 0 && (
          <div className="text-center py-20 text-gray-400">검색 결과가 없습니다.</div>
        )}

        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-1 mt-8 flex-wrap">
            <button
              onClick={() => goToPage(page - 1)}
              disabled={page === 1}
              className="px-3 py-2 rounded-lg border text-sm font-medium disabled:opacity-30 hover:border-emerald-400 hover:text-emerald-600 transition-colors"
            >
              ← 이전
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter((p) => p === 1 || p === totalPages || Math.abs(p - page) <= 2)
              .reduce<(number | "...")[]>((acc, p, idx, arr) => {
                if (idx > 0 && p - (arr[idx - 1] as number) > 1) acc.push("...");
                acc.push(p);
                return acc;
              }, [])
              .map((p, i) =>
                p === "..." ? (
                  <span key={`ellipsis-${i}`} className="px-2 text-gray-400">…</span>
                ) : (
                  <button
                    key={p}
                    onClick={() => goToPage(p as number)}
                    className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                      p === page
                        ? "bg-emerald-600 text-white"
                        : "border hover:border-emerald-400 hover:text-emerald-600"
                    }`}
                  >
                    {p}
                  </button>
                )
              )}

            <button
              onClick={() => goToPage(page + 1)}
              disabled={page === totalPages}
              className="px-3 py-2 rounded-lg border text-sm font-medium disabled:opacity-30 hover:border-emerald-400 hover:text-emerald-600 transition-colors"
            >
              다음 →
            </button>
          </div>
        )}
      </div>
      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
    </div>
  );
}
