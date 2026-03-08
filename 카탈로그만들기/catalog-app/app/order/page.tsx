"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCartStore } from "@/store/cartStore";
import type { OrderInfo } from "@/lib/types";

const today = new Date().toISOString().split("T")[0];

export default function OrderPage() {
  const { items, total, setQty, remove, clear } = useCartStore();
  const router = useRouter();
  const [info, setInfo] = useState<OrderInfo>({
    custCode: "",
    custName: "",
    managerName: "",
    phone: "",
    orderDate: today,
    note: "",
  });
  const [excelLoading, setExcelLoading] = useState(false);
  const [ecountLoading, setEcountLoading] = useState(false);
  const [ecountResult, setEcountResult] = useState<{
    success: boolean;
    message?: string;
    error?: string;
  } | null>(null);

  const handleChange =
    (field: keyof OrderInfo) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setInfo((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const payload = { orderInfo: info, items };

  const downloadExcel = async () => {
    setExcelLoading(true);
    try {
      const res = await fetch("/api/order/excel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const cd = res.headers.get("Content-Disposition") ?? "";
      const match = cd.match(/filename\*=UTF-8''(.+)/);
      a.download = match ? decodeURIComponent(match[1]) : "주문서.xlsx";
      a.href = url;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setExcelLoading(false);
    }
  };

  const submitEcount = async () => {
    if (!info.custCode) {
      alert("거래처코드를 입력하세요.");
      return;
    }
    if (!confirm("Ecount ERP에 판매 입력합니다. 계속하시겠습니까?")) return;
    setEcountLoading(true);
    setEcountResult(null);
    try {
      const res = await fetch("/api/order/ecount", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setEcountResult(data);
      if (data.success) {
        clear();
      }
    } catch {
      setEcountResult({ success: false, error: "네트워크 오류" });
    } finally {
      setEcountLoading(false);
    }
  };

  if (items.length === 0 && !ecountResult?.success) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-4">
        <p className="text-gray-500">장바구니가 비어있습니다.</p>
        <button
          onClick={() => router.push("/")}
          className="bg-emerald-600 text-white px-6 py-2 rounded-full text-sm"
        >
          카탈로그로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="text-gray-500 hover:text-gray-800"
          >
            ← 뒤로
          </button>
          <h1 className="font-bold text-lg text-gray-800">주문서 작성</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 거래처 정보 */}
        <div className="bg-white rounded-2xl border p-5 space-y-4 h-fit">
          <h2 className="font-bold text-gray-800 text-base">거래처 정보</h2>

          {(
            [
              {
                label: "거래처코드 *",
                field: "custCode" as const,
                placeholder: "Ecount 거래처코드 (예: 44522)",
              },
              {
                label: "거래처명",
                field: "custName" as const,
                placeholder: "회사명",
              },
              {
                label: "담당자",
                field: "managerName" as const,
                placeholder: "담당자 이름",
              },
              {
                label: "연락처",
                field: "phone" as const,
                placeholder: "010-0000-0000",
              },
            ] as const
          ).map(({ label, field, placeholder }) => (
            <div key={field}>
              <label className="block text-xs text-gray-500 mb-1">{label}</label>
              <input
                type="text"
                value={info[field]}
                onChange={handleChange(field)}
                placeholder={placeholder}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-400"
              />
            </div>
          ))}

          <div>
            <label className="block text-xs text-gray-500 mb-1">주문일</label>
            <input
              type="date"
              value={info.orderDate}
              onChange={handleChange("orderDate")}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">비고</label>
            <textarea
              value={info.note}
              onChange={handleChange("note")}
              rows={2}
              placeholder="특이사항..."
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-400 resize-none"
            />
          </div>
        </div>

        {/* 주문 상품 + 액션 */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border p-5">
            <h2 className="font-bold text-gray-800 text-base mb-3">
              주문 상품 ({items.length})
            </h2>
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 py-2 border-b last:border-0"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {item.name}
                    </p>
                    <p className="text-xs text-gray-400">
                      <span className="inline-block bg-emerald-50 text-emerald-700 rounded px-1 mr-1 font-medium">{item.unit}</span>
                      {item.spec}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => setQty(item.id, item.qty - 1)}
                      className="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-sm font-bold flex items-center justify-center"
                    >
                      -
                    </button>
                    <span className="w-7 text-center text-sm font-semibold">
                      {item.qty}
                    </span>
                    <button
                      onClick={() => setQty(item.id, item.qty + 1)}
                      className="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-sm font-bold flex items-center justify-center"
                    >
                      +
                    </button>
                    <button
                      onClick={() => remove(item.id)}
                      className="ml-1 text-gray-300 hover:text-red-400 text-lg"
                    >
                      &times;
                    </button>
                  </div>
                </div>
              ))}
            </div>

          </div>

          {/* 버튼 */}
          <div className="space-y-2">
            <button
              onClick={downloadExcel}
              disabled={excelLoading || items.length === 0}
              className="w-full bg-white border-2 border-emerald-600 text-emerald-600 hover:bg-emerald-50 font-semibold py-3 rounded-xl transition-colors disabled:opacity-50 text-sm"
            >
              {excelLoading ? "엑셀 생성 중..." : "엑셀 주문서 다운로드"}
            </button>

            <button
              onClick={submitEcount}
              disabled={ecountLoading || items.length === 0 || !info.custCode}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 rounded-xl transition-colors disabled:opacity-50 text-sm"
            >
              {ecountLoading ? "Ecount 전송 중..." : "Ecount ERP 판매 자동입력"}
            </button>

            {!info.custCode && items.length > 0 && (
              <p className="text-xs text-amber-600 text-center">
                거래처코드 입력 후 Ecount 자동입력 가능
              </p>
            )}
          </div>

          {/* Ecount 결과 */}
          {ecountResult && (
            <div
              className={`rounded-xl p-4 text-sm ${
                ecountResult.success
                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                  : "bg-red-50 text-red-700 border border-red-200"
              }`}
            >
              {ecountResult.success ? (
                <>
                  <p className="font-semibold">Ecount 판매 입력 완료!</p>
                  <p className="mt-1 text-xs">장바구니가 초기화되었습니다.</p>
                </>
              ) : (
                <>
                  <p className="font-semibold">Ecount 전송 실패</p>
                  <p className="mt-1 text-xs">{ecountResult.error}</p>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
