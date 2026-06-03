# Python version control system

A proof-of-concept version control system for a school project.

## 설계

pwd에는 .pvcsconfig, .pvcsignore 파일과 .pvcshist 디렉토리가 생성된다.

.pvcsconfig에는 추적하고 싶은 파일의 pwd에서부터의 경로가 삽입된다.

.pvcsignore에는 무시하고 싶은 파일의 pwd에서부터의 경로가 삽입된다. 디렉토리를 무시한 경우 예하 디렉토리 또한 모두 무시된다.

.pvcshist에는 iso 표준 날자로 구분된 예하 디렉토리를 생성해, 사용자가 코밋한 경우 여기에 추적되는 파일을 완전 복사한다.

## 발표자료
https://1drv.ms/p/c/71f47a4cfba21a8b/IQCDzp72QmgZQJ1JtBi2VrhYAYmz04_QfGmg0RuV2DKf-ok?e=Z6fSeh
https://canva.link/h32mygzwzxmt3an
