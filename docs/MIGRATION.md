# 메인 PC로 이전 & 로컬 개발 시작

현재 코드는 `bbikiming/Yuseok` 의 `claude/gifted-shannon-apiak5` 브랜치에 있고,
앞으로 개발은 `bbikiming/stock-auto-trader` 에서 진행한다. 한 번만 옮기면 된다.

## A. Yuseok → stock-auto-trader 로 전체 이전 (1회)

```bash
# 1) 최신 코드가 있는 Yuseok 브랜치 확보
cd ~/Yuseok
git fetch origin
git checkout claude/gifted-shannon-apiak5
git pull

# 2) stock-auto-trader 로 전체 복사 (.git 제외)
rsync -av --exclude '.git' --exclude '.venv' --exclude 'data' \
      --exclude '__pycache__' --exclude '.pytest_cache' \
      ~/Yuseok/ ~/stock-auto-trader/

# 3) 커밋 & 푸시
cd ~/stock-auto-trader
git add -A
git commit -m "전체 동기화: 스켈레톤+문서+학습 루프 골격"
git push
```

> `rsync` 가 없으면(Windows 등) `cp -r` 사용:
> `cp -r ~/Yuseok/src ~/Yuseok/config ~/Yuseok/docs ~/Yuseok/tests ~/Yuseok/scripts ~/Yuseok/.github ~/stock-auto-trader/`
> 그리고 루트 파일들(`README.md pyproject.toml requirements.txt Makefile .editorconfig .gitignore .env.example CONTRIBUTING.md`)도 복사.

## B. 로컬 개발 환경 부트스트랩

```bash
cd ~/stock-auto-trader
bash scripts/bootstrap.sh      # venv + 설치 + init + test
# 또는: make setup && make init && make test
```

## C. 키 설정 & 연결 확인

```bash
# .env 편집 → TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 입력
source .venv/bin/activate
tradebot auth test             # [STATUS] Ready 나오면 성공
```

## D. 구현 시작

```bash
git checkout -b feat/phase1-collectors
# docs/IMPLEMENTATION_PLAN.md Phase 1 부터
make test    # 자주 돌리기
```

## 이후 정리
- Yuseok 저장소/PR #1 은 더 쓰지 않으면 닫아도 됨(중복).
- 앞으로 모든 작업은 stock-auto-trader 에서.
