# -*- coding: utf-8 -*-
# 🚀 EMP 자동화 최종 버전
# 달랏마트 ERP 시스템 자동화

import os
import time
import psutil
from pywinauto import Application, findwindows

def find_emp_process():
    """실행 중인 EMP 프로세스 찾기"""
    for p in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            name = (p.info['name'] or '').lower()
            if 'emp' in name and '.exe' in name:
                print(f"✅ EMP 프로세스 발견: {p.info['name']}, PID: {p.info['pid']}")
                return p.info['pid']
        except:
            continue
    return None

def connect_to_emp():
    """EMP에 연결하고 달랏마트 창 찾기"""
    pid = find_emp_process()
    if not pid:
        print("❌ EMP 프로세스를 찾을 수 없습니다.")
        return None, None
    
    app = Application(backend="uia").connect(process=pid)
    print(f"✅ EMP 프로세스에 연결 성공!")
    
    # 달랏마트 ERP 창 찾기
    all_windows = findwindows.find_windows(title_re=r".*")
    for handle in all_windows:
        try:
            window = app.window(handle=handle)
            title = window.window_text()
            if '달랏마트' in title and 'Enhanced Management Plus' in title:
                print(f"🎯 달랏마트 ERP 창 발견: {title}")
                return app, window
        except:
            continue
    
    print("❌ 달랏마트 ERP 창을 찾을 수 없습니다.")
    return app, None

def find_all_controls(win):
    """모든 컨트롤을 완전 탐색"""
    print("🔍 모든 컨트롤 탐색 중...")
    
    control_types = [
        "Button", "MenuItem", "Text", "Hyperlink", "ListItem", 
        "TreeItem", "TabItem", "Static", "Group", "Pane", 
        "Window", "MenuBar", "ToolBar", "Edit", "ComboBox"
    ]
    
    all_controls = []
    
    for control_type in control_types:
        try:
            controls = win.descendants(control_type=control_type)
            print(f"📋 {control_type:<12}: {len(controls):3d}개")
            
            for i, ctrl in enumerate(controls):
                try:
                    text_info = {}
                    
                    # 다양한 텍스트 속성 수집
                    try:
                        window_text = ctrl.window_text()
                        if window_text and window_text.strip():
                            text_info['window_text'] = window_text.strip()
                    except: pass
                    
                    try:
                        auto_id = ctrl.automation_id()
                        if auto_id and auto_id.strip():
                            text_info['automation_id'] = auto_id.strip()
                    except: pass
                    
                    try:
                        element_name = ctrl.element_info.name
                        if element_name and element_name.strip():
                            text_info['element_name'] = element_name.strip()
                    except: pass
                    
                    if text_info:
                        all_controls.append({
                            'type': control_type,
                            'index': i,
                            'element': ctrl,
                            'texts': text_info
                        })
                        
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ {control_type}: {e}")
    
    print(f"📊 총 발견된 컨트롤: {len(all_controls)}개")
    return all_controls

def search_controls(all_controls, keywords):
    """키워드로 컨트롤 검색"""
    matches = []
    for ctrl_info in all_controls:
        for text_type, text_value in ctrl_info['texts'].items():
            for keyword in keywords:
                if keyword in str(text_value):
                    matches.append({
                        'type': ctrl_info['type'],
                        'index': ctrl_info['index'],
                        'text_type': text_type,
                        'text_value': text_value,
                        'element': ctrl_info['element']
                    })
                    break
    return matches

def click_control(element, method='click'):
    """컨트롤 클릭"""
    try:
        if method == 'click':
            element.click()
        elif method == 'double_click':
            element.double_click()
        elif method == 'right_click':
            element.right_click()
        
        print(f"✅ 컨트롤 {method} 성공!")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"❌ 컨트롤 {method} 실패: {e}")
        return False

# 🚀 메인 실행 부분
if __name__ == "__main__":
    print("🚀 EMP 자동화 시작!")
    
    # 1. EMP 연결
    app, emp_window = connect_to_emp()
    
    if not emp_window:
        print("❌ EMP 연결 실패")
        exit()
    
    # 2. 모든 컨트롤 탐색
    all_controls = find_all_controls(emp_window)
    
    # 3. 상품 관련 컨트롤 검색
    keywords = ['상품', '관리', '단일옵션', '품목', '재고', '등록']
    matches = search_controls(all_controls, keywords)
    
    if matches:
        print(f"\n🎯 상품 관련 컨트롤 발견: {len(matches)}개")
        for i, match in enumerate(matches):
            print(f"[{i:2d}] {match['type']:<12}: '{match['text_value']}'")
        
        print(f"\n💡 사용 예시:")
        print(f"   # 상품그룹 버튼 클릭")
        print(f"   click_control(matches[0]['element'])")
        
        # 상품그룹 버튼이 있으면 자동 클릭 (주석 해제하려면)
        # if '상품그룹' in matches[0]['text_value']:
        #     print("🎯 상품그룹 버튼을 자동으로 클릭합니다...")
        #     click_control(matches[0]['element'])
        
    else:
        print("❌ 상품 관련 컨트롤을 찾지 못했습니다.")
        
    print("\n🎉 EMP 자동화 준비 완료!")
