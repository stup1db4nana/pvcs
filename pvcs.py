import os
import datetime
import shutil


# 추가해야 할 사항: 파일 변경점 검사, 히스트에서 파일 되돌리기

class Pvcs:
    # 디렉토리 위치 설정.
    def __init__(self):
        self.HISTDIR = ".pvcshist"  # 옛 코밋 저장하는 위치
        self.CONFIGDIR = ".pvcsconfig"  # 추적하는 파일
        self.IGNOREDIR = ".pvcsignore"  # 무시할 파일

    # filepath를 받아 그 위치에 디렉토리 생성 .
    @staticmethod
    def create_dirs(filepath):
        if not os.path.exists(filepath):
            print("debuginfo: createdir ", filepath)
            os.makedirs(filepath)

    # filepath를 받아 그 위치에 파일 생성.
    @staticmethod
    def create_file(filepath):
        if not os.path.exists(filepath):
            print("debuginfo: createfile ", filepath)
            file = open(filepath, "w")
            file.close()

    # filepath에서 compvalue가 있는지 검사. 모드가 1일 경우 완전 일치, 0일 경우 시작하는 줄에 포함되는지 검사.
    @staticmethod
    def check_line_from_file(filepath, target, mode=1):
        if not os.path.exists(filepath):
            return False

        with open(filepath, "r") as file:
            normal_target = os.path.normpath(target.strip())
            for line in file:
                if not line.strip() or line.startswith("#"):
                    continue
                normal_line = os.path.normpath(line.strip())
                if mode == 1:
                    if normal_target == normal_line:
                        return True
                else:
                    if normal_target.startswith(normal_line):
                        return True
        return False

    # filepath에 new_line 추가.
    @staticmethod
    def add_line_into_file(filepath, new_line):
        if not os.path.exists(filepath):
            print("debuginfo: addfilefailure")
            return False
        with open(filepath, "a") as file:
            print("debuginfo: addfile ", filepath, new_line)
            file.write("\n" + new_line)
            return None

    # 파일이 추적중인 경우 참, 아니면 거짓.
    def check_tracking_status(self, filepath):
        normal_target = os.path.normpath(filepath)
        return self.check_line_from_file(self.CONFIGDIR, normal_target)

    # 파일이 무시된 경우 참, 아니면 거짓. mode가 1인 경우 완전 일치, 0일 경우 시작줄에 포함되는지 검사.
    def check_ignore_status(self, filepath, mode):
        normal_target = os.path.normpath(filepath)
        return self.check_line_from_file(self.IGNOREDIR, normal_target, mode)

    # 무시된 파일을 제외하고 워킹 디렉토리를 탐색.
    def scan_pwd(self, pwd="."):
        scanned_files = []

        for path, subdir, file in os.walk(pwd):
            subdir[:] = [d for d in subdir if d != self.HISTDIR]

            for i in file:
                combined_path = os.path.normpath(os.path.join(path, i))

                if not self.check_ignore_status(i, 1) and not self.check_ignore_status(path, 0):
                    print("debuginfo: scan ", combined_path)
                    scanned_files.append(combined_path)

        return scanned_files

    # 추적 중인 파일만을 탐색
    def get_tracked_files(self, pwd="."):
        scanned_files = []

        for path, subdir, file in os.walk(pwd):
            subdir[:] = [d for d in subdir if d != self.HISTDIR]

            for i in file:
                combined_path = os.path.normpath(os.path.join(path, i))

                if self.check_tracking_status(combined_path):
                    print("debuginfo: scan ", combined_path)
                    scanned_files.append(combined_path)

        return scanned_files

    # 작업중
    def check_for_changes(self):
        if not os.path.exists(self.HISTDIR) or not os.listdir(self.HISTDIR):
            return False

        sorted_commit_list = sorted(os.listdir(self.HISTDIR))
        latest_commit = os.path.join(self.HISTDIR, sorted_commit_list[-1])
        return False

    # 추적중인 파일을 iso날자로 구분해 hist에 디렉토리 째로 저장.
    def commit(self):
        foldername = datetime.datetime.now(datetime.timezone.utc).isoformat()
        foldername = foldername.replace(":", "-")
        foldername = foldername.replace(".", "-")

        commit_path = os.path.join(self.HISTDIR, foldername)
        commit_files = self.get_tracked_files()
        print("debuginfo: commit ", commit_path, commit_files)

        if not commit_files:
            return False

        for i in commit_files:
            hist_path = os.path.join(commit_path, i)
            self.create_dirs(os.path.dirname(hist_path))

            shutil.copy2(i, hist_path)
            print("debuginfo: copy ", i, hist_path)
        print("debuginfo: commit complete")
        return True

    def checkout(self, commit_id):
        target_path = os.path.join(self.HISTDIR, commit_id)
        if not os.path.exists(target_path):
            print("debuginfo: checkout failed! ", commit_id, " does not exist")
            return False
        for path, subdir, files in os.walk(target_path):
            for i in files:
                target_file = os.path.join(path, i)
                rel_path = os.path.relpath(target_file, target_path)
                print("debuginfo: checkout", target_file, rel_path)
                self.create_dirs(rel_path)

                shutil.copy2(target_file, rel_path)
                print("debuginfo: copy ", target_file, rel_path)

        print("debuginfo: checkout complete")
        return True


if __name__ == "__main__":
    vcs = Pvcs()
    vcs.create_dirs(vcs.HISTDIR)
    vcs.create_file(vcs.CONFIGDIR)
    vcs.create_file(vcs.IGNOREDIR)

    vcs.get_tracked_files()

    # vcs.commit()
    # vcs.checkout("2026-06-01T07-02-29-383304+00-00")
