"""검증 지표 + 승격 게이트.

핵심 지표는 승률이 아니라 '비용 반영 기대값'과 '확률 보정(calibration)'.
승률 기준은 두지 않는다: 손익분기 승률은 비용과 익절/손절 폭에 따라 40~90% 로 달라지므로
(docs/PROFIT_PLAN.md §2) 고정 승률 게이트는 손실 전략을 통과시킬 수 있다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    n_train: int
    n_entry: int
    win_rate: float
    expected_value: float     # 비용(수수료·세금·슬리피지) 반영, 거래당 평균 순수익률
    ev_ci_low: float          # expected_value 의 부트스트랩 신뢰구간 하한
    avg_win: float
    avg_loss: float
    profit_loss_ratio: float
    max_consec_loss: int
    max_drawdown: float
    calibration_ece: float    # Expected Calibration Error


# 승격 게이트 기준 (LEARNING_SYSTEM.md §6, PRD §11.7/§18.3)
GATE = {
    "min_train": 100,
    "min_entry": 50,
    "max_consec_loss": 5,
    "max_drawdown": 0.05,      # 설정값으로 외부화 권장
    "max_ece": 0.1,
}


def evaluate(validation_results) -> Metrics:
    """워크포워드 검증 결과 집계 → Metrics.

    TODO(Phase 4): 비용 반영 손익/보정오차/낙폭 계산.
    """
    raise NotImplementedError("Phase 4")


def passes_gate(m: Metrics, active: Metrics | None = None) -> tuple[bool, list[str]]:
    """게이트 통과 여부와 실패 사유 목록 반환.

    active 가 주어지면 '퇴보 방지'(신규 기대값 ≥ active 기대값)도 검사.
    """
    reasons: list[str] = []
    if m.n_train < GATE["min_train"]:
        reasons.append(f"학습 신호 부족({m.n_train}<{GATE['min_train']})")
    if m.n_entry < GATE["min_entry"]:
        reasons.append(f"진입 부족({m.n_entry}<{GATE['min_entry']})")
    if m.expected_value <= 0:
        reasons.append(f"비용 반영 기대값 음수({m.expected_value:+.4%})")
    elif m.ev_ci_low <= 0:
        reasons.append(f"기대값 신뢰구간 하한이 0 이하({m.ev_ci_low:+.4%})")
    if m.max_consec_loss > GATE["max_consec_loss"]:
        reasons.append(f"연속손실 초과({m.max_consec_loss})")
    if m.max_drawdown > GATE["max_drawdown"]:
        reasons.append(f"최대낙폭 초과({m.max_drawdown:.2%})")
    if m.calibration_ece > GATE["max_ece"]:
        reasons.append(f"보정오차 초과(ECE={m.calibration_ece:.3f})")
    if active is not None and m.expected_value < active.expected_value:
        reasons.append("기존 active 대비 기대값 퇴보")
    return (not reasons), reasons
