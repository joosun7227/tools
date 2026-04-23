"use client";
import { useState } from "react";

export default function InquiryButton() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [memo, setMemo] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [errMsg, setErrMsg] = useState("");

  const reset = () => {
    setName("");
    setPhone("");
    setMemo("");
    setStatus("idle");
    setErrMsg("");
  };

  const handleClose = () => {
    setOpen(false);
    reset();
  };

  const handleSubmit = async () => {
    if (!name.trim() && !phone.trim()) {
      setErrMsg("성명 또는 연락처를 입력해 주세요.");
      return;
    }
    setStatus("loading");
    setErrMsg("");
    try {
      const res = await fetch("/api/inquiry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, memo }),
      });
      if (res.ok) {
        setStatus("done");
      } else {
        const data = await res.json();
        setErrMsg(data.error ?? "전송 실패");
        setStatus("error");
      }
    } catch {
      setErrMsg("네트워크 오류");
      setStatus("error");
    }
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-40 bg-emerald-600 hover:bg-emerald-700 text-white rounded-full shadow-lg px-4 py-3 text-sm font-semibold flex items-center gap-2 transition-colors"
      >
        <span>📞</span>
        <span>문의하기</span>
      </button>

      {/* Modal backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-end sm:items-center justify-center p-4"
          onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
        >
          <div className="bg-white rounded-2xl w-full max-w-sm shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between px-5 pt-5 pb-3">
              <h2 className="font-bold text-gray-800 text-base">문의하기</h2>
              <button onClick={handleClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
            </div>

            {status === "done" ? (
              <div className="px-5 pb-6 text-center space-y-3">
                <p className="text-3xl">✅</p>
                <p className="font-semibold text-gray-800">문의가 접수되었습니다!</p>
                <p className="text-sm text-gray-500">담당자가 확인 후 연락드리겠습니다.</p>
                <button
                  onClick={handleClose}
                  className="w-full bg-emerald-600 text-white py-2.5 rounded-xl text-sm font-semibold mt-2"
                >
                  확인
                </button>
              </div>
            ) : (
              <div className="px-5 pb-5 space-y-4">
                {/* 연락처 표시 */}
                <div className="bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3 text-center">
                  <p className="text-xs text-gray-500 mb-0.5">직접 연락하실 경우</p>
                  <a
                    href="tel:010-8587-7227"
                    className="text-lg font-bold text-emerald-700 hover:underline"
                  >
                    📞 010-8587-7227
                  </a>
                </div>

                {/* Form */}
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">성명</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="이름을 입력해 주세요"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">연락처</label>
                    <input
                      type="tel"
                      inputMode="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="010-0000-0000"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">메모</label>
                    <textarea
                      value={memo}
                      onChange={(e) => setMemo(e.target.value)}
                      rows={3}
                      placeholder="문의 내용을 간단히 적어주세요..."
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-400 resize-none"
                    />
                  </div>
                </div>

                {errMsg && (
                  <p className="text-xs text-red-500">{errMsg}</p>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={status === "loading"}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  {status === "loading" ? "전송 중..." : "문의 접수"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
