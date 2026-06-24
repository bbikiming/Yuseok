#!/usr/bin/env bash
# 메인 PC 로컬 개발 부트스트랩. 저장소 루트에서 실행: bash scripts/bootstrap.sh
set -euo pipefail

cd "$(dirname "$0")/.."

PY=${PYTHON:-python3}
echo "==> Python: $($PY --version)"

if [ ! -d .venv ]; then
  echo "==> venv 생성"
  $PY -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> 의존성 설치 (.[ml,dev])"
pip install -U pip >/dev/null
pip install -e ".[ml,dev]"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> .env 생성됨 — TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 를 채우세요."
fi

echo "==> 초기화 (디렉토리 + DB)"
tradebot init

echo "==> 테스트"
pytest -q

cat <<'EOF'

✅ 부트스트랩 완료.
다음:
  1) .env 에 토스 API 키 입력
  2) source .venv/bin/activate
  3) tradebot auth test     # 토큰/계좌 확인
  4) docs/IMPLEMENTATION_PLAN.md Phase 1 부터 구현 시작
EOF
