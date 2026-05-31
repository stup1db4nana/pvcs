import os
import datetime
import shutil


# 추가해야 할 사항: 코밋, 파일 복사, 디렉토리 복사(파일복사와 함계 코밋시 파일 저장), 파일 변경점 검사, 히스트에서 파일 되돌리기

class Pvcs:
    # 디렉토리 위치 설정
    def __init__(self):
        self.HISTDIR = ".pvcshist"  # 옛 코밋 저장하는 위치
        self.CONFIGDIR = ".pvcsconfig"  # 추적하는 파일
        self.IGNOREDIR = ".pvcsignore"  # 무시할 파일

    # 디렉토리 생성
    @staticmethod
    def create_dirs(filepath):
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    # 파일 생성
    @staticmethod
    def create_file(filepath):
        if not os.path.exists(filepath):
            file = open(filepath, "w")
            file.close()

    # filepath 파일에서 compvalue를 검색 모드가 1일 경우 완전 일치, 0일 경우 시작하는 줄에 포함
    @staticmethod
    def check_line_from_file(filepath, target, mode=1):
        if not os.path.exists(filepath):
            return False

        with open(filepath, "r") as file:
            # 경로 노말라이즈
            normal_target = os.path.normpath(target.strip())
            for line in file:
                # 공백 샵 무시
                if not line.strip() or line.startswith("#"):
                    continue
                # 경로 노말라이즈
                normal_line = os.path.normpath(line.strip())
                if mode == 1:
                    if normal_target == normal_line:
                        return True
                else:
                    if normal_target.startswith(normal_line):
                        return True
        return False

    # filepath에 new_line 추가
    @staticmethod
    def add_line_into_file(filepath, new_line):
        if not os.path.exists(filepath):
            return False
        with open(filepath, "a") as file:
            file.write("\n" + new_line)
            return None

    # 파일이 추적중인 경우 참, 아니면 거짓
    def check_tracking_status(self, filepath):
        normal_target = os.path.normpath(filepath)
        return self.check_line_from_file(self.CONFIGDIR, normal_target)

    # 파일이 무시된 경우 참, 아니면 거짓
    def check_ignore_status(self, filepath, mode):
        normal_target = os.path.normpath(filepath)
        return self.check_line_from_file(self.IGNOREDIR, normal_target, mode)

    # 무시된 파일 제외 디렉토리 검사
    def scan_pwd(self, pwd="."):
        scanned_files = []

        for path, subdir, file in os.walk(pwd):
            subdir[:] = [d for d in subdir if d != self.HISTDIR]

            for i in file:
                combined_path = os.path.normpath(os.path.join(path, i))

                if not self.check_ignore_status(i, 1) and not self.check_ignore_status(path, 0):
                    scanned_files.append(combined_path)

        return scanned_files

    # 작업중
    def check_for_changes(self):
        return False

    #
    def commit(self):
        foldername = datetime.datetime.now(datetime.timezone.utc).isoformat()
        foldername = foldername.replace(":", "-")
        foldername = foldername.replace(".", "-")

        commit_path = os.path.join(self.HISTDIR, foldername)
        commit_files = self.scan_pwd()
        print(commit_path, commit_files)

        if not commit_files:
            return False

        for i in commit_files:
            hist_path = os.path.join(commit_path, i)
            self.create_dirs(os.path.dirname(hist_path))

            shutil.copy2(i, hist_path)
        return True


if __name__ == "__main__":
    vcs = Pvcs()
    vcs.create_dirs(vcs.HISTDIR)
    vcs.create_file(vcs.CONFIGDIR)
    vcs.create_file(vcs.IGNOREDIR)

    vcs.commit()
