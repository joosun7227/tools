"""
Excel 품목정보 -> Next.js 카탈로그용 products.json 변환 스크립트
"""
import pandas as pd
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "품목정보.xlsx")
IMAGE_DIR = r"C:\Users\User\OneDrive\문서\3yejoo\그라미스Gromise\2.쇼핑몰\쇼핑몰_상품구성\그라미스상품사진\그라미스상품사진_최종본_260128"
OUTPUT_PATH = os.path.join(BASE_DIR, "catalog-app", "data", "products.json")
META_OUTPUT_PATH = os.path.join(BASE_DIR, "catalog-app", "data", "meta.json")

def main():
    print("품목정보.xlsx 로딩 중...")
    df = pd.read_excel(EXCEL_PATH)

    df = df[
        (df["단위 EA,PACK,BOX,KG,포"] == "EA") &
        (df["소비자가"].notna()) &
        (df["소비자가"] > 0)
    ].copy()
    print(f"유효 품목 수: {len(df)}")

    img_files = set()
    if os.path.isdir(IMAGE_DIR):
        for f in os.listdir(IMAGE_DIR):
            if f.lower().endswith(".png"):
                img_files.add(f[:-4])
    print(f"이미지 파일 수: {len(img_files)}")

    def get_image_filename(name):
        if name in img_files:
            return name + ".png"
        if (name + "-Photoroom") in img_files:
            return name + "-Photoroom.png"
        return None

    products = []
    for _, row in df.iterrows():
        name = str(row["품목명"]).strip()
        img_file = get_image_filename(name)

        barcode = ""
        if pd.notna(row["바코드"]):
            barcode = str(int(row["바코드"])) if isinstance(row["바코드"], float) else str(row["바코드"])

        prod_cd = str(int(row["품목코드"])).zfill(8)

        products.append({
            "id": int(row["품목코드"]),
            "prodCd": prod_cd,
            "name": name,
            "barcode": barcode,
            "country": str(row["국가명"]) if pd.notna(row["국가명"]) else "",
            "brand": str(row["브랜드"]) if pd.notna(row["브랜드"]) else "",
            "category": str(row["카테고리명"]) if pd.notna(row["카테고리명"]) else "",
            "spec": str(row["규격정보"]) if pd.notna(row["규격정보"]) else "",
            "storage": str(row["냉동/냉장명"]) if pd.notna(row["냉동/냉장명"]) else "",
            "price": int(row["소비자가"]),
            "imageFile": img_file,
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"products.json 완료: {len(products)}개 품목, 이미지 있음: {sum(1 for p in products if p['imageFile'])}개")

    categories = sorted(set(p["category"] for p in products if p["category"]))
    countries = sorted(set(p["country"] for p in products if p["country"]))
    storages = sorted(set(p["storage"] for p in products if p["storage"]))
    meta = {"categories": categories, "countries": countries, "storages": storages}
    with open(META_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"meta.json 완료")

if __name__ == "__main__":
    main()
