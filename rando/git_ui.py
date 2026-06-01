import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox


class GitHubMethodAdapter:
    def __init__(self):
        self.repo_path = None

    def connect_repository(self, repo_path):
        self.repo_path = repo_path

    def is_connected(self):
        if not self.repo_path:
            return False

        git_folder = os.path.join(self.repo_path, ".git")
        return os.path.exists(git_folder)

    def run_git(self, command):
        if not self.repo_path:
            return False, "저장소가 선택되지 않았습니다."

        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                text=True,
                capture_output=True
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except Exception as e:
            return False, str(e)

    def get_changed_files(self):
        if not self.is_connected():
            return self.get_dummy_changed_files()

        success, output = self.run_git(["git", "status", "--porcelain"])

        if not success:
            return []

        files = []

        if not output:
            return files

        for line in output.splitlines():
            status = line[:2].strip()
            filename = line[3:].strip()

            files.append({
                "filename": filename,
                "status": status,
                "changed": True
            })

        return files

    def get_file_diff(self, filename):
        if not self.is_connected():
            return self.get_dummy_diff(filename)

        success, output = self.run_git(["git", "diff", "--", filename])

        if success and output:
            return output

        success, output = self.run_git(["git", "diff", "--cached", "--", filename])

        if success and output:
            return output

        return "해당 파일의 변경 내용을 찾을 수 없습니다.\n이미 ADD 되었거나 diff가 없는 파일일 수 있습니다."

    def add_file(self, filename):
        if not self.is_connected():
            return True, f"[더미 실행] {filename} 파일이 ADD 처리되었습니다."

        return self.run_git(["git", "add", filename])

    def commit_files(self, message):
        if not message.strip():
            return False, "커밋 메시지를 입력해야 합니다."

        if not self.is_connected():
            return True, f"[더미 실행] 커밋 완료: {message}"

        return self.run_git(["git", "commit", "-m", message])

    def push_to_github(self):
        if not self.is_connected():
            return True, "[더미 실행] GitHub에 Push 되었습니다."

        return self.run_git(["git", "push"])

    def get_history(self):
        if not self.is_connected():
            return self.get_dummy_history()

        success, output = self.run_git(
            ["git", "log", "--oneline", "--decorate", "--graph", "-10"]
        )

        if success and output:
            return output

        return "커밋 히스토리가 없습니다."

    def get_dummy_changed_files(self):
        return [
            {"filename": "pvcs.py", "status": "M", "changed": True},
            {"filename": "README.md", "status": "M", "changed": True},
            {"filename": ".pvcsconfig", "status": "A", "changed": True},
            {"filename": ".pvcsignore", "status": "", "changed": False},
            {"filename": "LICENSE", "status": "", "changed": False},
        ]

    def get_dummy_diff(self, filename):
        return f"""
파일명: {filename}

- 이전 내용:
    print("old version")

+ 변경 내용:
    print("new version")

설명:
이 영역은 선택한 파일의 세부 변경 사항을 확인하는 공간입니다.
현재 Git 저장소가 연결되지 않았기 때문에 더미 데이터가 표시됩니다.

실제 GitHub 저장소를 선택하면,
git diff 결과가 이 영역에 표시됩니다.
"""

    def get_dummy_history(self):
        return """
* a1b2c3d UI 기본 레이아웃 구성
* b2c3d4e 파일 변경 여부 표시 기능 추가
* c3d4e5f ADD / Commit 메소드 구조 작성
* d4e5f6g GitHub Push 기능 연결 준비
"""


class GitHubManagerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.git_adapter = GitHubMethodAdapter()
        self.selected_file = None

        self.title("GitHub 파일 변경 관리 프로그램")
        self.geometry("1250x760")
        self.minsize(1050, 680)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_ui()
        self.refresh_files()

    def create_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, height=78, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="GitHub File Review Manager",
            font=("Arial", 26, "bold")
        )
        self.title_label.grid(row=0, column=0, padx=24, pady=22, sticky="w")

        self.repo_path_label = ctk.CTkLabel(
            self.header_frame,
            text="연결된 GitHub 프로젝트 없음",
            font=("Arial", 13),
            text_color="#AFAFAF"
        )
        self.repo_path_label.grid(row=0, column=1, padx=10, pady=22, sticky="w")

        self.connect_btn = ctk.CTkButton(
            self.header_frame,
            text="프로젝트 디렉토리 연결",
            width=180,
            height=38,
            command=self.connect_repository
        )
        self.connect_btn.grid(row=0, column=2, padx=22, pady=20)

        self.left_panel = ctk.CTkFrame(self, width=310, corner_radius=18)
        self.left_panel.grid(row=1, column=0, padx=22, pady=22, sticky="nsew")
        self.left_panel.grid_rowconfigure(2, weight=1)

        self.file_list_title = ctk.CTkLabel(
            self.left_panel,
            text="파일 목록",
            font=("Arial", 22, "bold")
        )
        self.file_list_title.grid(row=0, column=0, padx=20, pady=(22, 4), sticky="w")

        self.file_list_subtitle = ctk.CTkLabel(
            self.left_panel,
            text="변경된 파일은 ✅ 로 표시됩니다.",
            font=("Arial", 13),
            text_color="#AFAFAF"
        )
        self.file_list_subtitle.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        self.file_scroll_frame = ctk.CTkScrollableFrame(
            self.left_panel,
            width=260,
            corner_radius=14
        )
        self.file_scroll_frame.grid(row=2, column=0, padx=18, pady=8, sticky="nsew")

        self.left_button_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color="transparent"
        )
        self.left_button_frame.grid(row=3, column=0, padx=18, pady=18, sticky="ew")

        self.add_btn = ctk.CTkButton(
            self.left_button_frame,
            text="ADD",
            height=40,
            command=self.add_selected_file
        )
        self.add_btn.pack(fill="x", pady=5)

        self.refresh_btn = ctk.CTkButton(
            self.left_button_frame,
            text="Refresh",
            height=40,
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            command=self.refresh_files
        )
        self.refresh_btn.pack(fill="x", pady=5)

        self.main_panel = ctk.CTkFrame(self, corner_radius=18)
        self.main_panel.grid(row=1, column=1, padx=(0, 22), pady=22, sticky="nsew")
        self.main_panel.grid_columnconfigure(0, weight=1)
        self.main_panel.grid_rowconfigure(2, weight=1)

        self.review_title = ctk.CTkLabel(
            self.main_panel,
            text="파일 리뷰 / 변경 내용 확인",
            font=("Arial", 23, "bold")
        )
        self.review_title.grid(row=0, column=0, padx=26, pady=(24, 6), sticky="w")

        self.selected_file_label = ctk.CTkLabel(
            self.main_panel,
            text="왼쪽에서 파일을 선택하면 세부 변경 내용이 표시됩니다.",
            font=("Arial", 14),
            text_color="#AFAFAF"
        )
        self.selected_file_label.grid(row=1, column=0, padx=26, pady=(0, 12), sticky="w")

        self.diff_textbox = ctk.CTkTextbox(
            self.main_panel,
            font=("Consolas", 14),
            corner_radius=14,
            wrap="none"
        )
        self.diff_textbox.grid(row=2, column=0, padx=26, pady=10, sticky="nsew")
        self.set_diff_text("파일을 선택하세요.\n\n선택한 파일의 변경 내용이 이곳에 표시됩니다.")

        self.bottom_panel = ctk.CTkFrame(self.main_panel, corner_radius=14)
        self.bottom_panel.grid(row=3, column=0, padx=26, pady=22, sticky="ew")
        self.bottom_panel.grid_columnconfigure(0, weight=1)

        self.commit_entry = ctk.CTkEntry(
            self.bottom_panel,
            placeholder_text="커밋 메시지를 입력하세요. 예: Update UI layout",
            height=42,
            font=("Arial", 14)
        )
        self.commit_entry.grid(row=0, column=0, padx=14, pady=14, sticky="ew")

        self.commit_btn = ctk.CTkButton(
            self.bottom_panel,
            text="Commit",
            width=115,
            height=42,
            command=self.commit_changes
        )
        self.commit_btn.grid(row=0, column=1, padx=8, pady=14)

        self.push_btn = ctk.CTkButton(
            self.bottom_panel,
            text="Push",
            width=115,
            height=42,
            fg_color="#2E8B57",
            hover_color="#246B45",
            command=self.push_changes
        )
        self.push_btn.grid(row=0, column=2, padx=8, pady=14)

        self.history_btn = ctk.CTkButton(
            self.bottom_panel,
            text="History",
            width=115,
            height=42,
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            command=self.open_history_window
        )
        self.history_btn.grid(row=0, column=3, padx=14, pady=14)

    def connect_repository(self):
        path = filedialog.askdirectory(title="GitHub 프로젝트 폴더를 선택하세요")

        if not path:
            return

        self.git_adapter.connect_repository(path)
        self.repo_path_label.configure(text=path)

        if not self.git_adapter.is_connected():
            messagebox.showwarning(
                "Git 저장소 확인",
                "선택한 폴더 안에서 .git 폴더를 찾지 못했습니다.\n"
                "현재는 더미 데이터로 UI가 표시됩니다."
            )

        self.refresh_files()

    def refresh_files(self):
        for widget in self.file_scroll_frame.winfo_children():
            widget.destroy()

        files = self.git_adapter.get_changed_files()

        if not files:
            empty_label = ctk.CTkLabel(
                self.file_scroll_frame,
                text="변경된 파일이 없습니다.",
                font=("Arial", 14),
                text_color="#AFAFAF"
            )
            empty_label.pack(padx=12, pady=30)
            return

        for file_info in files:
            self.create_file_item(file_info)

    def create_file_item(self, file_info):
        filename = file_info.get("filename", "unknown")
        status = file_info.get("status", "")
        changed = file_info.get("changed", False)

        check_icon = "✅" if changed else "⬜"
        status_text = self.convert_status_text(status)

        button_text = f"{check_icon}  {filename}\n   {status_text}"

        file_button = ctk.CTkButton(
            self.file_scroll_frame,
            text=button_text,
            height=68,
            anchor="w",
            fg_color="#242A32",
            hover_color="#313945",
            font=("Arial", 13),
            command=lambda name=filename: self.select_file(name)
        )
        file_button.pack(fill="x", padx=8, pady=6)

    def convert_status_text(self, status):
        status_map = {
            "M": "수정됨",
            "A": "추가됨",
            "D": "삭제됨",
            "R": "이름 변경",
            "C": "복사됨",
            "??": "새 파일",
            "": "변경 없음"
        }

        return status_map.get(status, status if status else "변경 없음")

    def select_file(self, filename):
        self.selected_file = filename
        self.selected_file_label.configure(text=f"선택된 파일: {filename}")

        diff = self.git_adapter.get_file_diff(filename)
        self.set_diff_text(diff)

    def set_diff_text(self, text):
        self.diff_textbox.configure(state="normal")
        self.diff_textbox.delete("1.0", "end")
        self.diff_textbox.insert("1.0", text)
        self.diff_textbox.configure(state="disabled")

    def add_selected_file(self):
        if not self.selected_file:
            messagebox.showinfo("알림", "먼저 파일을 선택하세요.")
            return

        success, result = self.git_adapter.add_file(self.selected_file)

        if success:
            messagebox.showinfo(
                "ADD 완료",
                result if result else f"{self.selected_file} 파일이 ADD 되었습니다."
            )
            self.refresh_files()
        else:
            messagebox.showerror("ADD 실패", result)

    def commit_changes(self):
        message = self.commit_entry.get()

        success, result = self.git_adapter.commit_files(message)

        if success:
            messagebox.showinfo(
                "Commit 완료",
                result if result else "커밋이 완료되었습니다."
            )
            self.commit_entry.delete(0, "end")
            self.refresh_files()
        else:
            messagebox.showerror("Commit 실패", result)

    def push_changes(self):
        success, result = self.git_adapter.push_to_github()

        if success:
            messagebox.showinfo(
                "Push 완료",
                result if result else "GitHub에 업로드되었습니다."
            )
        else:
            messagebox.showerror("Push 실패", result)

    def open_history_window(self):
        history_window = ctk.CTkToplevel(self)
        history_window.title("Commit History")
        history_window.geometry("760x520")
        history_window.grab_set()

        title = ctk.CTkLabel(
            history_window,
            text="최근 커밋 히스토리",
            font=("Arial", 23, "bold")
        )
        title.pack(padx=24, pady=(24, 10), anchor="w")

        subtitle = ctk.CTkLabel(
            history_window,
            text="현재 프로젝트의 최근 커밋 내역을 확인합니다.",
            font=("Arial", 14),
            text_color="#AFAFAF"
        )
        subtitle.pack(padx=24, pady=(0, 12), anchor="w")

        history_box = ctk.CTkTextbox(
            history_window,
            font=("Consolas", 14),
            corner_radius=14
        )
        history_box.pack(fill="both", expand=True, padx=24, pady=20)

        history = self.git_adapter.get_history()
        history_box.insert("1.0", history)
        history_box.configure(state="disabled")


if __name__ == "__main__":
    app = GitHubManagerUI()
    app.mainloop()
