from pvcs import Pvcs
import tkinter as tk
from tkinter import ttk

##############
import os

##############

"""
Track file 버튼 Checkout 버튼 및 기능 구현
Track file Refresh Checkout Commit버튼 재배치
파일 선택 후 파일 수정 기능 구현
"""


class PvcsGui:
    def __init__(self, root, vcs):
        # GUI 초기화, pvcs 연결
        self.root = root
        self.vcs = vcs

        self.root.title("PVCS")
        self.root.minsize(900, 800)

        self.build_ui()

    def build_ui(self):
        # 전체 UI 레이아웃
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        # 왼쪽: 파일 리스트
        left = ttk.Frame(main)
        main.add(left, weight=1)

        # 왼쪽 버튼 정렬
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X)
        # Refresh 버튼
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_files).pack(side=tk.LEFT)
        # Track 버튼 
        ttk.Button(btn_frame, text="Track File", command=self.track_file).pack(side=tk.LEFT)

        ttk.Label(left, text="Workspace").pack(anchor="w")

        # 파일 리스트
        self.tree = ttk.Treeview(left)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # 오른쪽: 코드 + 히스토리 + 버튼
        right = ttk.Frame(main)
        main.add(right, weight=3)

        btn_bottom = ttk.Frame(right)
        btn_bottom.pack(side=tk.BOTTOM, anchor="e")

        # 파일 내용 표시
        self.code = tk.Text(right)
        self.code.pack(fill=tk.BOTH, expand=True)

        # Commit 히스토리 이름
        ttk.Label(right, text="History").pack(anchor="w")

        # Commit list
        self.commit_list = tk.Listbox(right, height=6)
        self.commit_list.pack(fill=tk.X)

        # Log name
        ttk.Label(right, text="Log").pack(anchor="w")

        # Commit 히스토리 표시
        self.history = tk.Text(right, height=10)
        self.history.pack(fill=tk.X)

        # Commit 버튼
        ttk.Button(btn_bottom, text="Commit", command=self.commitgui).pack(side=tk.LEFT, padx=5)
        # Checkout 버튼
        ttk.Button(btn_bottom, text="Checkout", command=self.checkout_selected).pack(side=tk.LEFT, padx=5)

    def track_file(self):
        sel = self.tree.selection()

        if not sel:
            self.history.insert(tk.END, "파일 선택 안됨\n")
            return

        values = self.tree.item(sel[0], "values")

        if not values:
            return

        filepath = values[0]

        print("TRACK CLICK:", filepath)
        # 이미 tracked면 무시
        if self.vcs.check_tracking_status(filepath):
            self.history.insert(tk.END, "already tracked\n")
            return

        # tracked 등록
        self.vcs.add_line_into_file(self.vcs.CONFIGDIR, filepath)

        print("CONFIG AFTER TRACK:")
        print(self.vcs.read_from_file(self.vcs.CONFIGDIR))
        # with open(self.vcs.CONFIGDIR, "r") as f:
        #    print(f.read())

        self.history.insert(tk.END, f"tracked: {filepath}\n")
        self.refresh_files()

    def refresh_files(self):
        # 파일 목록 업로드
        self.tree.delete(*self.tree.get_children())

        untracked = self.vcs.scan_pwd()
        tracked = self.vcs.get_tracked_files()

        # print("NOT IGNORED:", untracked)
        # print("TRACKED:", tracked)

        for f in tracked:
            self.tree.insert("", tk.END, text=f"☑ {f}", values=(f,))

        for f in untracked:
            if f not in tracked:
                self.tree.insert("", tk.END, text=f"☐ {f}", values=(f,))

        # commit 리스트 갱신
        self.commit_list.delete(0, tk.END)

        commit_dir = self.vcs.HISTDIR

        if os.path.exists(commit_dir):
            commits = sorted(os.listdir(commit_dir))

            for c in commits:
                self.commit_list.insert(tk.END, c)

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

        file_content = self.vcs.read_from_file(filepath)
        if not file_content:
            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, f"파일을 열 수 없음")

        self.code.delete("1.0", tk.END)
        self.code.insert(tk.END, file_content)
        self.current_file = filepath
        '''
        try:
            with open(filepath, "r") as f:
                data = f.read()

            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, data)

            self.current_file = filepath

        except Exception as e:
            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, f"파일을 열 수 없음: {e}")
        '''

    def commitgui(self):
        sel = self.tree.selection()

        if sel:
            values = self.tree.item(sel[0], "values")

            if values:
                filepath = values[0]
                # text -> 실제 파일 저장
                with open(filepath, "w") as f:
                    f.write(self.code.get("1.0", tk.END))

        # commit 실행
        if self.vcs.commit():
            self.history.insert(tk.END, "Commit 성공\n")
            self.refresh_files()
        else:
            self.history.insert(tk.END, "변경 안됨\n")

    def checkout_selected(self):
        sel = self.commit_list.curselection()

        if not sel:
            self.history.insert(tk.END, "no commit selected\n")
            return

        commit_id = self.commit_list.get(sel[0])

        if self.vcs.checkout(commit_id):
            self.history.insert(tk.END, f"checkout: {commit_id}\n")
            self.refresh_files()
        else:
            self.history.insert(tk.END, "checkout failed\n")


if __name__ == "__main__":
    root = tk.Tk()
    vcs = Pvcs()
    app = PvcsGui(root, vcs)
    root.mainloop()
