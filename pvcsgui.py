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
        ttk.Button(right, text="Track File", command=self.track_file).pack(side=tk.TOP, anchor="e")

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

    def track_file(self):
        sel = self.tree.selection()

        if not sel:
            self.history.insert(tk.END, "파일 선택 안됨\n")
            return
        
        text = self.tree.item(sel[0], "text")
        filepath = text[2:]

        # 이미 tracked면 무시
        if self.vcs.check_tracking_status(filepath):
            self.history.insert(tk.END, "already tracked\n")
            return
        
        # tracked 등록
        self.vcs.add_line_into_file(self.vcs.CONFIGDIR, filepath)
        self.history.insert(tk.END, f"tracked: {filepath}\n")
        self.refresh_files()

    def refresh_files(self):
        # 파일 목록 업로드
        self.tree.delete(*self.tree.get_children())

        untracked = self.vcs.scan_pwd()
        tracked = self.vcs.get_tracked_files()

        for f in tracked:
            self.tree.insert("", tk.END, text=f"☑ {f}", values=(f,))
        
        for f in untracked:
            if f not in tracked:
                self.tree.insert("", tk.END, text=f"☐ {f}", values=(f,))
            

    def add_track(self, filepath):
        self.vcs.add_line_into_file(self.vcs.CONFIGDIR, filepath)
        self.refresh_files()

    def on_select(self, event):
        # 파일 클릭 시 해당 파일 로드
        sel = self.tree.selection()

        if not sel:
            return
        
        values = self.tree.item(sel[0], "values")

        if not values:
            return

        filepath = values[0]
        
        try:
            with open(filepath, "r") as f:
                data = f.read()

            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, data)

        except Exception as e:
            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, f"파일을 열 수 없음: {e}")

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

