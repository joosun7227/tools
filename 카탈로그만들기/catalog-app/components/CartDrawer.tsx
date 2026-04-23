"use client";
import { useCartStore } from "@/store/cartStore";
import { useLangStore } from "@/store/langStore";
import { useTranslationsStore } from "@/store/translationsStore";
import { useRouter } from "next/navigation";
import { t } from "@/lib/uiText";

export default function CartDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { items, setQty, remove, clear } = useCartStore();
  const { lang } = useLangStore();
  const { translations } = useTranslationsStore();
  const router = useRouter();

  const getDisplayName = (productId: number, fallback: string) => {
    const tr = translations[String(productId)];
    return (lang !== "ko" && tr?.[lang]) ? tr[lang] : fallback;
  };

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/30 z-40" onClick={onClose} />}
      <div
        className={`fixed top-0 right-0 h-full w-80 bg-white z-50 shadow-2xl flex flex-col transition-transform duration-300 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-bold text-lg">{t("cart", lang)} ({items.length})</h2>
          <div className="flex items-center gap-2">
            {items.length > 0 && (
              <button
                onClick={() => { if (confirm(t("clearConfirm", lang))) clear(); }}
                className="text-xs text-red-400 hover:text-red-600 border border-red-200 hover:border-red-400 px-2 py-1 rounded-full transition-colors"
              >
                {t("clearAll", lang)}
              </button>
            )}
            <button onClick={onClose} className="text-gray-500 hover:text-gray-800 text-2xl leading-none">&times;</button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {items.length === 0 && (
            <p className="text-gray-400 text-center mt-10 text-sm">{t("cartEmpty", lang)}</p>
          )}
          {items.map((item) => (
            <div key={item.id} className="flex gap-3 items-start border-b pb-3">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 line-clamp-2">{getDisplayName(item.productId, item.name)}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  <span className="inline-block bg-emerald-50 text-emerald-700 rounded px-1 mr-1 font-medium">{item.unit}</span>
                  {item.spec}
                </p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <button onClick={() => setQty(item.id, item.qty - 1)} className="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-sm font-bold flex items-center justify-center">-</button>
                <span className="w-7 text-center text-sm font-semibold">{item.qty}</span>
                <button onClick={() => setQty(item.id, item.qty + 1)} className="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-sm font-bold flex items-center justify-center">+</button>
                <button onClick={() => remove(item.id)} className="ml-1 text-gray-300 hover:text-red-400 text-lg leading-none">&times;</button>
              </div>
            </div>
          ))}
        </div>

        {items.length > 0 && (
          <div className="p-4 border-t">
            <button
              onClick={() => { onClose(); router.push("/order"); }}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 rounded-xl transition-colors"
            >
              {t("order", lang)} ({items.reduce((s, i) => s + i.qty, 0)})
            </button>
          </div>
        )}
      </div>
    </>
  );
}
