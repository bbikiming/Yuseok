import shutil
from datetime import date, timedelta
from pathlib import Path

from helpers import day_with_outcome, to_api_candles
from typer.testing import CliRunner

from puddle_trader.cli import app
from puddle_trader.db import init_db
from puddle_trader.db import repository as repo
from puddle_trader.db.database import connect

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _seed(tmp_path, monkeypatch, n_days=40):
    monkeypatch.chdir(tmp_path)
    shutil.copytree(ROOT / "config", tmp_path / "config")
    init_db("data/tradebot.sqlite")
    conn = connect("data/tradebot.sqlite")
    # 3일에 2번 익절, 1번 손절하는 합성 데이터 (주식 1, ETF 1)
    for code, stype in (("111111", "STOCK"), ("222222", "ETF")):
        sid = repo.ensure_symbol(conn, "KR", code, code, stype)
        for k in range(n_days):
            day = date(2026, 3, 2) + timedelta(days=k)
            bars = day_with_outcome(day, "loss" if k % 3 == 0 else "win")
            repo.upsert_candles(conn, sid, "1m", to_api_candles(bars))
    conn.commit()
    return conn


def test_backtest_single_reports_per_group_and_saves(tmp_path, monkeypatch):
    conn = _seed(tmp_path, monkeypatch)
    res = runner.invoke(app, ["backtest"])
    assert res.exit_code == 0, res.output
    assert "[STOCK]" in res.output and "[ETF]" in res.output
    assert "거래 40회" in res.output and "기대값" in res.output
    assert conn.execute("select count(*) from backtest_runs").fetchone()[0] == 2
    assert conn.execute("select count(*) from backtest_trades").fetchone()[0] == 80
    # 같은 가격 경로라도 ETF 가 비용이 낮아 순수익률이 높다
    rows = dict(conn.execute(
        "select symbol_id, avg(net_rate) from backtest_trades group by symbol_id"))
    assert rows["KR:222222"] > rows["KR:111111"]


def test_backtest_grid_evaluates_out_of_sample(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch, n_days=60)
    res = runner.invoke(app, ["backtest", "--grid", "--no-save"])
    assert res.exit_code == 0, res.output
    assert "선택:" in res.output and "표본 외: 거래 18회" in res.output
    assert "거래 수 부족" in res.output      # 표본 외 18일뿐이라 통과 기준(50회) 미달


def test_backtest_without_data_fails_cleanly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    shutil.copytree(ROOT / "config", tmp_path / "config")
    res = runner.invoke(app, ["backtest"])
    assert res.exit_code == 1 and "backfill" in res.output


def test_data_status_lists_coverage(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch, n_days=3)
    res = runner.invoke(app, ["data", "status"])
    assert res.exit_code == 0 and "KR:111111" in res.output and "3거래일" in res.output
