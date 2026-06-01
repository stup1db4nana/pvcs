from pvcs import Pvcs
import tkinter as tk
from tkinter import ttk
import os
import datetime
import filecmp


class PvcsGui:
    def __init__(self, root, vcs):
        self.root = root
        self.vcs = vcs
        self.current_file = None

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
        main.pane(left, minsize=200)

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
        main.pane(right, minsize=100)

        self.code = tk.Text(right, font=("Consolas", 11), undo=True)
        self.code.pack(fill=tk.BOTH, expand=True)
        
        self.code.bind("<KeyRelease>", lambda e: self.save_current_text_silently())

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

    def save_current_text_silently(self):
        if hasattr(self, 'current_file') and self.current_file and os.path.exists(self.current_file):
            try:
                content = self.code.get("1.0", tk.END + "-1c")
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                selected_item = self.tree.selection()
                self.refresh_files()
                if selected_item:
                    for item in self.tree.get_children():
                        if self.tree.item(item, "values")[0] == self.current_file:
                            self.tree.selection_set(item)
                            break
            except Exception:
                pass

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

        latest_commit = None
        if os.path.exists(self.vcs.HISTDIR) and os.listdir(self.vcs.HISTDIR):
            sorted_commit_list = sorted(os.listdir(self.vcs.HISTDIR))
            latest_commit = os.path.join(self.vcs.HISTDIR, sorted_commit_list[-1])

        for f in tracked:
            if keyword and keyword not in f.lower():
                continue
            
            is_modified = False
            
            if latest_commit and os.path.exists(f):
                comp_file = os.path.join(latest_commit, f)
                if os.path.exists(comp_file):
                    if not filecmp.cmp(comp_file, f, shallow=False):
                        is_modified = True
                else:
                    is_modified = True

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
        if hasattr(self, 'current_file') and self.current_file and os.path.exists(self.current_file):
            try:
                content = self.code.get("1.0", tk.END + "-1c")
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception:
                pass

        sel = self.tree.selection()
        if not sel:
            return

        filepath = self.tree.item(sel[0], "values")[0]

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
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

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.code.get("1.0", tk.END + "-1c"))

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
            
            if hasattr(self, 'current_file') and self.current_file and os.path.exists(self.current_file):
                try:
                    with open(self.current_file, "r", encoding="utf-8", errors="ignore") as f:
                        restored_data = f.read()
                    self.code.delete("1.0", tk.END)
                    self.code.insert(tk.END, restored_data)
                except Exception:
                    pass
            
            self.refresh_files()
        else:
            self.history.insert(tk.END, "checkout failed\n")


if __name__ == "__main__":
    root = tk.Tk()
    vcs = Pvcs()
    
    vcs.create_dirs(vcs.HISTDIR)
    vcs.create_file(vcs.CONFIGDIR)
    vcs.create_file(vcs.IGNOREDIR)
    
    app = PvcsGui(root, vcs)
    root.mainloop()
