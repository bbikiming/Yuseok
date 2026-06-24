# 문서 인덱스

Puddle Trader CLI 설계·기획·구현 문서 모음.

## 기획 / 제품
- [PRD.md](PRD.md) — 제품 요구사항 정의서 (원본 기획)
- [DECISIONS.md](DECISIONS.md) — 주요 설계 결정과 근거 (ADR 요약)
- [ROADMAP.md](ROADMAP.md) — 버전별 로드맵 (v0.1~v0.5)

## 설계
- [ARCHITECTURE.md](ARCHITECTURE.md) — 계층 구조, 데이터 흐름, 모듈 매핑
- [STRATEGY.md](STRATEGY.md) — Puddle Rebound 전략 명세 (C1~C10, 청산, 라벨)
- [LEARNING_SYSTEM.md](LEARNING_SYSTEM.md) — 자기개선 학습 루프 (축적→학습→확률개선→승격)
- [DATA_MODEL.md](DATA_MODEL.md) — SQLite 스키마와 사용 규칙

## API
- [API_NOTES.md](API_NOTES.md) — 토스 OpenAPI v1.1.1 검증 결과 (PRD 대비 수정점)
- [API_REFERENCE.md](API_REFERENCE.md) — 엔드포인트 빠른 참조

## 구현/운영
- [SETUP.md](SETUP.md) — 개발 환경 설정 가이드
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) — Phase별 구현 체크리스트
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — 개발 컨벤션

## 읽는 순서 (메인 PC에서 구현 시작 시)
1. SETUP.md 로 환경 구성 + `tradebot auth test`
2. ARCHITECTURE.md 로 전체 그림 파악
3. IMPLEMENTATION_PLAN.md Phase 1 부터 착수
4. 작업 중 STRATEGY.md / API_REFERENCE.md / DATA_MODEL.md 참조
