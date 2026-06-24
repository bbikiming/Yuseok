from puddle_trader.db import init_db
from puddle_trader.db.database import connect
from puddle_trader.ml.evaluation import Metrics, passes_gate
from puddle_trader.ml.labeler import is_trainable, to_target


def test_learning_tables_created(tmp_path):
    db = tmp_path / "t.sqlite"
    init_db(db)
    conn = connect(db)
    tables = {r[0] for r in conn.execute("select name from sqlite_master where type='table'")}
    assert {"training_examples", "model_registry", "training_runs", "metrics_daily"} <= tables


def test_label_mapping():
    assert to_target("WIN") == 1
    assert to_target("WEAK_WIN") == 1
    assert to_target("LOSS") == 0
    assert to_target("TIMEOUT") == 0
    assert to_target("INVALID") is None
    assert is_trainable("WIN") and not is_trainable("INVALID")


def _metrics(**kw):
    base = dict(
        n_train=120, n_entry=60, win_rate=0.58, expected_value=0.004,
        avg_win=0.007, avg_loss=-0.005, profit_loss_ratio=1.2,
        max_consec_loss=3, max_drawdown=0.02, calibration_ece=0.05,
    )
    base.update(kw)
    return Metrics(**base)


def test_gate_passes_when_good():
    ok, reasons = passes_gate(_metrics())
    assert ok and reasons == []


def test_gate_blocks_low_winrate_and_regression():
    ok, reasons = passes_gate(_metrics(win_rate=0.40))
    assert not ok and any("승률" in r for r in reasons)

    active = _metrics(expected_value=0.006)
    ok2, reasons2 = passes_gate(_metrics(expected_value=0.003), active=active)
    assert not ok2 and any("퇴보" in r for r in reasons2)
