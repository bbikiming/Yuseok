"""모델 학습 + 확률 보정.

우선순위(PRD §11.5): LogisticRegression → RandomForest → GradientBoosting.
초기에는 모델보다 feature 품질·라벨 정확도가 중요.
확률 보정(Platt/Isotonic) 필수 — win_prob 이 실제 적중률과 일치해야 임계가 의미를 가진다.
"""
from __future__ import annotations

from dataclasses import dataclass

from .dataset import Example


@dataclass
class TrainResult:
    version: str
    algo: str
    feature_version: str
    model_path: str
    calibrator_path: str
    metrics: dict[str, float]   # 워크포워드 검증 지표


def train(
    examples: list[Example],
    *,
    algo: str = "logreg",
    feature_version: str = "v1",
    target: str = "hit_tp_before_sl",
) -> TrainResult:
    """학습셋으로 모델을 학습하고 보정한 뒤 models/{version}/ 에 저장한다.

    절차:
    1. 워크포워드 분할로 학습/검증 (dataset.load_walk_forward_splits)
    2. 모델 적합 + 확률 보정기 적합
    3. 비용 반영 기대값·승률·ECE·MDD 계산 (evaluation)
    4. model_registry 에 candidate 로 등록, training_runs 기록

    TODO(Phase 4): scikit-learn 구현. 저장은 joblib.
    """
    raise NotImplementedError("Phase 4: 학습 구현 예정")
