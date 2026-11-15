"""학습 데이터셋 빌드: signals + paper_trades → training_examples.

누수 방지 불변식:
- example.detected_at(=feature 시각) < example.resolved_at(=청산 시각)
- feature_version 이 섞이지 않도록 단일 버전으로 필터링.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class Example:
    signal_id: str
    feature_version: str
    features: dict[str, float]
    label: int
    label_source: str
    detected_at: str
    resolved_at: str


def build(conn: sqlite3.Connection, feature_version: str) -> int:
    """signals ⨝ paper_trades 로 training_examples 를 재구성한다.

    - 라벨 가능한(청산 완료 + INVALID 아님) 신호만 포함.
    - 시간 정합(detected_at < resolved_at) 위반은 제외하고 카운트.
    - 반환: 적재된 example 수.

    TODO(Phase 4): JOIN/검증/INSERT 구현.
    """
    raise NotImplementedError("Phase 4: 데이터셋 빌드 구현 예정")


def load_walk_forward_splits(
    conn: sqlite3.Connection, feature_version: str
) -> list[tuple[list[Example], list[Example]]]:
    """시간순 워크포워드 분할 리스트((train, validate), ...) 반환.

    무작위 분할 금지(시계열 누수). LEARNING_SYSTEM.md §5.
    TODO(Phase 4): 날짜 경계로 분할 구현.
    """
    raise NotImplementedError("Phase 4: 워크포워드 분할 구현 예정")
