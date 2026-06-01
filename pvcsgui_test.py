from pvcs import Pvcs
import tkinter as tk
from tkinter import ttk

import os
import datetime
import shutil


class PvcsGui:
    def __init__(self, root, vcs):
        self.root = root
        self.vcs = vcs

        self.root.title("PVCS")
        self.root.minsize(900, 800)

        self.build_ui()

    def build_ui(self):
        style = ttk.Style()

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#d6ecff")]
        )

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        main.add(left, weight=1)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame,
            text="Refresh",
            bg="#cfefff",
            activebackground="#b8e6ff",
            font=("Arial", 10, "bold"),
            command=self.refresh_files
        ).pack(side=tk.LEFT, padx=2, pady=2)

        tk.Button(
            btn_frame,
            text="Track File",
            bg="#d8f8d8",
            activebackground="#c7f0c7",
            font=("Arial", 10, "bold"),
            command=self.track_file
        ).pack(side=tk.LEFT, padx=2, pady=2)

        ttk.Label(left, text="Workspace").pack(anchor="w")

        self.tree = ttk.Treeview(left)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right = ttk.Frame(main)
        main.add(right, weight=3)

        btn_bottom = ttk.Frame(right)
        btn_bottom.pack(side=tk.BOTTOM, anchor="e")

        self.code = tk.Text(
            right,
            font=("Consolas", 11),
            undo=True
        )
        self.code.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="History").pack(anchor="w")

        self.commit_list = tk.Listbox(
            right,
            height=6,
            font=("Consolas", 10),
            activestyle="none"
        )
        self.commit_list.pack(fill=tk.X)

        ttk.Label(right, text="Log").pack(anchor="w")

        self.history = tk.Text(
            right,
            height=10,
            bg="#f5f5f5",
            font=("Consolas", 10)
        )
        self.history.pack(fill=tk.X)

        tk.Button(
            btn_bottom,
            text="Commit",
            bg="#fff0b3",
            activebackground="#ffe680",
            font=("Arial", 10, "bold"),
            command=self.commitgui
        ).pack(side=tk.LEFT, padx=5, pady=4)

        tk.Button(
            btn_bottom,
            text="Checkout",
            bg="#ffd9b3",
            activebackground="#ffcc99",
            font=("Arial", 10, "bold"),
            command=self.checkout_selected
        ).pack(side=tk.LEFT, padx=5, pady=4)

    def track_file(self):
        sel = self.tree.selection()

        if not sel:
            self.history.insert(tk.END, "파일 선택 안됨\n")
            self.history.see(tk.END)
            return

        values = self.tree.item(sel[0], "values")

        if not values:
            return

        filepath = values[0]

        print("TRACK CLICK:", filepath)

        if self.vcs.check_tracking_status(filepath):
            self.history.insert(tk.END, "already tracked\n")
            self.history.see(tk.END)
            return

        self.vcs.add_line_into_file(self.vcs.CONFIGDIR, filepath)

        print("CONFIG AFTER TRACK:")
        with open(self.vcs.CONFIGDIR, "r") as f:
            print(f.read())

        self.history.insert(tk.END, f"tracked: {filepath}\n")
        self.history.see(tk.END)

        self.refresh_files()

    def refresh_files(self):
        self.tree.delete(*self.tree.get_children())

        untracked = self.vcs.scan_pwd()
        tracked = self.vcs.get_tracked_files()

        for f in tracked:
            self.tree.insert(
                "",
                tk.END,
                text=f"🟢 {os.path.basename(f)}",
                values=(f,)
            )

        for f in untracked:
            if f not in tracked:
                self.tree.insert(
                    "",
                    tk.END,
                    text=f"⚪ {os.path.basename(f)}",
                    values=(f,)
                )

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

            self.current_file = filepath

        except Exception as e:
            self.code.delete("1.0", tk.END)
            self.code.insert(tk.END, f"파일을 열 수 없음: {e}")

    def commitgui(self):
        sel = self.tree.selection()

        if sel:
            values = self.tree.item(sel[0], "values")

            if values:
                filepath = values[0]

                with open(filepath, "w") as f:
                    f.write(self.code.get("1.0", tk.END))

        if self.vcs.commit():
            self.history.insert(tk.END, "Commit 성공\n")
            self.history.see(tk.END)
            self.refresh_files()
        else:
            self.history.insert(tk.END, "변경 안됨\n")
            self.history.see(tk.END)

    def checkout_selected(self):
        sel = self.commit_list.curselection()

        if not sel:
            self.history.insert(tk.END, "no commit selected\n")
            self.history.see(tk.END)
            return

        commit_id = self.commit_list.get(sel[0])

        if self.vcs.checkout(commit_id):
            self.history.insert(tk.END, f"checkout: {commit_id}\n")
            self.history.see(tk.END)
            self.refresh_files()
        else:
            self.history.insert(tk.END, "checkout failed\n")
            self.history.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    vcs = Pvcs()
    app = PvcsGui(root, vcs)
    root.mainloop()
