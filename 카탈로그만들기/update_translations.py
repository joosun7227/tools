"""
products.json 기준으로 translations.json을 최신화:
1) 누락 ID 추가 (ko = 상품명)
2) 빈 en / th / vi 를 Google 자동번역으로 채움
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
from deep_translator import GoogleTranslator

BASE = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_PATH = os.path.join(BASE, "catalog-app", "data", "products.json")
TRANS_PATH = os.path.join(BASE, "catalog-app", "data", "translations.json")

with open(PRODUCTS_PATH, encoding="utf-8") as f:
    products = json.load(f)
with open(TRANS_PATH, encoding="utf-8") as f:
    translations = json.load(f)

added = 0
for p in products:
    pid = str(p["id"])
    if pid not in translations:
        translations[pid] = {"ko": p["name"], "en": "", "th": "", "vi": ""}
        added += 1
    else:
        if not translations[pid].get("ko"):
            translations[pid]["ko"] = p["name"]
print(f"기존 ID: {len(translations) - added}, 신규 추가: {added}")

targets = [
    ("en", GoogleTranslator(source="ko", target="en")),
    ("th", GoogleTranslator(source="ko", target="th")),
    ("vi", GoogleTranslator(source="ko", target="vi")),
]

counters = {k: 0 for k, _ in targets}
errors = 0
total_to_do = sum(
    1 for t in translations.values() for lang, _ in targets if not t.get(lang) and t.get("ko")
)
print(f"번역 필요 항목 수(총): {total_to_do}")

done = 0
for pid, t in translations.items():
    ko = t.get("ko", "")
    if not ko:
        continue
    for lang, tr in targets:
        if t.get(lang):
            continue
        try:
            t[lang] = tr.translate(ko)
            counters[lang] += 1
        except Exception as e:
            errors += 1
            print(f"  [{pid}][{lang}] 오류: {e}")
        done += 1
        if done % 50 == 0:
            print(f"  진행 {done}/{total_to_do}  en={counters['en']} th={counters['th']} vi={counters['vi']} err={errors}")
        time.sleep(0.25)

print(f"완료: en={counters['en']}, th={counters['th']}, vi={counters['vi']}, 오류={errors}")

with open(TRANS_PATH, "w", encoding="utf-8") as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)
print(f"저장: {TRANS_PATH}")
