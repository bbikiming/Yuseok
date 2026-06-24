"""신호 시점 데이터 → feature 벡터.

누수 금지: 신호 발생 시점까지의 정보만 사용한다. 미래 봉/청산 결과를 넣지 않는다.
결측은 NaN + mask 로 표현(0 으로 채우지 않는다).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import FEATURE_VERSION


@dataclass
class FeatureBundle:
    version: str
    values: dict[str, float]   # feature 이름 → 값 (NaN 허용)

    def to_json(self) -> dict[str, Any]:
        return {"version": self.version, "values": self.values}


def build_features(
    *,
    candles_1m: list[dict],
    candles_3m: list[dict],
    candles_5m: list[dict],
    orderbook: dict,
    trades: list[dict],
    now_price: dict,
    context: dict | None = None,
) -> FeatureBundle:
    """탐지 시점의 원천 데이터로 feature 를 생성한다 (PRD §11.4 그룹).

    그룹: 가격 수익률 / 최근 최대 하락률 / 저점 대비 반등률 / 캔들 형태 /
    이동평균 위치 / 거래량 배율 / 호가 스프레드·잔량비 / 체결강도 근사 /
    장 경과시간·점심 / 종목 변동성 / 리스크 상태.

    TODO(Phase 4): 각 그룹 계산 구현. 반드시 FEATURE_VERSION 동봉.
    """
    raise NotImplementedError("Phase 4: feature 계산 구현 예정")
