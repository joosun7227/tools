"use client";
import { useState, useRef, useCallback } from "react";
import productsData from "@/data/products.json";
import type { Product } from "@/lib/types";

// 이미지를 최대 1200px, JPEG 85%로 압축 (4.5MB 제한 대응)
function resizeImage(file: File, maxPx = 1200, quality = 0.85): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      const scale = Math.min(1, maxPx / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale);
      const h = Math.round(img.height * scale);
      const canvas = document.createElement("canvas");
      canvas.width = w;
      canvas.height = h;
      canvas.getContext("2d")!.drawImage(img, 0, 0, w, h);
      canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("canvas toBlob 실패")), "image/jpeg", quality);
    };
    img.onerror = reject;
    img.src = url;
  });
}

// ─── 엑셀 업로드 섹션 ───────────────────────────────────────────
type UploadResult = { total: number; added: number; updated: number };

function ExcelUploadSection() {
  const fileRef = useRef<HTMLInputElement>(null);
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
        const detail = data.found?.length
          ? `\n발견된 열: ${data.found.join(", ")}`
          : "";
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

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="font-semibold text-gray-800">품목정보 엑셀 업로드</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            품목정보.xlsx 형식 — 새 품목 추가 및 기존 품목 정보 업데이트
          </p>
        </div>
        <button
          onClick={() => fileRef.current?.click()}
          disabled={status === "loading"}
          className="px-4 py-2 rounded-lg text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {status === "loading" ? "처리 중..." : "엑셀 파일 선택"}
        </button>
        <input ref={fileRef} type="file" accept=".xlsx,.xls" className="hidden" onChange={handleFile} />
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
        <div className="text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2.5 border border-red-200">
          오류: {errMsg}
        </div>
      )}
    </div>
  );
}

const BLOB_BASE = process.env.NEXT_PUBLIC_BLOB_STORE_URL ?? "";
const products = productsData as Product[];

function blobUrl(id: number) {
  return BLOB_BASE ? `${BLOB_BASE}/products/${id}.jpg` : null;
}
function staticUrl(imageFile: string | null) {
  return imageFile ? `/images/${encodeURIComponent(imageFile)}` : null;
}

// 개별 상품 카드 — blob 이미지 로드 여부를 자체적으로 관리
function ProductImageCard({
  product,
  uploading,
  uploadedUrl,
  onUploadClick,
}: {
  product: Product;
  uploading: boolean;
  uploadedUrl: string | null;
  onUploadClick: (id: number) => void;
}) {
  const blob = blobUrl(product.id);
  const stat = staticUrl(product.imageFile);
  // 업로드 직후엔 uploadedUrl 우선, 아니면 blob → static 순서
  const [src, setSrc] = useState<string | null>(uploadedUrl ?? blob ?? stat);
  const [hasImage, setHasImage] = useState<boolean | null>(
    uploadedUrl ? true : stat ? true : null // null = blob 로딩 중
  );

  // uploadedUrl 변경 시 즉시 반영
  if (uploadedUrl && src !== uploadedUrl) {
    setSrc(uploadedUrl);
    setHasImage(true);
  }

  const handleError = () => {
    if (src === blob && stat) {
      setSrc(stat);
      setHasImage(true);
    } else if (src === blob) {
      setSrc(null);
      setHasImage(false);
    } else {
      setSrc(null);
      setHasImage(false);
    }
  };

  const imgExists = hasImage === true || uploadedUrl !== null;

  return (
    <div className={`bg-white rounded-xl border overflow-hidden flex flex-col ${imgExists ? "border-gray-100" : "border-red-100"}`}>
      <div className="relative h-32 bg-gray-50 flex items-center justify-center">
        {src ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={src}
            alt={product.name}
            className="max-h-full max-w-full object-contain p-1"
            onLoad={() => setHasImage(true)}
            onError={handleError}
          />
        ) : hasImage === null ? (
          <span className="text-xs text-gray-300">확인 중...</span>
        ) : (
          <span className="text-4xl text-gray-200">📦</span>
        )}
        {uploadedUrl && (
          <span className="absolute top-1 right-1 bg-emerald-500 text-white text-xs px-1.5 py-0.5 rounded-full">
            신규
          </span>
        )}
      </div>
      <div className="p-2 flex flex-col gap-1.5 flex-1">
        <p className="text-xs text-gray-400">ID: {product.id}</p>
        <p className="text-xs font-medium text-gray-700 leading-tight line-clamp-2">{product.name}</p>
        <button
          onClick={() => onUploadClick(product.id)}
          disabled={uploading}
          className={`mt-auto w-full py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            uploading
              ? "bg-gray-100 text-gray-400"
              : imgExists
              ? "bg-gray-100 text-gray-600 hover:bg-emerald-50 hover:text-emerald-700"
              : "bg-red-500 text-white hover:bg-red-600"
          }`}
        >
          {uploading ? "업로드 중..." : imgExists ? "이미지 교체" : "이미지 등록"}
        </button>
      </div>
    </div>
  );
}

export default function AdminPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "noimage">("noimage");
  const [uploading, setUploading] = useState<number | null>(null);
  const [uploaded, setUploaded] = useState<Record<number, string>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [downloading, setDownloading] = useState(false);

  const downloadAll = useCallback(async () => {
    setDownloading(true);
    try {
      const res = await fetch("/api/admin/download-all");
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        alert(d.error ?? "다운로드 실패");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "product-images.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("다운로드 중 오류가 발생했습니다.");
    } finally {
      setDownloading(false);
    }
  }, []);

  const noImageCount = products.filter((p) => !p.imageFile && !blobUrl(p.id)).length;

  const filtered = products.filter((p) => {
    const matchSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      String(p.id).includes(search);
    const matchFilter = filter === "all" || (!p.imageFile && !uploaded[p.id]);
    return matchSearch && matchFilter;
  });

  const handleUploadClick = (productId: number) => {
    setActiveId(productId);
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || activeId === null) return;
    e.target.value = "";
    setUploading(activeId);
    // 4.5MB 제한 대응: 클라이언트에서 리사이즈 후 업로드
    const blob = await resizeImage(file).catch(() => file);
    const formData = new FormData();
    formData.append("file", new File([blob], file.name.replace(/\.\w+$/, ".jpg"), { type: "image/jpeg" }));
    formData.append("productId", String(activeId));
    try {
      const res = await fetch("/api/admin/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (data.url) {
        setUploaded((prev) => ({ ...prev, [activeId]: data.url }));
      } else {
        alert("업로드 실패: " + (data.error ?? "알 수 없는 오류"));
      }
    } catch {
      alert("업로드 중 오류가 발생했습니다.");
    } finally {
      setUploading(null);
      setActiveId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 pt-6">
        <ExcelUploadSection />
      </div>
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
          <div>
            <h1 className="font-bold text-lg text-gray-800">상품 이미지 관리</h1>
            <p className="text-xs text-gray-400">
              기존 이미지 없는 상품: <span className="text-red-500 font-semibold">{noImageCount}개</span>
              {" / "}전체: {products.length}개
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={downloadAll}
              disabled={downloading}
              className="px-3 py-1.5 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {downloading ? "ZIP 생성 중..." : "전체 다운로드 (ZIP)"}
            </button>
            <button
              onClick={() => setFilter("noimage")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === "noimage" ? "bg-red-500 text-white" : "bg-white border text-gray-600 hover:border-red-300"
              }`}
            >
              이미지 없는 것만
            </button>
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === "all" ? "bg-emerald-600 text-white" : "bg-white border text-gray-600 hover:border-emerald-300"
              }`}
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

      <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />

      <div className="max-w-6xl mx-auto px-4 py-4">
        <p className="text-xs text-gray-400 mb-3">표시 {filtered.length}개</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {filtered.map((product) => (
            <ProductImageCard
              key={product.id}
              product={product}
              uploading={uploading === product.id}
              uploadedUrl={uploaded[product.id] ?? null}
              onUploadClick={handleUploadClick}
            />
          ))}
        </div>
        {filtered.length === 0 && (
          <div className="text-center py-20 text-gray-400">검색 결과가 없습니다.</div>
        )}
      </div>
    </div>
  );
}
