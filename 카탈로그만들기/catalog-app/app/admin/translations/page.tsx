"use client";
import { useState, useEffect, useMemo } from "react";

interface TranslationEntry {
  ko: string;
  th: string;
  vi: string;
  en: string;
}

interface EditMap {
  [productId: string]: string;
}

type LangTab = "th" | "vi";

export default function TranslationsAdminPage() {
  const [translations, setTranslations] = useState<Record<string, TranslationEntry>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");
  const [langTab, setLangTab] = useState<LangTab>("th");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "missing">("missing");
  const [edits, setEdits] = useState<EditMap>({});

  useEffect(() => {
    fetch("/api/admin/translation")
      .then((r) => r.json())
      .then((data) => {
        setTranslations(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const entries = useMemo(() => {
    return Object.entries(translations)
      .filter(([, t]) => {
        const matchSearch = !search || t.ko.toLowerCase().includes(search.toLowerCase());
        const matchFilter = filter === "all" || !t[langTab];
        return matchSearch && matchFilter;
      })
      .sort(([a], [b]) => Number(a) - Number(b));
  }, [translations, search, filter, langTab]);

  const missingCount = useMemo(() => {
    return Object.values(translations).filter((t) => !t[langTab]).length;
  }, [translations, langTab]);

  const handleEdit = (pid: string, value: string) => {
    setEdits((prev) => ({ ...prev, [`${pid}_${langTab}`]: value }));
  };

  const getEditValue = (pid: string, original: string) => {
    const key = `${pid}_${langTab}`;
    return key in edits ? edits[key] : original;
  };

  const saveSingle = async (pid: string) => {
    const key = `${pid}_${langTab}`;
    const value = edits[key] ?? translations[pid]?.[langTab] ?? "";
    try {
      const res = await fetch("/api/admin/translation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ productId: pid, lang: langTab, value }),
      });
      if (res.ok) {
        setTranslations((prev) => ({
          ...prev,
          [pid]: { ...prev[pid], [langTab]: value },
        }));
        const newEdits = { ...edits };
        delete newEdits[key];
        setEdits(newEdits);
        setSaveMsg(`저장됨: ID ${pid}`);
        setTimeout(() => setSaveMsg(""), 2000);
      }
    } catch {
      setSaveMsg("저장 실패");
      setTimeout(() => setSaveMsg(""), 2000);
    }
  };

  const saveAll = async () => {
    setSaving(true);
    setSaveMsg("");
    // Build bulk update from edits
    const bulk: Record<string, TranslationEntry> = {};
    for (const [key, value] of Object.entries(edits)) {
      const [pid, lang] = key.split(/_(?=[a-z]+$)/);
      if (!bulk[pid]) {
        bulk[pid] = { ...translations[pid] };
      }
      bulk[pid][lang as LangTab] = value;
    }
    if (Object.keys(bulk).length === 0) {
      setSaving(false);
      setSaveMsg("변경사항 없음");
      setTimeout(() => setSaveMsg(""), 2000);
      return;
    }
    try {
      const res = await fetch("/api/admin/translation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bulk }),
      });
      const data = await res.json();
      if (res.ok) {
        // Apply all edits to state
        setTranslations((prev) => {
          const next = { ...prev };
          for (const [pid, entry] of Object.entries(bulk)) {
            next[pid] = { ...next[pid], ...entry };
          }
          return next;
        });
        setEdits({});
        setSaveMsg(`${data.updated}개 저장 완료`);
      } else {
        setSaveMsg("저장 실패: " + data.error);
      }
    } catch {
      setSaveMsg("저장 중 오류 발생");
    } finally {
      setSaving(false);
      setTimeout(() => setSaveMsg(""), 3000);
    }
  };

  const pendingCount = Object.keys(edits).filter((k) => k.endsWith(`_${langTab}`)).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="font-bold text-lg text-gray-800">번역 관리</h1>
              <p className="text-xs text-gray-400">
                번역 없는 상품: <span className="text-amber-500 font-semibold">{missingCount}개</span>
                {" / "}전체: {Object.keys(translations).length}개
              </p>
            </div>
            <div className="flex items-center gap-2">
              {saveMsg && (
                <span className="text-xs text-emerald-600 font-medium">{saveMsg}</span>
              )}
              <button
                onClick={saveAll}
                disabled={saving || pendingCount === 0}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40 transition-colors"
              >
                {saving ? "저장 중..." : `전체 저장 ${pendingCount > 0 ? `(${pendingCount})` : ""}`}
              </button>
            </div>
          </div>

          {/* Language tabs */}
          <div className="flex gap-2 mb-3">
            {(["th", "vi"] as LangTab[]).map((l) => (
              <button
                key={l}
                onClick={() => setLangTab(l)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  langTab === l
                    ? "bg-emerald-600 text-white"
                    : "bg-white border border-gray-200 text-gray-600 hover:border-emerald-400"
                }`}
              >
                {l === "th" ? "🇹🇭 태국어" : "🇻🇳 베트남어"}
              </button>
            ))}
          </div>

          {/* Search & filter */}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="한국어 상품명으로 검색..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-emerald-400"
            />
            <button
              onClick={() => setFilter("missing")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filter === "missing"
                  ? "bg-amber-500 text-white"
                  : "bg-white border border-gray-200 text-gray-600 hover:border-amber-400"
              }`}
            >
              번역 없는 것만
            </button>
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filter === "all"
                  ? "bg-gray-700 text-white"
                  : "bg-white border border-gray-200 text-gray-600 hover:border-gray-400"
              }`}
            >
              전체
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-4">
        {loading ? (
          <div className="text-center py-20 text-gray-400">불러오는 중...</div>
        ) : (
          <>
            <p className="text-xs text-gray-400 mb-3">표시 {entries.length}개</p>
            <div className="flex flex-col gap-2">
              {entries.map(([pid, t]) => {
                const currentValue = getEditValue(pid, t[langTab]);
                const isDirty = edits[`${pid}_${langTab}`] !== undefined && edits[`${pid}_${langTab}`] !== t[langTab];
                return (
                  <div
                    key={pid}
                    className={`bg-white rounded-xl border p-4 flex flex-col sm:flex-row sm:items-center gap-3 ${
                      isDirty ? "border-emerald-300" : "border-gray-100"
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-400 mb-0.5">ID: {pid}</p>
                      <p className="text-sm font-medium text-gray-800 mb-1">{t.ko}</p>
                      {t[langTab] && !isDirty && (
                        <p className="text-xs text-gray-400">
                          현재: {t[langTab]}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-2 sm:w-80">
                      <input
                        type="text"
                        value={currentValue}
                        onChange={(e) => handleEdit(pid, e.target.value)}
                        placeholder={langTab === "th" ? "태국어 번역 입력..." : "베트남어 번역 입력..."}
                        className={`flex-1 border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-emerald-400 ${
                          isDirty ? "border-emerald-300 bg-emerald-50" : "border-gray-200"
                        }`}
                      />
                      <button
                        onClick={() => saveSingle(pid)}
                        disabled={!isDirty}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-30 transition-colors shrink-0"
                      >
                        저장
                      </button>
                    </div>
                  </div>
                );
              })}
              {entries.length === 0 && (
                <div className="text-center py-20 text-gray-400">
                  {filter === "missing" ? "번역이 필요한 상품이 없습니다." : "검색 결과가 없습니다."}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
