"use client";
import { useState, useEffect, useCallback } from "react";
import productsData from "@/data/products.json";
import type { Product } from "@/lib/types";
import type { Inquiry } from "@/app/api/inquiry/route";

const products = productsData as Product[];

// ─── 이미지 업로드 섹션 ──────────────────────────────────────────
type FileStatus = "pending" | "uploading" | "done" | "error";
interface FileItem {
  file: File;
  status: FileStatus;
  preview: string;
  error?: string;
}

function ImageUploadSection() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [inputEl, setInputEl] = useState<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const addFiles = (newFiles: FileList | File[]) => {
    const items: FileItem[] = Array.from(newFiles)
      .filter((f) => /\.(jpg|jpeg|png)$/i.test(f.name))
      .map((f) => ({
        file: f,
        status: "pending",
        preview: URL.createObjectURL(f),
      }));
    if (items.length === 0) return;
    setFiles((prev) => [...prev, ...items]);
  };

  const uploadAll = async () => {
    const pending = files.filter((f) => f.status === "pending" || f.status === "error");
    if (pending.length === 0) return;

    for (const item of pending) {
      setFiles((prev) =>
        prev.map((f) => (f.file === item.file ? { ...f, status: "uploading" } : f))
      );

      const form = new FormData();
      form.append("file", item.file);

      try {
        const res = await fetch("/api/admin/upload", { method: "POST", body: form });
        if (res.ok) {
          setFiles((prev) =>
            prev.map((f) => (f.file === item.file ? { ...f, status: "done" } : f))
          );
        } else {
          const data = await res.json();
          setFiles((prev) =>
            prev.map((f) =>
              f.file === item.file ? { ...f, status: "error", error: data.error ?? "실패" } : f
            )
          );
        }
      } catch {
        setFiles((prev) =>
          prev.map((f) =>
            f.file === item.file ? { ...f, status: "error", error: "네트워크 오류" } : f
          )
        );
      }
    }
  };

  const remove = (file: File) => {
    setFiles((prev) => {
      const item = prev.find((f) => f.file === file);
      if (item) URL.revokeObjectURL(item.preview);
      return prev.filter((f) => f.file !== file);
    });
  };

  const clearDone = () => {
    setFiles((prev) => {
      prev.filter((f) => f.status === "done").forEach((f) => URL.revokeObjectURL(f.preview));
      return prev.filter((f) => f.status !== "done");
    });
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    addFiles(e.dataTransfer.files);
  }, []);

  const pendingCount = files.filter((f) => f.status === "pending" || f.status === "error").length;
  const doneCount = files.filter((f) => f.status === "done").length;
  const uploadingCount = files.filter((f) => f.status === "uploading").length;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="font-semibold text-gray-800">상품 이미지 업로드</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            파일명을 품목코드로 저장하세요 (예: 5430.jpg) — 여러 장 한꺼번에 가능
          </p>
        </div>
        <div className="flex gap-2">
          {doneCount > 0 && (
            <button
              onClick={clearDone}
              className="px-3 py-2 rounded-lg text-sm text-gray-500 border hover:border-gray-400 transition-colors"
            >
              완료 목록 지우기
            </button>
          )}
          <button
            onClick={() => inputEl?.click()}
            className="px-4 py-2 rounded-lg text-sm font-semibold bg-white border-2 border-emerald-500 text-emerald-600 hover:bg-emerald-50 transition-colors"
          >
            파일 선택
          </button>
          {pendingCount > 0 && (
            <button
              onClick={uploadAll}
              disabled={uploadingCount > 0}
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              {uploadingCount > 0 ? `업로드 중... (${uploadingCount})` : `업로드 (${pendingCount}개)`}
            </button>
          )}
        </div>
        <input
          ref={setInputEl}
          type="file"
          accept=".jpg,.jpeg,.png"
          multiple
          className="hidden"
          onChange={(e) => { if (e.target.files) addFiles(e.target.files); e.target.value = ""; }}
        />
      </div>

      {/* 드래그 앤 드롭 영역 */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => files.length === 0 && inputEl?.click()}
        className={`border-2 border-dashed rounded-xl transition-colors ${
          isDragging
            ? "border-emerald-400 bg-emerald-50"
            : files.length === 0
            ? "border-gray-200 bg-gray-50 cursor-pointer hover:border-emerald-300 hover:bg-emerald-50/50"
            : "border-gray-200 bg-gray-50"
        }`}
      >
        {files.length === 0 ? (
          <div className="py-10 text-center text-gray-400">
            <p className="text-3xl mb-2">🖼️</p>
            <p className="text-sm">여기에 이미지를 드래그하거나 클릭해서 선택</p>
            <p className="text-xs mt-1">JPG, PNG 지원 · 여러 파일 동시 선택 가능</p>
          </div>
        ) : (
          <div className="p-3 grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-10 gap-2">
            {files.map((item) => (
              <div key={item.file.name + item.file.size} className="relative group">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={item.preview}
                  alt={item.file.name}
                  className={`w-full aspect-square object-cover rounded-lg border-2 ${
                    item.status === "done"
                      ? "border-emerald-400"
                      : item.status === "error"
                      ? "border-red-400"
                      : item.status === "uploading"
                      ? "border-blue-400 opacity-70"
                      : "border-gray-200"
                  }`}
                />
                {/* 상태 배지 */}
                <span className="absolute bottom-1 left-1 right-1 text-center text-xs rounded px-1 truncate">
                  {item.status === "done" && <span className="bg-emerald-500 text-white rounded px-1">✓</span>}
                  {item.status === "uploading" && <span className="bg-blue-500 text-white rounded px-1">...</span>}
                  {item.status === "error" && <span className="bg-red-500 text-white rounded px-1">✗</span>}
                </span>
                {/* 파일명 툴팁 & 삭제 */}
                <button
                  onClick={(e) => { e.stopPropagation(); remove(item.file); }}
                  className="absolute top-0.5 right-0.5 w-5 h-5 bg-black/60 text-white rounded-full text-xs items-center justify-center hidden group-hover:flex"
                >
                  ×
                </button>
                <p className="text-xs text-gray-400 truncate mt-0.5 text-center">{item.file.name}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 요약 */}
      {files.length > 0 && (
        <div className="flex gap-3 mt-2 text-xs text-gray-500">
          <span>전체 {files.length}개</span>
          {doneCount > 0 && <span className="text-emerald-600 font-medium">완료 {doneCount}개</span>}
          {pendingCount > 0 && <span className="text-amber-600">대기 {pendingCount}개</span>}
          {uploadingCount > 0 && <span className="text-blue-600">업로드 중 {uploadingCount}개</span>}
          {files.filter((f) => f.status === "error").length > 0 && (
            <span className="text-red-500">오류 {files.filter((f) => f.status === "error").length}개</span>
          )}
        </div>
      )}
    </div>
  );
}

// ─── 엑셀 업로드 섹션 ───────────────────────────────────────────
type UploadResult = { total: number; added: number; updated: number };

function ExcelUploadSection() {
  const fileRef = useState<HTMLInputElement | null>(null);
  const [inputEl, setInputEl] = useState<HTMLInputElement | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<UploadResult | null>(null);
  const [errMsg, setErrMsg] = useState("");

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";
    setStatus("loading");
    setResult(null);
    setErrMsg("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/admin/products", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok || data.error) {
        const detail = data.found?.length ? `\n발견된 열: ${data.found.join(", ")}` : "";
        setErrMsg((data.error ?? "업로드 실패") + detail);
        setStatus("error");
      } else {
        setResult(data as UploadResult);
        setStatus("done");
      }
    } catch {
      setErrMsg("네트워크 오류");
      setStatus("error");
    }
  };

  void fileRef;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="font-semibold text-gray-800">품목정보 엑셀 업로드</h2>
          <p className="text-xs text-gray-400 mt-0.5">품목정보.xlsx 형식 — 새 품목 추가 및 기존 품목 정보 업데이트</p>
        </div>
        <button
          onClick={() => inputEl?.click()}
          disabled={status === "loading"}
          className="px-4 py-2 rounded-lg text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {status === "loading" ? "처리 중..." : "엑셀 파일 선택"}
        </button>
        <input ref={setInputEl} type="file" accept=".xlsx,.xls" className="hidden" onChange={handleFile} />
      </div>
      {status === "done" && result && (
        <div className="flex gap-4 text-sm bg-emerald-50 rounded-lg px-4 py-2.5 border border-emerald-200">
          <span className="text-emerald-700 font-medium">업로드 완료</span>
          <span className="text-gray-500">전체 <strong className="text-gray-800">{result.total}</strong>개</span>
          <span className="text-blue-600">신규 <strong>{result.added}</strong>개</span>
          <span className="text-amber-600">업데이트 <strong>{result.updated}</strong>개</span>
          <span className="text-gray-400 text-xs self-center">새로고침하면 반영됩니다</span>
        </div>
      )}
      {status === "error" && (
        <div className="text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2.5 border border-red-200 whitespace-pre-wrap">
          오류: {errMsg}
        </div>
      )}
    </div>
  );
}

// ─── 상품 카드 (이미지 업로드 포함) ─────────────────────────────
function ProductImageCard({ product }: { product: Product }) {
  const BLOB = process.env.NEXT_PUBLIC_BLOB_STORE_URL ?? "";
  const defaultSrc = product.imageFile
    ? BLOB
      ? `${BLOB}/products/${encodeURIComponent(product.imageFile)}`
      : `/images/${encodeURIComponent(product.imageFile)}`
    : null;

  const [imgSrc, setImgSrc] = useState<string | null>(defaultSrc);
  const [ok, setOk] = useState<boolean | null>(defaultSrc ? null : false);
  const [uploading, setUploading] = useState(false);
  const [inputEl, setInputEl] = useState<HTMLInputElement | null>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";

    setUploading(true);
    const form = new FormData();
    // 품목코드.확장자 형식으로 파일명 지정
    const ext = file.name.split(".").pop()?.toLowerCase() ?? "jpg";
    const renamedFile = new File([file], `${product.id}.${ext}`, { type: file.type });
    form.append("file", renamedFile);

    try {
      const res = await fetch("/api/admin/upload", { method: "POST", body: form });
      if (res.ok) {
        const data = await res.json();
        setImgSrc(data.url + "?t=" + Date.now()); // 캐시 무효화
        setOk(true);
      } else {
        alert("업로드 실패");
      }
    } catch {
      alert("네트워크 오류");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={`bg-white rounded-xl border overflow-hidden flex flex-col group ${ok === false ? "border-red-100" : "border-gray-100"}`}>
      {/* 이미지 영역 — 호버 시 업로드 버튼 오버레이 */}
      <div
        className="relative h-32 bg-gray-50 flex items-center justify-center cursor-pointer"
        onClick={() => inputEl?.click()}
      >
        {imgSrc && ok !== false ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imgSrc}
            alt={product.name}
            className="max-h-full max-w-full object-contain p-1"
            onLoad={() => setOk(true)}
            onError={() => setOk(false)}
          />
        ) : (
          <span className="text-4xl text-gray-200">📦</span>
        )}

        {/* 호버 오버레이 */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center">
          {uploading ? (
            <span className="text-white text-xs font-semibold bg-black/50 px-2 py-1 rounded-full">업로드 중...</span>
          ) : (
            <span className="text-white text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
              📷 사진 변경
            </span>
          )}
        </div>

        <input
          ref={setInputEl}
          type="file"
          accept=".jpg,.jpeg,.png"
          className="hidden"
          onChange={handleFile}
        />
      </div>

      <div className="p-2">
        <p className="text-xs text-gray-400">ID: {product.id}</p>
        <p className="text-xs font-medium text-gray-700 leading-tight line-clamp-2">{product.name}</p>
        <p className={`text-xs mt-1 font-medium ${ok === false ? "text-red-400" : ok === true ? "text-emerald-500" : "text-gray-300"}`}>
          {ok === false ? "이미지 없음 · 클릭해서 추가" : ok === true ? `${product.id}.jpg` : "확인 중..."}
        </p>
      </div>
    </div>
  );
}

// ─── 문의 목록 섹션 ──────────────────────────────────────────────
function InquirySection() {
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [errMsg, setErrMsg] = useState("");

  useEffect(() => {
    fetch("/api/inquiry")
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setInquiries(data);
        else setErrMsg(data.error ?? "불러오기 실패");
      })
      .catch(() => setErrMsg("네트워크 오류"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <h2 className="font-semibold text-gray-800 mb-3">
        문의 목록{" "}
        {!loading && !errMsg && (
          <span className="text-sm font-normal text-gray-400">({inquiries.length}건)</span>
        )}
      </h2>

      {loading && <p className="text-sm text-gray-400">불러오는 중...</p>}
      {errMsg && <p className="text-sm text-red-500">{errMsg}</p>}

      {!loading && !errMsg && inquiries.length === 0 && (
        <p className="text-sm text-gray-400">아직 문의가 없습니다.</p>
      )}

      {inquiries.length > 0 && (
        <div className="divide-y divide-gray-100">
          {inquiries.map((inq) => (
            <div key={inq.id} className="py-3 text-sm">
              <div className="flex items-center gap-3 flex-wrap">
                <span className="font-medium text-gray-800">{inq.name || "—"}</span>
                {inq.phone && (
                  <a href={`tel:${inq.phone}`} className="text-emerald-600 hover:underline">
                    {inq.phone}
                  </a>
                )}
                <span className="ml-auto text-xs text-gray-400">
                  {new Date(inq.createdAt).toLocaleString("ko-KR", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
              {inq.memo && <p className="mt-1 text-gray-600 whitespace-pre-wrap">{inq.memo}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── 메인 ───────────────────────────────────────────────────────
export default function AdminPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "noimage">("noimage");

  const noImageCount = products.filter((p) => !p.imageFile).length;

  const filtered = products.filter((p) => {
    const matchSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      String(p.id).includes(search);
    const matchFilter = filter === "all" || !p.imageFile;
    return matchSearch && matchFilter;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 pt-6">
        <InquirySection />
        <ImageUploadSection />
        <ExcelUploadSection />
      </div>

      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
          <div>
            <h1 className="font-bold text-lg text-gray-800">상품 이미지 현황</h1>
            <p className="text-xs text-gray-400">
              이미지 없는 상품: <span className="text-red-500 font-semibold">{noImageCount}개</span>
              {" / "}전체: {products.length}개
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter("noimage")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filter === "noimage" ? "bg-red-500 text-white" : "bg-white border text-gray-600 hover:border-red-300"}`}
            >
              이미지 없는 것만
            </button>
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filter === "all" ? "bg-emerald-600 text-white" : "bg-white border text-gray-600 hover:border-emerald-300"}`}
            >
              전체 보기
            </button>
          </div>
        </div>
        <div className="max-w-6xl mx-auto px-4 pb-3">
          <input
            type="text"
            placeholder="상품명 또는 ID 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-400"
          />
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-4">
        <p className="text-xs text-gray-400 mb-3">표시 {filtered.length}개</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {filtered.map((product) => (
            <ProductImageCard key={product.id} product={product} />
          ))}
        </div>
        {filtered.length === 0 && (
          <div className="text-center py-20 text-gray-400">검색 결과가 없습니다.</div>
        )}
      </div>
    </div>
  );
}
