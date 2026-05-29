# Python version control system
A proof-of-concept version control system for a school project.

##디자인
실행 디렉토리에 폴더 .pvcshist와 평문 파일 .pvcsconfig, .pvcsignore를 생성한다.
pvcshist 폴더 내에는 각 코밋 시의 프로젝트를 통째로 복사하여 저장한다(닷파일 제외)
pvcsconfig에는 추적할 파일의 전체 경로를 저장한다.
pvcsignore에는 변화를 무시할 파일의 경로를 저장한다.
