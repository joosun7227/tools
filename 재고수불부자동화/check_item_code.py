# -*- coding: utf-8 -*-
import pandas as pd

# 수불부
df1 = pd.read_excel("df_suful_100.xlsx")
print("=== df_suful_100.xlsx ===")
print("columns:", list(df1.columns))
item_col = [c for c in df1.columns if "품목" in c or "코드" in c]
if item_col:
    c = item_col[0]
    s = df1[c].dropna().astype(str).head(25)
    print("품목 컬럼:", c, "dtype:", df1[c].dtype)
    print("샘플:", s.tolist())

# 보세 (경로: Input data 또는 input data 확인)
import os
path_bonded = "Input data/보세수불부_원본.xlsx"
if not os.path.exists(path_bonded):
    path_bonded = "input data/보세수불부_원본.xlsx"
df2 = pd.read_excel(path_bonded)
print("\n=== 보세수불부_원본.xlsx ===")
print("columns:", list(df2.columns))
item_col2 = [c for c in df2.columns if "품목" in c or "코드" in c]
if item_col2:
    c = item_col2[0]
    s = df2[c].dropna().astype(str).head(25)
    print("품목 컬럼:", c, "dtype:", df2[c].dtype)
    print("샘플:", s.tolist())
