"""드리프트 감지 + 자동 보호.

성능/입력 분포가 학습 시점과 멀어지면 과거 학습이 손실로 이어질 수 있다.
감지 시 auto mode 자동 비활성화(R13)와 재학습 트리거를 권고한다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftReport:
    perf_drift: float       # 최근 실현 성능 vs 검증 기대값 편차
    feature_psi: float      # 입력 분포 변화(Population Stability Index)
    data_missing_rate: float
    auto_should_disable: bool
    reasons: list[str]


def assess(
    *,
    recent_expected_value: float,
    validated_expected_value: float,
    feature_psi: float,
    data_missing_rate: float,
    perf_drop_threshold: float = 0.5,   # 검증 기대값의 50% 미만으로 급락 시
    psi_threshold: float = 0.25,
    missing_threshold: float = 0.05,
) -> DriftReport:
    """드리프트 지표로 보호 발동 여부 판정.

    TODO(Phase 4): 입력 검증/임계 비교. 발동 시 로그 + metrics_daily 기록.
    """
    reasons: list[str] = []
    perf_drift = (
        (validated_expected_value - recent_expected_value) / validated_expected_value
        if validated_expected_value
        else 0.0
    )
    if recent_expected_value < validated_expected_value * perf_drop_threshold:
        reasons.append("최근 성능 급락")
    if feature_psi > psi_threshold:
        reasons.append(f"feature 분포 변화(PSI={feature_psi:.2f})")
    if data_missing_rate > missing_threshold:
        reasons.append(f"데이터 누락률 상승({data_missing_rate:.2%})")
    return DriftReport(
        perf_drift=perf_drift,
        feature_psi=feature_psi,
        data_missing_rate=data_missing_rate,
        auto_should_disable=bool(reasons),
        reasons=reasons,
    )
