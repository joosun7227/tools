import { create } from "zustand";
import type { Translations } from "@/lib/types";

interface TranslationsStore {
  translations: Translations;
  setTranslations: (t: Translations) => void;
}

export const useTranslationsStore = create<TranslationsStore>((set) => ({
  translations: {},
  setTranslations: (translations) => set({ translations }),
}));
