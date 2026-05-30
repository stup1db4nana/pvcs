import os

# 추가해야 할 사항 파일 복사, 디렉토리 복사(파일복사와 함계 코밋시 파일 저장), 파일 변경점 검사, 히스트에서 파일 되돌리기

class Pvcs:
    # 디렉토리 위치 설정
    def __init__(self):
        self.HISTDIR = ".pvcshist"  # 옛 코밋 저장하는 위치
        self.CONFIGDIR = ".pvcsconfig"  # 추적하는 파일
        self.IGNOREDIR = ".pvcsignore"  # 무시할 파일

    # 디렉토리 생성
    @staticmethod
    def createdirs(filepath):
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    # 파일 생성
    @staticmethod
    def createfile(filepath):
        if not os.path.exists(filepath):
            file = open(filepath, "w")
            file.close()

    # filepath 파일에서 compvalue를 검색
    @staticmethod
    def check_line_from_file(filepath, target):
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
            if normal_target == normal_line:
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

if __name__ == "__main__":
    vcs = Pvcs()
    vcs.createdirs(vcs.HISTDIR)
    vcs.createfile(vcs.CONFIGDIR)
    vcs.createfile(vcs.IGNOREDIR)
    vcs.add_line_into_file(vcs.CONFIGDIR, ".hello")