import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Lang } from "@/lib/types";

interface LangStore {
  lang: Lang;
  setLang: (lang: Lang) => void;
}

export const useLangStore = create<LangStore>()(
  persist(
    (set) => ({
      lang: "ko",
      setLang: (lang) => set({ lang }),
    }),
    { name: "catalog-lang" }
  )
);
