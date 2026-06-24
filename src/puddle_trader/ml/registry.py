"""모델 레지스트리: 버전 관리·승격·롤백.

active 는 항상 1개. 추론은 active 만 사용. 성능 저하 시 직전 archived 로 롤백.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class ModelRecord:
    version: str
    algo: str
    feature_version: str
    path: str
    status: str            # candidate / active / archived / rejected
    metrics: dict


def get_active(conn: sqlite3.Connection) -> ModelRecord | None:
    """현재 active 모델. 없으면 None(콜드 스타트)."""
    raise NotImplementedError("Phase 4")


def list_models(conn: sqlite3.Connection) -> list[ModelRecord]:
    raise NotImplementedError("Phase 4")


def promote(conn: sqlite3.Connection, version: str) -> None:
    """version 을 active 로, 기존 active 는 archived 로 (트랜잭션).

    승격 전 gate.passes() 통과를 반드시 확인할 것.
    """
    raise NotImplementedError("Phase 4")


def rollback(conn: sqlite3.Connection, to_version: str) -> None:
    """지정 버전으로 롤백(active 교체)."""
    raise NotImplementedError("Phase 4")
