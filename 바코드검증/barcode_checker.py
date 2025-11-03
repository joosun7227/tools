# -*- coding: utf-8 -*-
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime

APP_TITLE = "바코드 스캔 & 매칭 프로그램"
AUTOSAVE_INTERVAL = 30  # remains available; manual save also provided prominently
MASTER_FILENAME = "master_template.xlsx"
MASTER_UPDATED = "master_updated.xlsx"
SCAN_LOG_FILE = "scan_log.xlsx"

def norm(s: str) -> str:
    return (s or "").replace(" ", "").replace("-", "").strip()

class BarcodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("780x560")
        self.configure(padx=14, pady=14)
        self.scan_count = 0
        self.log_rows = []
        self.scanned_barcodes = {}  # 스캔한 바코드 저장 {barcode: {"품목명": ..., "시간": ...}}
        self._load_master()
        self._build_menu()
        self._build_ui()
        self.after(200, lambda: self.entry_barcode.focus_set())

    # ---------- Data ----------
    def _load_master(self):
        path = MASTER_UPDATED if os.path.exists(MASTER_UPDATED) else MASTER_FILENAME
        if not os.path.exists(path):
            messagebox.showerror("오류", f"마스터 파일이 없습니다: {path}")
            sys.exit(1)
        self.master_df = pd.read_excel(path, dtype=str).fillna("")
        
        for c in ["품목코드","품목명","단위","등록바코드","실제바코드"]:
            if c not in self.master_df.columns:
                self.master_df[c] = ""
        
        # '바코드' 컬럼이 있으면 '등록바코드'로 복사 (기존 등록바코드가 비어있을 경우)
        if "바코드" in self.master_df.columns:
            empty_reg = self.master_df["등록바코드"] == ""
            self.master_df.loc[empty_reg, "등록바코드"] = self.master_df.loc[empty_reg, "바코드"]
        
        # Normalized helper columns for robust equality
        self.master_df["_n_reg"]  = self.master_df["등록바코드"].map(norm)
        self.master_df["_n_real"] = self.master_df["실제바코드"].map(norm)
        # '바코드' 컬럼도 정규화하여 검색에 사용
        if "바코드" in self.master_df.columns:
            self.master_df["_n_barcode"] = self.master_df["바코드"].map(norm)
        else:
            self.master_df["_n_barcode"] = ""
        
        # Fast index (optional)
        self._index = {}
        for _, r in self.master_df.iterrows():
            # '바코드', '등록바코드', '실제바코드' 모두 인덱스에 추가
            for key in (r["_n_barcode"], r["_n_reg"], r["_n_real"]):
                if key:
                    self._index[key] = {
                        "품목코드": r["품목코드"],
                        "품목명": r["품목명"],
                        "단위": r["단위"],
                        "등록바코드": r["등록바코드"],
                        "실제바코드": r["실제바코드"],
                    }

    def _lookup_match(self, barcode_norm: str):
        """Return a dict with item info if matched by 등록바코드 or 실제바코드, else None."""
        # 1) try fast index
        info = self._index.get(barcode_norm)
        if info:
            return info
        
        # 2) robust fallback on dataframe ('바코드', '등록바코드', '실제바코드' 모두 체크)
        m = (self.master_df["_n_barcode"] == barcode_norm) | (self.master_df["_n_reg"] == barcode_norm) | (self.master_df["_n_real"] == barcode_norm)
        if m.any():
            r = self.master_df.loc[m].iloc[0]  # first match
            info = {
                "품목코드": r["품목코드"],
                "품목명": r["품목명"],
                "단위": r["단위"],
                "등록바코드": r["등록바코드"],
                "실제바코드": r["실제바코드"],
            }
            # backfill index
            self._index[barcode_norm] = info
            return info
        
        return None

    # ---------- UI ----------
    def _build_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="지금 저장", command=self.save_now, accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="종료", command=self.on_close, accelerator="Ctrl+Q")
        menubar.add_cascade(label="파일", menu=filemenu)
        self.config(menu=menubar)
        self.bind_all("<Control-s>", lambda e: self.save_now())
        self.bind_all("<Control-q>", lambda e: self.on_close())

    def _build_ui(self):
        # Top controls (barcode + save)
        frm_in = ttk.LabelFrame(self, text="입력")
        frm_in.pack(fill="x", pady=6)
        ttk.Label(frm_in, text="바코드 입력:").pack(side="left", padx=(10,6), pady=10)
        self.entry_barcode = ttk.Entry(frm_in, width=36)
        self.entry_barcode.pack(side="left", padx=(0,10), pady=10)
        self.entry_barcode.bind("<Return>", lambda e: self.process_scan())
        ttk.Button(frm_in, text="확인(Enter)", command=self.process_scan).pack(side="left", padx=4)
        ttk.Button(frm_in, text="저장(Ctrl+S)", command=self.save_now).pack(side="left", padx=8)

        frm_info = ttk.LabelFrame(self, text="결과")
        frm_info.pack(fill="both", expand=True, pady=8)

        grid = ttk.Frame(frm_info)
        grid.pack(fill="x", padx=10, pady=10)

        self.var_status = tk.StringVar(value="대기 중")
        ttk.Label(grid, text="상태:").grid(row=0, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_status, font=("맑은 고딕", 11, "bold")).grid(row=0, column=1, sticky="w", padx=8)

        self.var_name = tk.StringVar()
        self.var_unit = tk.StringVar()
        self.var_code = tk.StringVar()
        self.var_match = tk.StringVar()
        self.var_saved = tk.StringVar(value="")

        row = 1
        ttk.Label(grid, text="품목명:").grid(row=row, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_name).grid(row=row, column=1, sticky="w", padx=8)
        row += 1
        ttk.Label(grid, text="단위:").grid(row=row, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_unit).grid(row=row, column=1, sticky="w", padx=8)
        row += 1
        ttk.Label(grid, text="바코드번호:").grid(row=row, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_code).grid(row=row, column=1, sticky="w", padx=8)
        row += 1
        ttk.Label(grid, text="일치여부:").grid(row=row, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_match).grid(row=row, column=1, sticky="w", padx=8)
        row += 1
        ttk.Label(grid, text="최근 저장:").grid(row=row, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_saved).grid(row=row, column=1, sticky="w", padx=8)

        # recent scans table
        self.tree = ttk.Treeview(frm_info, columns=("time","barcode","result","item","unit"), show="headings", height=9)
        for c, w, t in [("time",160,"시간"), ("barcode",170,"바코드"), ("result",80,"결과"), ("item",220,"품목명"), ("unit",60,"단위")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(4,10))

        frm_bottom = ttk.Frame(self)
        frm_bottom.pack(fill="x")
        self.var_counter = tk.StringVar(value="0 건")
        ttk.Label(frm_bottom, text="스캔 누계:").pack(side="left")
        ttk.Label(frm_bottom, textvariable=self.var_counter, font=("맑은 고딕", 10, "bold")).pack(side="left", padx=8)

    # ---------- Actions ----------
    def process_scan(self):
        raw = self.entry_barcode.get().strip()
        self.entry_barcode.delete(0, tk.END)
        if not raw:
            return
        barcode_norm = norm(raw)

        # 중복 바코드 체크
        if barcode_norm in self.scanned_barcodes:
            prev_info = self.scanned_barcodes[barcode_norm]
            messagebox.showwarning(
                "중복 바코드",
                f"⚠️ 이미 스캔한 바코드입니다!\n\n"
                f"바코드: {barcode_norm}\n"
                f"품목명: {prev_info['품목명']}\n"
                f"이전 스캔 시간: {prev_info['시간']}"
            )
            # 중복이지만 화면에는 표시
            self.var_status.set("중복")
            self.var_name.set(prev_info["품목명"])
            self.var_unit.set(prev_info["단위"])
            self.var_code.set(barcode_norm)
            self.var_match.set("⚠️ 중복")
            return

        # Robust match against 등록/실제바코드 (NO manual selection if matched)
        info = self._lookup_match(barcode_norm)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if info:
            # 스캔한 바코드 저장
            self.scanned_barcodes[barcode_norm] = {
                "품목명": info["품목명"],
                "단위": info["단위"],
                "품목코드": info["품목코드"],
                "시간": now
            }
            
            # record as match
            self.var_status.set("일치")
            self.var_name.set(info["품목명"])
            self.var_unit.set(info["단위"])
            self.var_code.set(barcode_norm)
            self.var_match.set("✅ 일치")
            self.add_log(now, barcode_norm, "일치", info["품목코드"], info["품목명"], info["단위"])
            # SAVE immediately per requirement
            self.save_now()
        else:
            # open search dialog
            self.open_search_dialog(barcode_norm)
            return

        self.scan_count += 1
        self.var_counter.set(f"{self.scan_count} 건")
        # Autosave still available if you want to keep the 30-scan cadence as well
        if self.scan_count % AUTOSAVE_INTERVAL == 0:
            self.save_now()

    def open_search_dialog(self, scanned_barcode):
        dlg = tk.Toplevel(self)
        dlg.title("품목 검색 (일치 없음)")
        dlg.geometry("720x500")
        dlg.transient(self)
        dlg.grab_set()

        top = ttk.Frame(dlg)
        top.pack(fill="x", pady=8, padx=10)
        ttk.Label(top, text=f"스캔 바코드: {scanned_barcode}").pack(side="left")
        ttk.Label(top, text="검색:").pack(side="left", padx=(18,6))
        var_q = tk.StringVar()
        ent = ttk.Entry(top, textvariable=var_q, width=30)
        ent.pack(side="left")
        ent.focus_set()

        cols = ("품목코드","품목명","단위","등록바코드","실제바코드")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=15)
        for c, w in [("품목코드",100),("품목명",240),("단위",60),("등록바코드",160),("실제바코드",160)]:
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=(6,10))

        def refresh_table(query=""):
            q = (query or "").strip().lower()
            tree.delete(*tree.get_children())
            df = self.master_df
            if q:
                mask = df["품목코드"].str.lower().str.contains(q) | df["품목명"].str.lower().str.contains(q)
                df = df[mask]
            for _, r in df.iterrows():
                tree.insert("", "end", values=(r["품목코드"], r["품목명"], r["단위"], r["등록바코드"], r["실제바코드"]))

        refresh_table()
        ent.bind("<KeyRelease>", lambda e: refresh_table(var_q.get()))

        def choose_and_close():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("안내","품목을 선택하세요.")
                return
            vals = tree.item(sel[0], "values")
            self.apply_mapping(scanned_barcode, vals[0])
            dlg.destroy()

        tree.bind("<Double-1>", lambda e: choose_and_close())
        btnfrm = ttk.Frame(dlg)
        btnfrm.pack(fill="x", pady=6)
        ttk.Button(btnfrm, text="선택(Enter)", command=choose_and_close).pack(side="right", padx=10)
        dlg.bind("<Return>", lambda e: choose_and_close())

    def apply_mapping(self, scanned_barcode, chosen_code):
        idx = self.master_df.index[self.master_df["품목코드"] == chosen_code]
        if len(idx) == 0:
            messagebox.showerror("오류","선택한 품목코드를 찾을 수 없습니다.")
            return
        i = idx[0]
        self.master_df.at[i, "실제바코드"] = scanned_barcode
        # Update normalized helper column
        self.master_df.at[i, "_n_real"] = norm(scanned_barcode)
        # Update index
        barcode_norm = norm(scanned_barcode)
        self._index[barcode_norm] = {
            "품목코드": self.master_df.at[i, "품목코드"],
            "품목명": self.master_df.at[i, "품목명"],
            "단위": self.master_df.at[i, "단위"],
            "등록바코드": self.master_df.at[i, "등록바코드"],
            "실제바코드": scanned_barcode,
        }
        
        # Show result + SAVE immediately?
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 스캔한 바코드 저장
        self.scanned_barcodes[barcode_norm] = {
            "품목명": self.master_df.at[i, "품목명"],
            "단위": self.master_df.at[i, "단위"],
            "품목코드": self.master_df.at[i, "품목코드"],
            "시간": now
        }
        
        self.var_status.set("수동지정")
        self.var_name.set(self.master_df.at[i, "품목명"])
        self.var_unit.set(self.master_df.at[i, "단위"])
        self.var_code.set(scanned_barcode)
        self.var_match.set("⚠️ 수동지정")
        self.add_log(now, scanned_barcode, "수동지정", self.master_df.at[i, "품목코드"], self.master_df.at[i, "품목명"], self.master_df.at[i, "단위"])
        # Save immediately as well to persist the mapping
        self.save_now()

        self.scan_count += 1
        self.var_counter.set(f"{self.scan_count} 건")
        if self.scan_count % AUTOSAVE_INTERVAL == 0:
            self.save_now()

    def add_log(self, ts, barcode, result, code, name, unit):
        self.tree.insert("", 0, values=(ts, barcode, result, name, unit))
        self.log_rows.append({
            "스캔시간": ts,
            "스캔바코드": barcode,
            "결과": result,
            "품목코드": code,
            "품목명": name,
            "단위": unit,
        })

    def save_now(self):
        try:
            # Persist master updates
            safe_df = self.master_df.drop(columns=[c for c in ["_n_reg","_n_real"] if c in self.master_df.columns])
            safe_df.to_excel(MASTER_UPDATED, index=False)
            # Append logs
            if self.log_rows:
                df_new = pd.DataFrame(self.log_rows)
                if os.path.exists(SCAN_LOG_FILE):
                    try:
                        df_old = pd.read_excel(SCAN_LOG_FILE, dtype=str).fillna("")
                        df_all = pd.concat([df_old, df_new], ignore_index=True)
                    except Exception:
                        df_all = df_new
                else:
                    df_all = df_new
                df_all.to_excel(SCAN_LOG_FILE, index=False)
                self.log_rows = []
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.var_status.set("저장 완료")
            self.var_saved.set(ts)
        except Exception as e:
            messagebox.showerror("저장 오류", str(e))

    def on_close(self):
        if self.log_rows:
            if messagebox.askyesno("종료 확인", "저장되지 않은 로그가 있습니다. 저장 후 종료할까요?"):
                self.save_now()
        self.destroy()

def main():
    app = BarcodeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()

if __name__ == "__main__":
    main()
