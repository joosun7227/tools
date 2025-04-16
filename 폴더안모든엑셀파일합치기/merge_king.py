import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# 실제 엑셀을 합치는 함수
def combine_excels(root_dir):
    combined_df = pd.DataFrame()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.xlsx') and not filename.startswith('~$'):
                file_path = os.path.join(dirpath, filename)

                try:
                    xls = pd.ExcelFile(file_path)
                    for sheet_name in xls.sheet_names:
                        df = xls.parse(sheet_name)
                        df['파일명'] = filename
                        df['파일_경로'] = file_path
                        df['시트명'] = sheet_name
                        df['상위_폴더'] = os.path.basename(dirpath)
                        combined_df = pd.concat([combined_df, df], ignore_index=True)
                except Exception as e:
                    print(f"❌ 오류: {file_path} - {e}")

    # 결과 저장
    output_path = os.path.join(root_dir, '합친파일.xlsx')
    combined_df.to_excel(output_path, index=False, engine='openpyxl')
    return output_path

# 폴더 선택하고 합치기 실행하는 함수
def select_folder():
    folder = filedialog.askdirectory()

    if folder:
        try:
            output_file = combine_excels(folder)
            messagebox.showinfo("완료", f"🎉 합친 파일 저장 완료!\n\n{output_file}")
        except Exception as e:
            messagebox.showerror("에러 발생", f"❌ 오류: {str(e)}")
    else:
        messagebox.showwarning("폴더 없음", "폴더를 선택해줘!")

# GUI 생성
root = tk.Tk()
root.title("엑셀 파일 합치기")
root.geometry("400x180")

label = tk.Label(root, text="엑셀 파일들이 들어 있는 폴더를 선택해줘!", pady=20)
label.pack()

button = tk.Button(root, text="📁 폴더 선택 및 실행", command=select_folder, width=30, height=2)
button.pack()

root.mainloop()
