"use client";
import { useLangStore } from "@/store/langStore";
import type { Lang } from "@/lib/types";

const LANGS: { code: Lang; label: string; flag: string }[] = [
  { code: "ko", label: "한국어", flag: "🇰🇷" },
  { code: "th", label: "ภาษาไทย", flag: "🇹🇭" },
  { code: "vi", label: "Tiếng Việt", flag: "🇻🇳" },
];

export default function LangSwitcher() {
  const { lang, setLang } = useLangStore();
  return (
    <div className="flex gap-1">
      {LANGS.map((l) => (
        <button
          key={l.code}
          onClick={() => setLang(l.code)}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            lang === l.code
              ? "bg-emerald-600 text-white"
              : "bg-white border border-gray-200 text-gray-600 hover:border-emerald-400"
          }`}
        >
          <span>{l.flag}</span>
          <span>{l.label}</span>
        </button>
      ))}
    </div>
  );
}
