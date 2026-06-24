.PHONY: help setup install init auth test lint fmt watch clean

help:           ## 명령 목록
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup:          ## venv 생성 + 의존성 설치(+ml,dev) + .env 준비
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -e ".[ml,dev]"
	@test -f .env || cp .env.example .env
	@echo "→ .env 에 TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 를 입력하세요."

install:        ## 의존성만 재설치
	pip install -e ".[ml,dev]"

init:           ## 디렉토리 + SQLite DB 생성
	tradebot init

auth:           ## 토큰 발급/계좌 조회 확인
	tradebot auth test

test:           ## 테스트
	pytest -q

lint:           ## 린트
	ruff check .

fmt:            ## 포맷
	ruff check --fix .

watch:          ## 장중 감시(paper)
	tradebot watch --mode paper --interval 10s

clean:          ## 캐시/빌드 산출물 정리
	rm -rf .pytest_cache .ruff_cache **/__pycache__ *.egg-info build dist
