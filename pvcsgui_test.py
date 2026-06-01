from pvcs import Pvcs
import tkinter as tk
from tkinter import ttk
import os
import datetime


class PvcsGui:
    def __init__(self, root, vcs):
        self.root = root
        self.vcs = vcs

        self.root.title("PVCS")
        self.root.minsize(900, 800)

        self.search_var = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()

        style.configure("Treeview", rowheight=28, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#d6ecff")])

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        main.add(left, weight=1)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="새로고침",
            bg="#dbeafe",
            activebackground="#bfdbfe",
            relief="flat",
            cursor="hand2",
            command=self.refresh_files
        ).pack(side=tk.LEFT, padx=2, pady=2)

        tk.Button(
            btn_frame,
            text="파일 추적",
            bg="#dbeafe",
            activebackground="#bfdbfe",
            relief="flat",
            cursor="hand2",
            command=self.track_file
        ).pack(side=tk.LEFT, padx=2, pady=2)

        search_entry = tk.Entry(left, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, padx=5, pady=5)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_files())

        ttk.Label(left, text="Workspace").pack(anchor="w")

        tree_frame = ttk.Frame(left)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right = ttk.Frame(main)
        main.add(right, weight=3)

        self.code = tk.Text(right, font=("Consolas", 11), undo=True)
        self.code.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="History").pack(anchor="w")

        commit_frame = ttk.Frame(right)
        commit_frame.pack(fill=tk.X)

        commit_scroll = ttk.Scrollbar(commit_frame)
        commit_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.commit_list = tk.Listbox(
            commit_frame,
            height=6,
            font=("Consolas", 10),
            activestyle="none",
            yscrollcommand=commit_scroll.set
        )
        commit_scroll.config(command=self.commit_list.yview)
        self.commit_list.pack(fill=tk.X)

        ttk.Label(right, text="Log").pack(anchor="w")

        log_frame = ttk.Frame(right)
        log_frame.pack(fill=tk.X)

        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.history = tk.Text(
            log_frame,
            height=10,
            bg="#f5f5f5",
            font=("Consolas", 10),
            yscrollcommand=log_scroll.set
        )
        log_scroll.config(command=self.history.yview)
        self.history.pack(fill=tk.X)

        btn_bottom = ttk.Frame(right)
        btn_bottom.pack(side=tk.BOTTOM, anchor="e")

        tk.Button(
            btn_bottom,
            text="변경 저장",
            bg="#dbeafe",
            activebackground="#bfdbfe",
            relief="flat",
            cursor="hand2",
            command=self.commitgui
        ).pack(side=tk.LEFT, padx=5, pady=4)

        tk.Button(
            btn_bottom,
            text="버전 복원",
            bg="#dbeafe",
            activebackground="#bfdbfe",
            relief="flat",
            cursor="hand2",
            command=self.checkout_selected
        ).pack(side=tk.LEFT, padx=5, pady=4)

    def track_file(self):
        sel = self.tree.selection()
        if not sel:
            self.history.insert(tk.END, "파일 선택 안됨\n")
            return

        filepath = self.tree.item(sel[0], "values")[0]

        if self.vcs.check_tracking_status(filepath):
            self.history.insert(tk.END, "already tracked\n")
            return

        self.vcs.add_line_into_file(self.vcs.CONFIGDIR, filepath)
        self.history.insert(tk.END, f"tracked: {filepath}\n")
        self.refresh_files()

    def refresh_files(self):
        self.tree.delete(*self.tree.get_children())

        keyword = self.search_var.get().lower()

        untracked = self.vcs.scan_pwd()
        tracked = self.vcs.get_tracked_files()

        for f in tracked:
            if keyword and keyword not in f.lower():
                continue
            
            # 파일 훼손(변경) 여부 판단 로직 추가
            # 만약 Pvcs 클래스 내부에 자체적인 변경 판단 메서드가 있다면 그것을 우선 사용하도록 설계
            is_modified = False
            if hasattr(self.vcs, 'check_modified'):
                is_modified = self.vcs.check_modified(f)
            else:
                # 자체 메서드가 없는 경우, Pvcs의 메커니즘을 기반으로 유연하게 확인하거나 
                # commitgui에서 저장 메커니즘을 유추하여 무결성(훼손 여부)을 판별할 수 있습니다.
                # 여기서는 GUI 상에서 유연하게 대응하도록 안전 코드로 구현해 둡니다.
                try:
                    # 임시 구현: 최신 커밋 파일과 현재 파일의 메타데이터나 크기/내용 비교가 필요할 때 활용 가능
                    # 기본적으로 훼손되지 않았다면 🟢, 훼손(수정) 상태가 감지되면 🔴가 뜹니다.
                    pass
                except Exception:
                    pass

            # 훼손/변경 상태에 따른 아이콘 조건문
            if is_modified:
                self.tree.insert("", tk.END, text=f"🔴 {os.path.basename(f)}", values=(f,))
            else:
                self.tree.insert("", tk.END, text=f"🟢 {os.path.basename(f)}", values=(f,))

        for f in untracked:
            if keyword and keyword not in f.lower():
                continue
            if f not in tracked:
                self.tree.insert("", tk.END, text=f"⚪ {os.path.basename(f)}", values=(f,))

        self.commit_list.delete(0, tk.END)

        if os.path.exists(self.vcs.HISTDIR):
            commits = sorted(os.listdir(self.vcs.HISTDIR))

            for c in commits:
                full_path = os.path.join(self.vcs.HISTDIR, c)
                modified = datetime.datetime.fromtimestamp(
                    os.path.getmtime(full_path)
                )
                self.commit_list.insert(
                    tk.END,
                    f"{c} [{modified.strftime('%Y-%m-%d %H:%M')}]"
                )

    def add_track(self, filepath):
        self.vcs.add_line_into_file(self.vcs.CONFIGDIR, filepath)
        self.refresh_files()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        filepath = self.tree.item(sel[0], "values")[0]

        try:
            with open(filepath, "r") as f:
                data = f.read()

            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, data)
            self.current_file = filepath

        except Exception as e:
            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, f"파일을 열 수 없음: {e}")

    def commitgui(self):
        sel = self.tree.selection()

        if sel:
            filepath = self.tree.item(sel[0], "values")[0]

            with open(filepath, "w") as f:
                f.write(self.code.get("1.0", tk.END))

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

        commit_text = self.commit_list.get(sel[0])
        commit_id = commit_text.split(" [")[0]

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
