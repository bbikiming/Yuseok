# 개발 컨벤션

혼자 개발하더라도 일관성을 위해 유지할 규칙.

## 브랜치 & 커밋
- `main` 직접 푸시 지양. 기능별 브랜치(`feat/puddle-detector`, `fix/...`).
- 커밋 메시지: 한글 가능, 한 줄 요약 + 필요 시 본문. 무엇을/왜.
- 한 PR = 한 관심사 (IMPLEMENTATION_PLAN 의 한 항목 단위 권장).

## 코드 스타일
- Python 3.10+, 타입힌트 사용. `from __future__ import annotations`.
- 포매터/린터: `ruff`. 커밋 전 `ruff check . && pytest -q`.
- 함수는 작게, 전략/청산/리스크는 **순수함수**로(부수효과는 호출측에서).
- 시크릿/계좌번호 전체를 로그·예외 메시지·리포트에 남기지 않는다.

## 디렉토리 규약
```
src/puddle_trader/
  api/        외부 API (통신만)
  strategy/   탐지·지표·청산룰 (순수 로직)
  ml/         feature/label/train/score
  trading/    paper/manual/auto, risk, position
  reports/    마크다운 생성
  db/         스키마·연결·repository
config/       *.yaml (튜닝 파라미터 외부화)
docs/         설계/가이드 문서
tests/        단위 테스트
```

## 테스트
- 새 전략/청산/리스크 로직은 테스트 동반.
- API 호출은 모킹(httpx) 또는 통합 테스트로 분리. 실계좌 주문 테스트는 금지(paper로).

## 설정 변경
- 임계·가중치 등 "튜닝 대상" 숫자는 코드 상수가 아니라 `config/*.yaml` 로.
- 안전장치 기본값(paper, allow_*_order=false)은 함부로 바꾸지 않는다.

## 의존성
- 런타임 최소화. ML 은 `[ml]` extra 로 선택 설치.
- 새 의존성 추가 시 pyproject 에 명시 + 이유를 PR 에 기록.
