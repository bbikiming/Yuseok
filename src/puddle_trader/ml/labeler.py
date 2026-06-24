"""매매 결과 → 학습 라벨.

기본 학습 질문: 진입 후 max_hold 안에 TP가 SL보다 먼저 도달했는가? (이진)
"""
from __future__ import annotations

# 결과 라벨 → 이진 타깃 매핑 (LEARNING_SYSTEM.md §3)
LABEL_TO_TARGET: dict[str, int | None] = {
    "WIN": 1,
    "WEAK_WIN": 1,
    "LOSS": 0,
    "TIMEOUT": 0,
    "INVALID": None,   # 학습 제외
}


def to_target(result: str) -> int | None:
    """paper_trades.result 문자열을 학습 타깃(1/0/None)으로 변환."""
    return LABEL_TO_TARGET.get(result)


def is_trainable(result: str) -> bool:
    return to_target(result) is not None
