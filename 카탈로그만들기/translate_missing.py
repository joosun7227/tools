#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from deep_translator import GoogleTranslator

TRANSLATIONS_PATH = 'c:/Users/User/OneDrive/문서/3yejoo/도구모음집/카탈로그만들기/catalog-app/data/translations.json'

with open(TRANSLATIONS_PATH, encoding='utf-8') as f:
    translations = json.load(f)

# Count items needing translation
need_th = [(pid, t) for pid, t in translations.items() if not t['th'] and t['ko']]
need_vi = [(pid, t) for pid, t in translations.items() if not t['vi'] and t['ko']]
print(f"태국어 번역 필요: {len(need_th)}개")
print(f"베트남어 번역 필요: {len(need_vi)}개")

ko_to_th = GoogleTranslator(source='ko', target='th')
ko_to_vi = GoogleTranslator(source='ko', target='vi')

th_done = 0
vi_done = 0
errors = 0

for pid, t in translations.items():
    if not t['th'] and t['ko']:
        try:
            t['th'] = ko_to_th.translate(t['ko'])
            th_done += 1
            time.sleep(0.3)
        except Exception as e:
            errors += 1
            print(f"  th 번역 오류 [{pid}]: {e}")
    if not t['vi'] and t['ko']:
        try:
            t['vi'] = ko_to_vi.translate(t['ko'])
            vi_done += 1
            time.sleep(0.3)
        except Exception as e:
            errors += 1
            print(f"  vi 번역 오류 [{pid}]: {e}")

    if (th_done + vi_done) % 50 == 0 and (th_done + vi_done) > 0:
        print(f"  진행중... th:{th_done}, vi:{vi_done}, 오류:{errors}")

print(f"\n완료: th={th_done}개, vi={vi_done}개, 오류={errors}개")

# Save
with open(TRANSLATIONS_PATH, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"저장 완료: {TRANSLATIONS_PATH}")
