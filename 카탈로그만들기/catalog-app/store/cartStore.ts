import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { CartItem, Product } from "@/lib/types";

interface CartStore {
  items: CartItem[];
  add: (product: Product) => void;
  remove: (id: number) => void;
  setQty: (id: number, qty: number) => void;
  clear: () => void;
  total: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      add: (product) => {
        set((s) => {
          const existing = s.items.find((i) => i.id === product.id);
          if (existing) {
            return { items: s.items.map((i) => i.id === product.id ? { ...i, qty: i.qty + 1 } : i) };
          }
          return { items: [...s.items, { ...product, qty: 1 }] };
        });
      },
      remove: (id) => set((s) => ({ items: s.items.filter((i) => i.id !== id) })),
      setQty: (id, qty) => {
        if (qty <= 0) {
          set((s) => ({ items: s.items.filter((i) => i.id !== id) }));
        } else {
          set((s) => ({ items: s.items.map((i) => i.id === id ? { ...i, qty } : i) }));
        }
      },
      clear: () => set({ items: [] }),
      total: () => get().items.reduce((sum, i) => sum + i.price * i.qty, 0),
    }),
    { name: "gromise-cart" }
  )
);
