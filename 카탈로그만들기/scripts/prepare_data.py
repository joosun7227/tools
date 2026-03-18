"""
Excel 품목정보 -> Next.js 카탈로그용 products.json 변환 스크립트
대표품목코드 기준으로 그루핑, 단위(EA/BOX/PACK 등) 옵션 포함
"""
import pandas as pd
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "품목정보.xlsx")
IMAGE_DIR = os.path.join(BASE_DIR, "catalog-app", "public", "images")
OUTPUT_PATH = os.path.join(BASE_DIR, "catalog-app", "data", "products.json")
META_OUTPUT_PATH = os.path.join(BASE_DIR, "catalog-app", "data", "meta.json")

UNIT_ORDER = ["BOX", "PACK", "BUNDLE", "KG", "EA", "포"]

def unit_sort_key(u):
    try:
        return UNIT_ORDER.index(u)
    except ValueError:
        return len(UNIT_ORDER)

def main():
    print("품목정보.xlsx 로딩 중...")
    df = pd.read_excel(EXCEL_PATH)

    col_prodcd   = df.columns[0]   # 품목코드
    col_unit     = df.columns[3]   # 단위
    col_spec     = df.columns[4]   # 규격정보
    col_storage  = df.columns[11]  # 냉동/냉장명
    col_country  = df.columns[12]  # 국가명
    col_brand    = df.columns[13]  # 브랜드
    col_category = df.columns[14]  # 카테고리명
    col_price    = df.columns[18]  # 소비자가
    col_repcd    = df.columns[26]  # 대표품목코드
    col_repnm    = df.columns[27]  # 대표품목명

    df = df[df[col_repcd].notna() & (df[col_price] > 0)].copy()
    print(f"유효 품목 수: {len(df)}")

    img_files = {}  # stem → filename (확장자 포함)
    if os.path.isdir(IMAGE_DIR):
        for f in os.listdir(IMAGE_DIR):
            lower = f.lower()
            if lower.endswith((".png", ".jpg", ".jpeg")):
                stem = f.rsplit(".", 1)[0]
                img_files[stem] = f
    print(f"이미지 파일 수: {len(img_files)}")

    def get_image_filename(name):
        if name in img_files:
            return img_files[name]
        if (name + "-Photoroom") in img_files:
            return img_files[name + "-Photoroom"]
        return None

    products = []
    for rep_cd, group in df.groupby(col_repcd):
        rep_cd_int = int(rep_cd)
        first = group.iloc[0]
        rep_nm = str(first[col_repnm]).strip()
        img_file = get_image_filename(rep_nm)

        units = []
        for _, row in group.iterrows():
            unit_val  = str(row[col_unit]).strip()
            spec_val  = str(row[col_spec]).strip() if pd.notna(row[col_spec]) else ""
            price_val = int(row[col_price])
            prod_cd_val = str(int(row[col_prodcd])).zfill(8)
            units.append({"prodCd": prod_cd_val, "unit": unit_val, "price": price_val, "spec": spec_val})
        units.sort(key=lambda u: unit_sort_key(u["unit"]))

        products.append({
            "id": rep_cd_int,
            "name": rep_nm,
            "country":  str(first[col_country])  if pd.notna(first[col_country])  else "",
            "brand":    str(first[col_brand])    if pd.notna(first[col_brand])    else "",
            "category": str(first[col_category]) if pd.notna(first[col_category]) else "",
            "storage":  str(first[col_storage])  if pd.notna(first[col_storage])  else "",
            "imageFile": img_file,
            "units": units,
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    img_count = sum(1 for p in products if p["imageFile"])
    print(f"products.json 완료: {len(products)}개 상품, 이미지 있음: {img_count}개")

    categories = sorted(set(p["category"] for p in products if p["category"]))
    countries  = sorted(set(p["country"]  for p in products if p["country"]))
    storages   = sorted(set(p["storage"]  for p in products if p["storage"]))
    meta = {"categories": categories, "countries": countries, "storages": storages}
    with open(META_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("meta.json 완료")

if __name__ == "__main__":
    main()
