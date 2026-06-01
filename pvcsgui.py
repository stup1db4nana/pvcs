from pvcs import Pvcs
import tkinter as tk
from tkinter import ttk

class PvcsGui:
    def __init__(self, root, vcs):
        #GUI 초기화, pvcs 연결
        self.root = root
        self.vcs = vcs

        self.root.title("PVCS")
        self.root.geometry("1000x600")

        self.build_ui()

    def build_ui(self):
        #전체 UI 레이아웃
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        # 왼쪽: 파일 리스트
        left = ttk.Frame(main)
        main.add(left, weight=1)

        ttk.Label(left, text="Workspace").pack(anchor="w")

        self.tree = ttk.Treeview(left)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # 오른쪽: 코드 + 히스토리 + 버튼
        right = ttk.Frame(main)
        main.add(right, weight=3)

        # 상단 Refrsh 버튼
        refbar = ttk.Frame(right)
        refbar.pack(fill=tk.X)

        ttk.Button(refbar, text="Refresh", command=self.refresh_files).pack(side=tk.RIGHT)

        # 파일 내용 표시
        self.code = tk.Text(right)
        self.code.pack(fill=tk.BOTH, expand=True)

        # Commit 히스토리 표시
        self.history = tk.Text(right, height=10)
        self.history.pack(fill=tk.X)

        # Commit 버튼
        ttk.Button(right, text="Commit", command=self.commitgui).pack(side=tk.BOTTOM, anchor="e")        


    def refresh_files(self):
        # 파일 목록 업로드
        self.tree.delete(*self.tree.get_children())

        files = self.vcs.get_tracked_files()

        if not files:
            files = self.vcs.scan_pwd()

        for f in files:
            check = "☑" if self.vcs.check_tracking_status(f) else "☐"
            self.tree.insert("", tk.END, text=f"{check} {f}")

    def on_select(self, event):
        # 파일 클릭 시 해당 파일 로드
        sel = self.tree.selection()

        if not sel:
            return
        
        text = self.tree.item(sel[0], "text")
        filepath = text[2:] #체크표시 제거

        try:
            with open(filepath, "r") as f:
                data = f.read()

            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, data)

        except:
            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, "파일을 열 수 없음")

    def commitgui(self):
        if self.vcs.commit():
            self.history.insert(tk.END, "Commit 성공\n")
            self.refresh_files()
        else:
            self.history.insert(tk.END, "변경 안됨\n")


if __name__ == "__main__":
    
    root = tk.Tk()
    vcs = Pvcs()
    app = PvcsGui(root, vcs)
    root.mainloop()


