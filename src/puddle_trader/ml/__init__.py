"""학습 루프 모듈 (LEARNING_SYSTEM.md).

수집/탐지 결과를 학습 데이터로 축적하고, 모델을 학습·검증·승격하며,
다음 매매의 성공 확률 추정(점수화)에 사용한다.

각 모듈은 인터페이스(시그니처+docstring) 골격이며 구현은 IMPLEMENTATION_PLAN Phase 4 참고.
AI 는 점수화만 담당하고 주문 권한은 갖지 않는다(DECISIONS D2).
"""

FEATURE_VERSION = "v1"
"""feature 스키마 버전. features_json 구조가 바뀌면 올린다(혼합 학습 방지)."""
