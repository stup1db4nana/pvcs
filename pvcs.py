import os


# 파일 생성
def createfile(filepath):
    if not os.path.exists(filepath):
        file = open(filepath, "w")
        file.close()


# filepath 파일에서 compvalue가 있나 검사
def compare_from_file(filepath, target):
    # 파일이 없는 경우
    if not os.path.exists(filepath):
        return False
    # 경로 노말라이즈
    normal_target = os.path.normpath(target.strip())

    with open(filepath, "r") as file:
        for line in file:
            # 공백 샵 무시
            if not line.strip() or line.startswith("#"):
                continue
        # 경로 노말라이즈
        normal_line = os.path.normpath(line.strip())
        if normal_target == normal_line:
            return True
    return False


class Pvcs:
    # 디렉토리 위치 설정
    def __init__(self):
        self.HISTDIR = ".pvcshist"  # 옛 코밋 저장하는 위치
        self.CONFIGDIR = ".pvcsconfig"  # 추적하는 파일
        self.IGNOREDIR = ".pvcsignore"  # 무시할 파일

    # 리포 초기화
    def init_repo(self):
        if not os.path.exists(self.HISTDIR):
            os.makedirs(self.HISTDIR)
