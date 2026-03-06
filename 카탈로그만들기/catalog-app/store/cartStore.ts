import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { CartItem } from "@/lib/types";

interface AddPayload {
  productId: number;
  name: string;
  prodCd: string;
  unit: string;
  price: number;
  spec: string;
}

interface CartStore {
  items: CartItem[];
  add: (payload: AddPayload) => void;
  remove: (id: string) => void;
  setQty: (id: string, qty: number) => void;
  clear: () => void;
  total: () => number;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      add: (payload) => {
        set((s) => {
          const existing = s.items.find((i) => i.id === payload.prodCd);
          if (existing) {
            return { items: s.items.map((i) => i.id === payload.prodCd ? { ...i, qty: i.qty + 1 } : i) };
          }
          return { items: [...s.items, { ...payload, id: payload.prodCd, qty: 1 }] };
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
