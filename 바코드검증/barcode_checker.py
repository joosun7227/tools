# -*- coding: utf-8 -*-
"""
바코드 스캔 & 매칭 프로그램
====================================
작성일: 2025년
기능:
  - 엑셀 마스터 파일에서 품목 정보 로드
  - 바코드 스캔하여 자동 매칭
  - 일치하지 않는 바코드는 수동으로 품목 지정
  - 중복 바코드 감지
  - 스캔 로그 자동 저장
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime

# ============================================================================
# 전역 상수 설정
# ============================================================================
APP_TITLE = "바코드 스캔 & 매칭 프로그램"
AUTOSAVE_INTERVAL = 30  # 30번 스캔마다 자동 저장
MASTER_FILENAME = "master_template.xlsx"  # 초기 마스터 파일
MASTER_UPDATED = "master_updated.xlsx"  # 업데이트된 마스터 파일 (실제바코드 저장용)
SCAN_LOG_FILE = "scan_log.xlsx"  # 스캔 로그 파일

# ============================================================================
# 유틸리티 함수
# ============================================================================
def norm(s: str) -> str:
    """
    바코드 정규화 함수
    - 공백, 하이픈 제거하여 비교를 쉽게 만듦
    - 예: "8802-534-882587" → "8802534882587"
    """
    return (s or "").replace(" ", "").replace("-", "").strip()

# ============================================================================
# 메인 애플리케이션 클래스
# ============================================================================
class BarcodeApp(tk.Tk):
    """바코드 스캔 프로그램의 메인 윈도우"""
    
    def __init__(self):
        """
        애플리케이션 초기화
        - 윈도우 설정
        - 데이터 로드
        - UI 구성
        """
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("780x560")
        self.configure(padx=14, pady=14)
        
        # 스캔 관련 변수 초기화
        self.scan_count = 0  # 스캔 누계
        self.log_rows = []  # 메모리에 임시 저장할 로그 (저장 전까지)
        self.scanned_barcodes = {}  # 중복 체크용: {바코드: {품목명, 시간, ...}}
        
        # 데이터 및 UI 구성
        self._load_master()  # 마스터 파일 로드
        self._build_menu()  # 메뉴바 생성
        self._build_ui()  # UI 구성
        
        # 200ms 후에 바코드 입력창에 포커스 (프로그램 시작 시 바로 스캔 가능)
        self.after(200, lambda: self.entry_barcode.focus_set())

    # ========================================================================
    # 데이터 관리 메서드
    # ========================================================================
    def _load_master(self):
        """
        마스터 엑셀 파일 로드
        1. master_updated.xlsx가 있으면 그것을 로드 (이전 작업 이어서)
        2. 없으면 master_template.xlsx 로드 (처음 시작)
        3. 필요한 컬럼이 없으면 빈 컬럼 생성
        4. 바코드 정규화 및 인덱스 생성
        """
        # 파일 선택: 업데이트 파일이 있으면 우선, 없으면 템플릿
        path = MASTER_UPDATED if os.path.exists(MASTER_UPDATED) else MASTER_FILENAME
        
        # 파일이 없으면 오류 표시 후 종료
        if not os.path.exists(path):
            messagebox.showerror("오류", f"마스터 파일이 없습니다: {path}")
            sys.exit(1)
        
        # 엑셀 파일 읽기 (모든 데이터를 문자열로, 빈 칸은 ""로)
        self.master_df = pd.read_excel(path, dtype=str).fillna("")
        
        # 필수 컬럼이 없으면 빈 컬럼 생성
        for c in ["품목코드","품목명","단위","등록바코드","실제바코드"]:
            if c not in self.master_df.columns:
                self.master_df[c] = ""
        
        # '바코드' 컬럼이 있으면 '등록바코드'로 복사
        # (엑셀 파일에서 '바코드' 컬럼을 사용하는 경우를 위한 호환성)
        if "바코드" in self.master_df.columns:
            empty_reg = self.master_df["등록바코드"] == ""
            self.master_df.loc[empty_reg, "등록바코드"] = self.master_df.loc[empty_reg, "바코드"]
        
        # 바코드 정규화 (공백/하이픈 제거한 버전)
        # "_n_"은 "normalized"의 약자
        self.master_df["_n_reg"]  = self.master_df["등록바코드"].map(norm)  # 등록바코드 정규화
        self.master_df["_n_real"] = self.master_df["실제바코드"].map(norm)  # 실제바코드 정규화
        
        # '바코드' 컬럼도 정규화
        if "바코드" in self.master_df.columns:
            self.master_df["_n_barcode"] = self.master_df["바코드"].map(norm)
        else:
            self.master_df["_n_barcode"] = ""
        
        # 빠른 검색을 위한 인덱스 딕셔너리 생성
        # {정규화된_바코드: {품목코드, 품목명, 단위, ...}}
        self._index = {}
        for _, r in self.master_df.iterrows():
            # 바코드, 등록바코드, 실제바코드 세 가지 모두 인덱스에 추가
            for key in (r["_n_barcode"], r["_n_reg"], r["_n_real"]):
                if key:  # 빈 문자열이 아니면
                    self._index[key] = {
                        "품목코드": r["품목코드"],
                        "품목명": r["품목명"],
                        "단위": r["단위"],
                        "등록바코드": r["등록바코드"],
                        "실제바코드": r["실제바코드"],
                    }

    def _lookup_match(self, barcode_norm: str):
        """
        정규화된 바코드로 품목 정보 검색
        
        매개변수:
            barcode_norm: 정규화된 바코드 (공백/하이픈 제거됨)
        
        반환값:
            일치하면: {"품목코드": ..., "품목명": ..., ...}
            불일치하면: None
        
        검색 순서:
            1. 인덱스에서 빠른 검색 (O(1))
            2. 인덱스에 없으면 DataFrame에서 직접 검색 (O(n))
        """
        # 1단계: 인덱스에서 빠른 검색
        info = self._index.get(barcode_norm)
        if info:
            return info
        
        # 2단계: DataFrame에서 직접 검색 (바코드, 등록바코드, 실제바코드 모두 체크)
        m = (self.master_df["_n_barcode"] == barcode_norm) | \
            (self.master_df["_n_reg"] == barcode_norm) | \
            (self.master_df["_n_real"] == barcode_norm)
        
        if m.any():  # 매칭되는 행이 있으면
            r = self.master_df.loc[m].iloc[0]  # 첫 번째 매칭 행 가져오기
            info = {
                "품목코드": r["품목코드"],
                "품목명": r["품목명"],
                "단위": r["단위"],
                "등록바코드": r["등록바코드"],
                "실제바코드": r["실제바코드"],
            }
            # 인덱스에 추가 (다음번엔 빠르게 찾을 수 있도록)
            self._index[barcode_norm] = info
            return info
        
        return None  # 매칭 실패

    # ========================================================================
    # UI 구성 메서드
    # ========================================================================
    def _build_menu(self):
        """
        메뉴바 생성
        - 파일 > 지금 저장 (Ctrl+S)
        - 파일 > 종료 (Ctrl+Q)
        """
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="지금 저장", command=self.save_now, accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="종료", command=self.on_close, accelerator="Ctrl+Q")
        menubar.add_cascade(label="파일", menu=filemenu)
        self.config(menu=menubar)
        
        # 키보드 단축키 바인딩
        self.bind_all("<Control-s>", lambda e: self.save_now())
        self.bind_all("<Control-q>", lambda e: self.on_close())

    def _build_ui(self):
        """
        UI 구성
        1. 입력 영역 (바코드 입력창, 확인/저장 버튼)
        2. 결과 영역 (상태, 품목명, 단위, 일치여부 등)
        3. 스캔 이력 테이블
        4. 하단 스캔 누계
        """
        # ====================================================================
        # 1. 입력 영역
        # ====================================================================
        frm_in = ttk.LabelFrame(self, text="입력")
        frm_in.pack(fill="x", pady=6)
        
        ttk.Label(frm_in, text="바코드 입력:").pack(side="left", padx=(10,6), pady=10)
        
        # 바코드 입력 필드
        self.entry_barcode = ttk.Entry(frm_in, width=36)
        self.entry_barcode.pack(side="left", padx=(0,10), pady=10)
        self.entry_barcode.bind("<Return>", lambda e: self.process_scan())  # Enter 키로 스캔
        
        # 버튼들
        ttk.Button(frm_in, text="확인(Enter)", command=self.process_scan).pack(side="left", padx=4)
        ttk.Button(frm_in, text="저장(Ctrl+S)", command=self.save_now).pack(side="left", padx=8)

        # ====================================================================
        # 2. 결과 영역
        # ====================================================================
        frm_info = ttk.LabelFrame(self, text="결과")
        frm_info.pack(fill="both", expand=True, pady=8)

        grid = ttk.Frame(frm_info)
        grid.pack(fill="x", padx=10, pady=10)

        # StringVar: 화면에 표시할 텍스트를 담는 변수 (자동 업데이트됨)
        self.var_status = tk.StringVar(value="대기 중")
        self.var_name = tk.StringVar()
        self.var_unit = tk.StringVar()
        self.var_code = tk.StringVar()
        self.var_match = tk.StringVar()
        self.var_saved = tk.StringVar(value="")

        # 라벨과 값 표시 (grid 레이아웃 사용)
        row = 0
        ttk.Label(grid, text="상태:").grid(row=row, column=0, sticky="w")
        ttk.Label(grid, textvariable=self.var_status, font=("맑은 고딕", 11, "bold")).grid(row=row, column=1, sticky="w", padx=8)

        row += 1
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

        # ====================================================================
        # 3. 스캔 이력 테이블 (Treeview)
        # ====================================================================
        self.tree = ttk.Treeview(
            frm_info, 
            columns=("time","barcode","result","item","unit"), 
            show="headings",  # 헤더만 표시 (첫 열 숨김)
            height=9
        )
        
        # 컬럼 설정: (컬럼ID, 너비, 헤더텍스트)
        for c, w, t in [
            ("time", 160, "시간"), 
            ("barcode", 170, "바코드"), 
            ("result", 80, "결과"), 
            ("item", 220, "품목명"), 
            ("unit", 60, "단위")
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=(4,10))

        # ====================================================================
        # 4. 하단 스캔 누계
        # ====================================================================
        frm_bottom = ttk.Frame(self)
        frm_bottom.pack(fill="x")
        self.var_counter = tk.StringVar(value="0 건")
        ttk.Label(frm_bottom, text="스캔 누계:").pack(side="left")
        ttk.Label(frm_bottom, textvariable=self.var_counter, font=("맑은 고딕", 10, "bold")).pack(side="left", padx=8)

    # ========================================================================
    # 액션 메서드 (스캔, 매칭, 저장 등)
    # ========================================================================
    def process_scan(self):
        """
        바코드 스캔 처리
        1. 입력창에서 바코드 읽기
        2. 중복 체크
        3. 마스터 파일에서 매칭 시도
        4. 매칭되면: 일치 처리 및 저장
        5. 안되면: 수동 검색 대화상자 표시
        """
        # 입력 받기
        raw = self.entry_barcode.get().strip()
        self.entry_barcode.delete(0, tk.END)  # 입력창 비우기
        
        if not raw:  # 빈 입력은 무시
            return
        
        barcode_norm = norm(raw)  # 바코드 정규화

        # ====================================================================
        # 중복 바코드 체크
        # ====================================================================
        if barcode_norm in self.scanned_barcodes:
            prev_info = self.scanned_barcodes[barcode_norm]
            messagebox.showwarning(
                "중복 바코드",
                f"⚠️ 이미 스캔한 바코드입니다!\n\n"
                f"바코드: {barcode_norm}\n"
                f"품목명: {prev_info['품목명']}\n"
                f"이전 스캔 시간: {prev_info['시간']}"
            )
            # 화면에는 표시하지만 로그에는 기록하지 않음
            self.var_status.set("중복")
            self.var_name.set(prev_info["품목명"])
            self.var_unit.set(prev_info["단위"])
            self.var_code.set(barcode_norm)
            self.var_match.set("⚠️ 중복")
            return

        # ====================================================================
        # 마스터 파일에서 매칭 시도
        # ====================================================================
        info = self._lookup_match(barcode_norm)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if info:
            # 매칭 성공!
            # 중복 체크용 딕셔너리에 저장
            self.scanned_barcodes[barcode_norm] = {
                "품목명": info["품목명"],
                "단위": info["단위"],
                "품목코드": info["품목코드"],
                "시간": now
            }
            
            # 화면 업데이트
            self.var_status.set("일치")
            self.var_name.set(info["품목명"])
            self.var_unit.set(info["단위"])
            self.var_code.set(barcode_norm)
            self.var_match.set("✅ 일치")
            
            # 로그에 기록 (메모리)
            self.add_log(now, barcode_norm, "일치", info["품목코드"], info["품목명"], info["단위"])
            
            # 즉시 저장 (중요한 데이터 손실 방지)
            self.save_now()
        else:
            # 매칭 실패 → 수동 검색 대화상자 표시
            self.open_search_dialog(barcode_norm)
            return

        # 스캔 누계 업데이트
        self.scan_count += 1
        self.var_counter.set(f"{self.scan_count} 건")
        
        # 30번마다 추가 자동저장 (혹시 모를 데이터 손실 방지)
        if self.scan_count % AUTOSAVE_INTERVAL == 0:
            self.save_now()

    def open_search_dialog(self, scanned_barcode):
        """
        품목 수동 검색 대화상자
        - 바코드가 마스터 파일에 없을 때 표시
        - 품목코드나 품목명으로 검색
        - 선택한 품목에 바코드를 매핑
        
        매개변수:
            scanned_barcode: 스캔한 바코드 (정규화되지 않은 원본)
        """
        # 대화상자 생성
        dlg = tk.Toplevel(self)
        dlg.title("품목 검색 (일치 없음)")
        dlg.geometry("720x500")
        dlg.transient(self)  # 부모 윈도우에 종속
        dlg.grab_set()  # 모달 다이얼로그 (다른 창 조작 불가)

        # ====================================================================
        # 상단: 스캔한 바코드 표시 및 검색창
        # ====================================================================
        top = ttk.Frame(dlg)
        top.pack(fill="x", pady=8, padx=10)
        
        ttk.Label(top, text=f"스캔 바코드: {scanned_barcode}").pack(side="left")
        ttk.Label(top, text="검색:").pack(side="left", padx=(18,6))
        
        var_q = tk.StringVar()  # 검색어 입력 변수
        ent = ttk.Entry(top, textvariable=var_q, width=30)
        ent.pack(side="left")
        ent.focus_set()  # 포커스를 검색창에

        # ====================================================================
        # 중간: 품목 리스트 테이블
        # ====================================================================
        cols = ("품목코드","품목명","단위","등록바코드","실제바코드")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=15)
        
        for c, w in [
            ("품목코드", 100),
            ("품목명", 240),
            ("단위", 60),
            ("등록바코드", 160),
            ("실제바코드", 160)
        ]:
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="center")
        
        tree.pack(fill="both", expand=True, padx=10, pady=(6,10))

        def refresh_table(query=""):
            """
            테이블 새로고침
            - 검색어가 있으면 품목코드나 품목명에 포함된 것만 표시
            """
            q = (query or "").strip().lower()
            tree.delete(*tree.get_children())  # 기존 항목 삭제
            
            df = self.master_df
            if q:  # 검색어가 있으면 필터링
                mask = df["품목코드"].str.lower().str.contains(q) | \
                       df["품목명"].str.lower().str.contains(q)
                df = df[mask]
            
            # 테이블에 행 추가
            for _, r in df.iterrows():
                tree.insert("", "end", values=(
                    r["품목코드"], 
                    r["품목명"], 
                    r["단위"], 
                    r["등록바코드"], 
                    r["실제바코드"]
                ))

        # 초기 테이블 로드 (전체 품목 표시)
        refresh_table()
        
        # 검색창에 입력할 때마다 테이블 새로고침
        ent.bind("<KeyRelease>", lambda e: refresh_table(var_q.get()))

        def choose_and_close():
            """
            품목 선택 및 대화상자 닫기
            - 선택한 품목의 품목코드를 가져와서 바코드 매핑
            """
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("안내","품목을 선택하세요.")
                return
            
            vals = tree.item(sel[0], "values")  # 선택한 행의 값들
            self.apply_mapping(scanned_barcode, vals[0])  # vals[0]은 품목코드
            dlg.destroy()

        # 더블클릭으로 선택
        tree.bind("<Double-1>", lambda e: choose_and_close())
        
        # ====================================================================
        # 하단: 선택 버튼
        # ====================================================================
        btnfrm = ttk.Frame(dlg)
        btnfrm.pack(fill="x", pady=6)
        ttk.Button(btnfrm, text="선택(Enter)", command=choose_and_close).pack(side="right", padx=10)
        
        # Enter 키로도 선택 가능
        dlg.bind("<Return>", lambda e: choose_and_close())

    def apply_mapping(self, scanned_barcode, chosen_code):
        """
        스캔한 바코드를 선택한 품목에 매핑
        
        매개변수:
            scanned_barcode: 스캔한 바코드
            chosen_code: 선택한 품목코드
        
        동작:
            1. 선택한 품목의 "실제바코드" 컬럼 업데이트
            2. 인덱스에 추가 (다음번엔 자동 매칭)
            3. 로그에 "수동지정"으로 기록
            4. 즉시 저장
        """
        # 품목코드로 행 찾기
        idx = self.master_df.index[self.master_df["품목코드"] == chosen_code]
        if len(idx) == 0:
            messagebox.showerror("오류","선택한 품목코드를 찾을 수 없습니다.")
            return
        
        i = idx[0]  # 첫 번째 매칭 행의 인덱스
        
        # DataFrame 업데이트
        self.master_df.at[i, "실제바코드"] = scanned_barcode
        self.master_df.at[i, "_n_real"] = norm(scanned_barcode)  # 정규화된 버전도 업데이트
        
        # 인덱스에 추가 (다음번엔 자동으로 매칭되도록)
        barcode_norm = norm(scanned_barcode)
        self._index[barcode_norm] = {
            "품목코드": self.master_df.at[i, "품목코드"],
            "품목명": self.master_df.at[i, "품목명"],
            "단위": self.master_df.at[i, "단위"],
            "등록바코드": self.master_df.at[i, "등록바코드"],
            "실제바코드": scanned_barcode,
        }
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 중복 체크용 딕셔너리에 저장
        self.scanned_barcodes[barcode_norm] = {
            "품목명": self.master_df.at[i, "품목명"],
            "단위": self.master_df.at[i, "단위"],
            "품목코드": self.master_df.at[i, "품목코드"],
            "시간": now
        }
        
        # 화면 업데이트
        self.var_status.set("수동지정")
        self.var_name.set(self.master_df.at[i, "품목명"])
        self.var_unit.set(self.master_df.at[i, "단위"])
        self.var_code.set(scanned_barcode)
        self.var_match.set("⚠️ 수동지정")
        
        # 로그에 기록
        self.add_log(
            now, 
            scanned_barcode, 
            "수동지정", 
            self.master_df.at[i, "품목코드"], 
            self.master_df.at[i, "품목명"], 
            self.master_df.at[i, "단위"]
        )
        
        # 즉시 저장 (매핑 정보 보존)
        self.save_now()

        # 스캔 누계 업데이트
        self.scan_count += 1
        self.var_counter.set(f"{self.scan_count} 건")
        
        if self.scan_count % AUTOSAVE_INTERVAL == 0:
            self.save_now()

    def add_log(self, ts, barcode, result, code, name, unit):
        """
        로그 추가
        1. 화면 테이블에 추가 (상단에 최신 항목)
        2. 메모리 리스트에 추가 (저장 전까지 임시 보관)
        
        매개변수:
            ts: 타임스탬프
            barcode: 바코드
            result: 결과 (일치/수동지정)
            code: 품목코드
            name: 품목명
            unit: 단위
        """
        # 화면 테이블에 추가 (맨 위에)
        self.tree.insert("", 0, values=(ts, barcode, result, name, unit))
        
        # 메모리에 저장 (나중에 엑셀로 저장)
        self.log_rows.append({
            "스캔시간": ts,
            "스캔바코드": barcode,
            "결과": result,
            "품목코드": code,
            "품목명": name,
            "단위": unit,
        })

    def save_now(self):
        """
        저장 실행
        1. master_updated.xlsx에 마스터 데이터 저장 (실제바코드 매핑 포함)
        2. scan_log.xlsx에 스캔 로그 추가 저장 (기존 로그에 이어서)
        """
        try:
            # ================================================================
            # 1. 마스터 데이터 저장
            # ================================================================
            # 정규화 컬럼(_n_reg, _n_real, _n_barcode)은 내부용이므로 제외
            safe_df = self.master_df.drop(
                columns=[c for c in ["_n_reg","_n_real","_n_barcode"] 
                        if c in self.master_df.columns]
            )
            safe_df.to_excel(MASTER_UPDATED, index=False)
            
            # ================================================================
            # 2. 스캔 로그 저장 (추가 모드)
            # ================================================================
            if self.log_rows:  # 저장할 로그가 있으면
                df_new = pd.DataFrame(self.log_rows)
                
                # 기존 로그 파일이 있으면 읽어서 합치기
                if os.path.exists(SCAN_LOG_FILE):
                    try:
                        df_old = pd.read_excel(SCAN_LOG_FILE, dtype=str).fillna("")
                        df_all = pd.concat([df_old, df_new], ignore_index=True)
                    except Exception:
                        # 파일이 손상되었으면 새로 시작
                        df_all = df_new
                else:
                    # 로그 파일이 없으면 새로 생성
                    df_all = df_new
                
                # 엑셀로 저장
                df_all.to_excel(SCAN_LOG_FILE, index=False)
                
                # 메모리 로그 초기화 (저장했으므로)
                self.log_rows = []
            
            # 화면 업데이트
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.var_status.set("저장 완료")
            self.var_saved.set(ts)
            
        except Exception as e:
            # 저장 실패 시 오류 메시지 표시
            messagebox.showerror("저장 오류", str(e))

    def on_close(self):
        """
        프로그램 종료 처리
        - 저장되지 않은 로그가 있으면 저장 여부 확인
        """
        if self.log_rows:  # 저장 안 된 로그가 있으면
            if messagebox.askyesno("종료 확인", "저장되지 않은 로그가 있습니다. 저장 후 종료할까요?"):
                self.save_now()
        self.destroy()

# ============================================================================
# 프로그램 시작
# ============================================================================
def main():
    """메인 함수: 애플리케이션 생성 및 실행"""
    app = BarcodeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)  # X 버튼 클릭 시 on_close 호출
    app.mainloop()  # GUI 이벤트 루프 시작

if __name__ == "__main__":
    main()
