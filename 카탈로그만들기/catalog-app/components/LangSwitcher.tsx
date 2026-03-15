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
    <div className="flex gap-1 shrink-0">
      {LANGS.map((l) => (
        <button
          key={l.code}
          onClick={() => setLang(l.code)}
          title={l.label}
          className={`w-8 h-8 rounded-lg text-lg flex items-center justify-center transition-colors ${
            lang === l.code
              ? "bg-emerald-600 ring-2 ring-emerald-400"
              : "bg-white border border-gray-200 hover:border-emerald-400"
          }`}
        >
          {l.flag}
        </button>
      ))}
    </div>
  );
}
