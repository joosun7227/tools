#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import openpyxl

EXCEL_PATH = 'c:/Users/User/OneDrive/문서/3yejoo/그라미스Gromise/2.쇼핑몰/쇼핑몰_상품구성/2.상품명번역_지머니트랜스/상품가격_제출.xlsx'
PRODUCTS_PATH = 'c:/Users/User/OneDrive/문서/3yejoo/도구모음집/카탈로그만들기/catalog-app/data/products.json'
OUTPUT_PATH = 'c:/Users/User/OneDrive/문서/3yejoo/도구모음집/카탈로그만들기/catalog-app/data/translations.json'

# Load products
with open(PRODUCTS_PATH, encoding='utf-8') as f:
    products = json.load(f)

print(f"총 상품 수: {len(products)}")

# Load Excel
wb = openpyxl.load_workbook(EXCEL_PATH)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

print(f"Excel 총 행 수: {len(rows)}")
print(f"헤더 (row[1]): {rows[1]}")

# Build lookup from prodCd to translation data
# rows[0] = title, rows[1] = header, rows[2:] = data
# col[1]: EA prodCd, col[2]: ko name, col[7]: en name, col[11]: th name, col[12]: vi name
# col[16]: pack prodCd, col[20]: bundle prodCd, col[24]: box (대표) prodCd

excel_data = {}  # prodCd -> {ko, en, th, vi}

for row in rows[2:]:
    if not row[2]:  # skip rows without Korean name
        continue
    ko = str(row[2]).strip() if row[2] else ""
    en = str(row[7]).strip() if row[7] else ""
    th = str(row[11]).strip() if row[11] else ""
    vi = str(row[12]).strip() if row[12] else ""

    translation = {"ko": ko, "en": en, "th": th, "vi": vi}

    # Map all prodCds to this translation
    for col_idx in [1, 16, 20, 24]:
        if row[col_idx]:
            code = str(row[col_idx]).strip()
            if code:
                excel_data[code] = translation

print(f"Excel에서 읽은 코드 수: {len(excel_data)}")

# Build translations.json
translations = {}
matched = 0
unmatched = 0

for product in products:
    pid = str(product['id'])
    found = None

    for unit in product['units']:
        prod_cd = unit['prodCd']
        if prod_cd in excel_data:
            found = excel_data[prod_cd]
            break

    if found:
        translations[pid] = found
        matched += 1
    else:
        translations[pid] = {"ko": product['name'], "en": "", "th": "", "vi": ""}
        unmatched += 1

print(f"번역 매칭된 상품: {matched}")
print(f"번역 없는 상품 (ko만): {unmatched}")
print(f"translations.json 총 항목: {len(translations)}")

# Save
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"저장 완료: {OUTPUT_PATH}")

# Show a few examples
items = list(translations.items())[:3]
for pid, t in items:
    print(f"  ID {pid}: ko={t['ko'][:20]}, th={t['th'][:20] if t['th'] else '(없음)'}")
