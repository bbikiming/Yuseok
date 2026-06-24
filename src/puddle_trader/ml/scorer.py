"""추론: 신호 → 성공확률(win_prob).

장중에는 active 모델을 고정해 사용한다(즉시 재학습 반영 금지, PRD NG6).
콜드 스타트(데이터 부족) 시 모델 없이 룰 점수만 사용.
"""
from __future__ import annotations

from dataclasses import dataclass

from .features import FeatureBundle


@dataclass
class Prediction:
    win_prob: float
    threshold: float
    accepted: bool
    model_version: str | None   # None 이면 모델 미사용(룰 only)


class PredictionScorer:
    def __init__(self, model_version: str | None, threshold: float):
        self._version = model_version
        self._threshold = threshold
        # TODO(Phase 4): models/{version}/ 에서 모델+보정기 로드

    @classmethod
    def load_active(cls, conn, threshold: float) -> "PredictionScorer":
        """model_registry 에서 status='active' 모델을 로드. 없으면 모델 없이 동작."""
        raise NotImplementedError("Phase 4: active 모델 로딩 구현 예정")

    def score(self, features: FeatureBundle) -> Prediction:
        """feature → 보정된 win_prob 및 임계 통과 여부.

        모델이 없으면 win_prob=NaN, accepted=True(룰 판단에 위임).
        TODO(Phase 4): 예측 + 보정 적용.
        """
        raise NotImplementedError("Phase 4: 추론 구현 예정")
