# 04. 자동매매 플랫폼·프레임워크의 설계와 운영 리스크 통제 (2026-11 기준)

> 조사 방법 메모(보고서 작성자용)
> - 이 세션은 외부 웹 페이지 직접 열람(WebFetch)이 네트워크 정책으로 막혀 있었다(freqtrade.io, sec.gov 등 접속 불가). 대신 ① 공개 GitHub 저장소를 read-only로 얕게 복제해 **문서 원문을 직접 읽었고**(Freqtrade develop 2026-11-19 커밋, NautilusTrader develop 2026-11-22 커밋, LEAN master 2026-11-20 커밋 등), ② 웹 검색 결과 요약을 사용했다. 검색 예산이 중간에 소진되어 일부 항목은 검색으로 재확인하지 못했다.
> - 따라서 각 항목에 **[원문 확인]**(저장소 문서를 직접 읽음) / **[검색 요약]**(검색 결과 요약에만 근거, 원문 미열람) 표시를 붙였다. 표시가 없는 "Gaps"의 "미검증 사전지식" 항목은 출처 원문을 이번에 확인하지 못한 것이므로 보고서에 쓰려면 재검증이 필요하다.
> - GitHub 스타 수는 git으로 확인할 수 없어 전부 [검색 요약]이며 시점이 2026-03~04로 다소 오래되었다.

---

## 1. 프레임워크 서베이와 채택 근거 — 어떤 것이 가장 많이 쓰이고 왜인가

### Takeaway
오픈소스 중 채택 근거가 가장 뚜렷한 것은 Freqtrade(스타 약 4.9만, 월간 릴리스), NautilusTrader(약 2.2만, Rust 코어·백테스트/라이브 동일 코드), QuantConnect LEAN(약 1.8만, 커뮤니티 52만 명 주장)이며, 공통된 인기 요인은 "전략 코드 하나로 백테스트→모의→실거래", 드라이런, 원격 모니터링, 내장 보호장치다. Backtrader·Blankly는 사실상 유지보수가 멈췄고, 소규모 단일 사용자 Python 도구가 벤치마크할 대상은 기능 구성 면에서 Freqtrade, 엔진 설계 면에서 NautilusTrader/LEAN이다.

### Cited Findings

**Freqtrade (Python, 암호화폐 중심이지만 설계는 범용)**
- [검색 요약] GitHub 스타 약 48.7k (Star History, 2026-04-16 기준) — [Star History](https://www.star-history.com/freqtrade/freqtrade/). 다른 스냅샷은 50,739개 — [ecosyste.ms](https://summary.ecosyste.ms/projects/357309)
- [원문 확인] 연도 기반 버전(예: `2026.9` 태그 존재)으로 월간 릴리스. develop 브랜치 최신 커밋 2026-11-19 — [freqtrade 저장소](https://github.com/freqtrade/freqtrade). (검색 요약상 PyPI 최신은 2026.10이라고 하나 공식 릴리스 페이지로는 미확인 — [Releases](https://github.com/freqtrade/freqtrade/releases))
- [원문 확인] 봇 루프는 기본 5초(`internals.process_throttle_secs`)마다 돌며 "DB에서 열린 거래 로드 → 캔들 갱신(캔들당 1회만) → 지표/진입/청산 신호 계산 → 주문 상태 갱신·타임아웃 처리 → 청산 판단 → 슬롯 확인 → 진입" 순서 — [bot-basics.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-basics.md), [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md)

**NautilusTrader (Rust 코어 + Python 제어면)**
- [검색 요약] GitHub 스타 약 22.1k (Star History, 2026-04-20) — [Star History](https://star-history.com/nautechsystems/nautilus_trader); CCXT 비교 페이지는 28.3k 스타·PyPI 월 36.1만 설치라고 적었으나 날짜 미표기로 상충 — [CCXT vs NautilusTrader](https://docs.ccxt.com/docs/comparisons/ccxt-vs-nautilustrader)
- [원문 확인] 자기 정의: "open-source, production-grade, Rust-native engine for multi-asset, multi-venue trading systems", 연구·결정론적 시뮬레이션·라이브 실행을 "single event-driven architecture"로 묶음. 저장소 `version.json`은 v2.0.0 표기(2026-11-22 커밋, 정식 릴리스 여부는 미확인) — [overview.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/overview.md)

**QuantConnect LEAN (C# 엔진, Python 전략 지원, 클라우드 플랫폼)**
- [검색 요약] 스타 약 18.4k (2026-04-15) — [Star History](https://star-history.com/quantconnect/lean). QuantConnect 자체 주장: 커뮤니티 525,200명, 월 평균 5만 명이 약 2,500개 신규 알고리즘 작성 — [QuantConnect splash](https://www.quantconnect.com/splash). 제3자 리뷰(2026-03)는 등록 48.3만 명·누적 라이브 전략 37.5만 개라고 썼으나 1차 출처 불명 — [newtrading.io 리뷰](https://www.newtrading.io/?p=13451)
- [원문 확인] README 자기 정의: "event-driven, professional-caliber algorithmic trading platform … modular in design, with each component pluggable"; master 최신 커밋 2026-11-20 — [QuantConnect/Lean](https://github.com/QuantConnect/Lean)

**유지보수 상태(저장소 최신 커밋일, 2026-11-22에 직접 확인)**
- [원문 확인] Backtrader 최신 커밋 2023-04-19(사실상 중단) — [mementum/backtrader](https://github.com/mementum/backtrader); "Backtrader is no longer maintained" — [Trading Strategy 문서](https://tradingstrategy.ai/docs/learn/algorithmic-trading-frameworks.html). 스타는 약 15K라는 2차 자료 — [autotradelab 비교 글](https://autotradelab.com/blog/nautilus-vs-vectorbt-vs-freqtrade-20-python-quant-trading-frameworks-compared)
- [원문 확인] Blankly 최신 커밋 2024-12-30(약 2년 정체). README는 "The same code can be backtested, paper traded, sandbox tested and run live by simply changing a single line"을 내세웠음 — [blankly-finance/blankly](https://github.com/blankly-finance/blankly)
- [원문 확인] zipline-reloaded 최신 커밋 2026-11-02(유지 중, 백테스트 전용) — [stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded)
- [원문 확인] vectorbt 최신 커밋 2026-11-11, 라이선스 배지는 "Fair Code", 선택형 Rust 엔진(`vectorbt-rust`) 추가, 상단에 유료 VectorBT PRO 안내. 자기 정의는 "Python toolkit for trading research … compare thousands of ideas across assets and timeframes" — [polakowo/vectorbt](https://github.com/polakowo/vectorbt). 스타 약 4.3K라는 2차 자료(정확도 낮음) — [autotradelab 비교 글](https://autotradelab.com/blog/nautilus-vs-vectorbt-vs-freqtrade-20-python-quant-trading-frameworks-compared)
- [원문 확인] Hummingbot 최신 커밋 2026-11-18. README: "Over the past year, Hummingbot users have generated over $34 billion in trading volume across 140+ unique trading venues"(자체 보고 수치). LLM 판단을 결정론적 주문 실행에 연결하는 별도 하네스 "Condor"(Telegram/웹 대시보드 제어)를 운영 — [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot)
- [원문 확인] Jesse 최신 커밋 2026-11-17. README 기능: look-ahead bias 없는 멀티 타임프레임 백테스트, Optuna+Ray 최적화, 실시간 알림, 백테스트/페이퍼/라이브 공통 인터랙티브 차트, **Monte Carlo(거래 순서 셔플 + 캔들 기반 시뮬레이션)**, 유의성 검정 — [jesse-ai/jesse](https://github.com/jesse-ai/jesse)
- [원문 확인] Lumibot 최신 커밋 2026-11-20. README 표어가 "Build AI trading agents. Backtest them. Trade with the same strategy."로 바뀌었고, "keep your strategy class; change the data source and broker runner"를 강조. 주식·옵션·선물·FX·크립토 지원 — [Lumiwealth/lumibot](https://github.com/Lumiwealth/lumibot)
- [원문 확인] OctoBot 최신 커밋 2026-11-19, "free open-source crypto trading bot with a visual user interface", Telegram·TradingView 연동 — [Drakkar-Software/OctoBot](https://github.com/Drakkar-Software/OctoBot)
- [원문 확인] ib_async(구 ib_insync)는 Ewald de Wit가 만든 라이브러리를 Matt Stancliff가 이어 유지, 최신 커밋 2025-12-06 — [ib-api-reloaded/ib_async](https://github.com/ib-api-reloaded/ib_async). 원 저장소·패키징 접근권을 잃어 이름을 바꿨다는 설명 — [PyPI ib_async](https://pypi.org/project/ib_async/1.0.1)
- [원문 확인] backtesting.py 최신 커밋 2026-08-05, SAMBO 기반 내장 옵티마이저 — [kernc/backtesting.py](https://github.com/kernc/backtesting.py)

**상용/브로커 플랫폼**
- [검색 요약] Brokeree 설문 표본에서 브로커의 약 68%가 MT5를 제공하고 85.2%가 MetaTrader 계열을 1개 이상 사용 — [FX News Group](https://fxnewsgroup.com/forex-news/platforms/what-platforms-are-brokers-using-in-2025); MT5가 거래대금에서 MT4를 추월 — [Finance Magnates](https://www.financemagnates.com/forex/products/exclusive-after-15-years-mt5-overtakes-mt4-in-trading-volume-marking-end-of-an-era)
- [검색 요약] Composer(노코드 전략 빌더): 2026-01 월 거래대금 16억 달러, 2026-02 총자산 2.5억 달러 돌파, 커뮤니티 전략 3,000개 이상(모두 자체 발표) — [Composer what's new](https://www.composer.trade/whats-new); SoFi가 인수해 2026-06-23 "Composer by SoFi" 출시 — [The Paypers](https://thepaypers.com/mergers-aquisitions-and-investments/news/sofi-acquires-ai-startup-composer-to-democratise-trading-strategies), [Let's Data Science](https://letsdatascience.com/news/sofi-launches-ai-investing-platform-after-composer-buy-fe95d37f)

### Inferences
- "가장 많이 쓰이는" 오픈소스 3종(Freqtrade, NautilusTrader, LEAN)의 공통분모는 (a) 백테스트와 라이브가 같은 전략 코드를 실행, (b) 실거래 전 모의(dry-run/paper/sandbox) 모드, (c) 내장 리스크 계층, (d) 상태 영속화와 재시작 복구다. 사용자의 도구는 (a)(b)를 이미 지향하므로 (c)(d)가 우선 보강 대상이다.
- Backtrader·Blankly·Zipline(원본)의 정체는 "1인 유지보수 + 브로커 API 변화"가 프레임워크를 죽인다는 것을 보여 준다. 단일 사용자 도구는 Toss API 의존부를 얇은 어댑터 한 곳에 가두어야 브로커 변경·API 변경에 버틴다.
- 비전문가용 웹 UI라는 목표에는 OctoBot("visual user interface")·Composer(자연어/노코드)·FreqUI가 참고 대상이고, 엔진 정확성 측면은 NautilusTrader/LEAN이 참고 대상이다. 두 축을 섞지 말고 분리해 벤치마크하는 편이 낫다.

### Gaps
- 스타 수는 모두 2026-03~04 시점의 2차 추적 사이트 값이다. Freqtrade "5.3만 개(v2026.7 시점)"라는 수치가 검색 요약에 있었으나 출처 URL을 특정하지 못했다. Hummingbot·Jesse·Lumibot·OctoBot·backtesting.py의 스타 수는 확인하지 못했다.
- NinjaTrader, TradeStation EasyLanguage, MetaTrader 총 사용자 수, Alpaca의 자금 조달·계좌 수는 이번에 출처를 찾지 못했다(검색 예산 소진).
- vectorbt PRO의 가격·사용자 수, QuantConnect의 유료 가입자 수는 미확인.

---

## 2. 아키텍처 패턴 — 백테스트/라이브 일치, 전략 인터페이스, 주문 상태, 재시작 복구

### Takeaway
선도 프레임워크는 "전략은 신호만 내고, 주문은 반드시 리스크 엔진을 거쳐 실행 엔진으로 간다"는 단방향 파이프라인과 "주문 결과가 불명확하면 추측하지 말고 조회·대사(reconciliation)로 확정한다"는 원칙을 공유한다. Freqtrade의 선언적 전략 인터페이스(지표→진입→청산 + ROI 표/손절/보호장치)는 사용자의 dip-rebound 단일 전략에 거의 그대로 대응된다.

### Cited Findings

**Freqtrade 전략 인터페이스와 실행 순서 [원문 확인]**
- 전략은 `populate_indicators()` → `populate_entry_trend()` → `populate_exit_trend()` 세 함수로 신호를 만들고, 진입 직전 `confirm_trade_entry()`, 청산 직전 `confirm_trade_exit()`, 수량 결정 `custom_stake_amount()`, 그리고 `custom_exit()`/`custom_stoploss()` 콜백으로 세부 제어 — [bot-basics.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-basics.md)
- `minimal_roi`는 "진입 후 경과 분 → 최소 수익률" 딕셔너리(예: `{"40": 0.0, "30": 0.01, "20": 0.02, "0": 0.04}`)로, 시간이 지날수록 익절 기준을 낮추는 시간 감쇠형 익절표 — [strategy-customization.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/strategy-customization.md)
- 진입·청산 신호가 같은 캔들에 충돌하면 "freqtrade will do nothing and ignore the entry signal"(들어갔다 즉시 나오는 거래 방지) — [strategy-customization.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/strategy-customization.md)
- 미완성 캔들은 전략에 제공하지 않음: "Using incomplete candles will lead to repainting and consequently to strategies with 'ghost' buys, which are impossible to both backtest, and verify after they happened" — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- 미체결 주문 타임아웃: `unfilledtimeout.entry/exit` 경과 시 취소(청산은 새 가격으로 재주문), `exit_timeout_count` 회 초과 시 emergency exit(기본 시장가) 발동 — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md), [stoploss.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/stoploss.md)
- `stoploss_on_exchange`: 매수 체결 직후 거래소에 손절 주문을 걸어 "sudden crashes"와 네트워크 지연에 대비. 거래소 손절 주문을 수동 취소하면 봇이 다시 생성. 갱신 주기는 기본 60초(매 루프마다 하면 거래소에서 차단되므로) — [stoploss.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/stoploss.md)

**Freqtrade dry-run 모드 [원문 확인]**
- dry-run은 거래소에 읽기 전용 호출만 하고 주문은 시뮬레이션. 별도 DB 파일(`tradesv3.dryrun.sqlite`)을 쓰고, 실거래 전환 시 "use a different / fresh database to avoid dry-run trades messing with your exchange money and eventually tainting your statistics" — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md)
- dry-run 체결 가정: 시장가는 주문 시점 호가창 물량 기준 체결(최대 슬리피지 5%), 지정가는 가격이 도달하면 체결되거나 `unfilledtimeout`으로 만료, 지정가가 가격을 1% 넘게 교차하면 시장가로 전환. 재시작 후에도 열린 주문은 "오프라인 동안 체결되지 않았다"는 가정으로 유지 — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md)

**NautilusTrader 실행 파이프라인과 리스크 엔진 [원문 확인]**
- 주문 경로: `Strategy` → (`OrderEmulator`/`ExecutionAlgorithm`) → `RiskEngine` → `ExecutionEngine` → `ExecutionClient`. `RiskEngine`은 "backtest, sandbox, and live" 모든 환경에 동일하게 존재 — [execution/index.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/index.md)
- `RiskEngine` 기본 검증: 가격·수량 정밀도, 양(+)의 가격, 최소·최대 수량, 만료된 GTD, `reduce_only` 위반, 주문당 최대 명목금액(`max_notional_per_order`)과 종목별 min/max notional, **현금계좌 잔고 영향**, **제출·수정 속도 제한**, **거래 상태(`ACTIVE`/`HALTED`/`REDUCING`)**. 실패 시 표준 사유 코드가 붙은 `OrderDenied` 이벤트 생성 — [execution/index.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/index.md)
- 주문 명령 결과를 3종으로 분류: "Definitive local failure"(전송 안 됨이 증명됨 → `OrderDenied`), "Definitive venue result"(거래소가 명시 확인), **"Unknown live outcome"**(거래소에 도달했을 수 있으나 결과 불명 → "Keeps the command in flight for stream updates, polling, queries, or reconciliation") — [execution/policies.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/policies.md)
- 중복 제출 방지: 이미 `INITIALIZED`/`RELEASED` 상태를 벗어난 주문에 대해 "A repeated `SubmitOrder` is skipped". 단, 이 dispatch 기록은 프로세스 로컬이라 재시작하면 사라짐 — [execution/policies.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/policies.md)

**재시작 후 대사(reconciliation) [원문 확인]**
- NautilusTrader: 시작 시 캐시된 주문·포지션 상태를 거래소 보고와 맞춘 뒤에야 전략을 시작. "An explicit position report is authoritative … the engine either aligns to that report within reconciliation tolerances or **fails closed**." 그리고 "Missing reports do not mean flat"(보고가 없다고 포지션이 없다고 가정하지 않음). 모든 실행 이벤트를 캐시 DB에 영속화하라고 권고 — [execution/reconciliation.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/reconciliation.md)
- NautilusTrader가 명시하는 백테스트↔라이브 차이 6가지: Venue(주문유형 지원 차이), Transport(네트워크 실패로 주문 결과 불명), Timing(입력 순서가 섞임), Persistence, External activity(봇 밖에서 생긴 주문), Reconciliation — [live.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/live.md)
- Freqtrade: "Freqtrade assumes that the trades it opens are managed only though the bot." 수동으로 봇 자본을 매도하면 거래소 주문을 다시 찾아 복구를 시도하지만 "best-effort approach, and will not work in all cases". `/reload_trade <trade_id>`로 거래소에서 거래를 다시 불러오는 수동 복구 명령 제공 — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md), [telegram-usage.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/telegram-usage.md)

**데이터 품질·정체 데이터 [원문 확인]**
- Freqtrade는 마지막 캔들이 오래된 경우 "Outdated history for pair" 경고를 내고 **해당 종목에 진입하지 않음**. 원인으로 거래소 장애, 시스템 시각 오류, 거래 희소 종목, API 문제를 열거 — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- 누락 캔들은 직전 종가로 OHLC를 채우고 거래량 0인 "빈 캔들"로 보정("Missing data fillup"), 인접 캔들 간 30% 초과 가격 점프는 "Price jump between 2 candles detected" 경고 — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- NautilusTrader는 바 실행 시 `ts_init`이 반드시 **구간 종료 시각**이어야 한다고 경고("prevents the complete bar from becoming visible before it formed"). 시가 기준 타임스탬프 데이터는 `ts_init = ts_event + interval`로 보정 — [backtesting/bar-execution.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/bar-execution.md)
- Lumibot 내부 조사 노트(2026-06)의 실행 불변식: "An order may wait for the next actionable bar/quote, but the fill must be recorded at that actual executable source timestamp. It must not fill at the original simulated timestamp using a price from a later bar, a stale bar, or a synthetic forward-filled row." 누락 OHLCV를 forward-fill해 전략에 보이는 행으로 만들지 않도록 수정 — [Lumibot 저장소 docs/investigations](https://github.com/Lumiwealth/lumibot)

**레이트 리밋 [원문 확인]**
- Freqtrade는 OHLCV 다운로드를 "once per Candle"로 제한해 불필요한 트래픽을 피하고, 지갑 잔고 갱신도 RPC 호출당 최대 시간당 1회로 제한 — [bot-basics.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-basics.md), [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)

### Inferences (소규모 단일 사용자 도구 적용 판단)

| 패턴 | 채택 권고 | 근거/메모 |
|---|---|---|
| 전략→리스크 게이트→실행의 단방향 파이프라인 | **필수** | Nautilus `RiskEngine`처럼 백테스트·페이퍼·실거래 모두에서 같은 게이트 코드를 통과시키면 "페이퍼에서는 되던 주문이 실거래에서 거부"되는 종류의 차이를 줄일 수 있다. "AI는 점수만, 주문은 안 함" 원칙도 이 구조의 특수한 경우다. |
| 완성된 1분봉만 전략에 전달 | **필수** | REST 폴링에서는 진행 중인 분봉이 섞여 오기 쉽다. Freqtrade의 "incomplete candle 금지"와 Nautilus의 `ts_init=구간 종료` 규칙을 그대로 따른다. |
| 정체 데이터 시 신규 진입 차단 | **필수** | Freqtrade "Outdated history → 진입 안 함". 폴링 실패·장애 시 마지막 봉 시각이 N초 이상 뒤처지면 진입 금지, 청산 판단은 별도 정책으로. |
| 주문 결과 3분류(확정 실패/확정 결과/불명) | **실거래 전 필수** | REST 타임아웃 후 재전송이 중복 주문의 주원인이다. "불명"이면 재전송하지 말고 주문 조회로 확정한다. 클라이언트 주문 ID를 SQLite에 먼저 기록(전송 전 영속화)하면 재시작 후에도 중복을 걸러낼 수 있다(Nautilus의 dispatch 기록은 프로세스 로컬이라 재시작 시 사라진다는 한계를 스스로 명시). |
| 시작 시 대사 + fail-closed | **실거래 전 필수** | 브로커 잔고·미체결 조회가 로컬 SQLite와 다르면 자동매매를 시작하지 않고 사용자에게 보여 준다. "조회 실패 = 포지션 없음"으로 가정하지 않는다. |
| 페이퍼/실거래 DB 분리 | **필수(저비용)** | Freqtrade 권고 그대로. 자기개선 루프의 학습 데이터 오염도 막는다. |
| 시간 감쇠형 ROI 표 | 선택 | 현재의 TP/SL/시간청산을 "보유 시간에 따라 익절 기준이 낮아지는 표"로 일반화하는 것으로, 파라미터 수가 늘어 과최적화 위험이 따른다. |
| 거래소(브로커) 측 손절 주문 | 조건부 | Toss Open API가 조건부/스탑 주문을 지원하는지에 달려 있다(본 조사 범위 밖, 미확인). 미지원이면 프로세스가 죽은 동안 손절이 작동하지 않는다는 점을 UI에 명시해야 한다. |
| Clock 추상화 | 권장 | Nautilus는 환경별 clock을 커널이 선택한다. 전략·리스크 코드가 `datetime.now()`를 직접 부르지 않게 하면 백테스트·페이퍼·리플레이 테스트가 같은 코드로 돈다. |
| 메시지 버스, 멀티 베뉴, 나노초 정밀도, Rust 코어 | 불필요 | 1분봉·단일 계좌·단일 전략에는 과설계. |

### Gaps
- LEAN의 라이브 대사·브로커리지 모델 문서는 이번에 원문을 열람하지 못했다(저장소 디렉터리 목록만 확인).
- Toss Securities Open API의 주문 조회·클라이언트 주문 ID·스탑 주문·레이트 리밋 사양은 본 과제 범위에서 확인하지 않았다.
- NautilusTrader의 `Clock`(TestClock/LiveClock) 세부 API는 architecture.md의 언급 수준만 확인했다 — [architecture.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/architecture.md)

---

## 3. 백테스트 현실성 — lookahead 탐지, 체결 모델, 봉 내 TP/SL 순서, 슬리피지·지연

### Takeaway
봉 데이터 백테스트의 핵심 약점은 "봉 안에서 무슨 일이 먼저 일어났는지 모른다"는 것이며, Freqtrade는 손절을 익절보다 먼저 평가하는 보수적 규칙과 더 작은 타임프레임 재검증(`--timeframe-detail`)으로, NautilusTrader는 O→H→L→C 경로 가정과 확률적 체결 모델로 대응한다. Freqtrade의 `lookahead-analysis`·`recursive-analysis`는 "코드를 읽지 않고 결과를 흔들어 편향을 드러내는" 방식이라 소규모 도구도 싸게 모방할 수 있다.

### Cited Findings

**Freqtrade 백테스트 가정 [원문 확인]** — [backtesting.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/backtesting.md)
- "Entries happen at open-price unless a custom price logic has been specified"; "Exit-signal exits happen at open-price of the consecutive candle"
- "All orders are filled at the requested price (no slippage) as long as the price is within the candle's high/low range" — 즉 기본 백테스트에는 슬리피지 모델이 없다.
- "Stoploss exits happen exactly at stoploss price, even if low was lower, but the loss will be `2 * fees` higher than the stoploss price"
- "Stoploss is evaluated before ROI within one candle. So you can often see more trades with the `stoploss` exit reason comparing to the results obtained with the same strategy in the Dry Run/Live Trade modes"; "Low happens before high for stoploss, protecting capital first"
- 같은 캔들에서 여러 신호가 겹칠 때 평가 순서: Exit-signal → Stoploss → ROI → Trailing stoploss
- ROI 청산은 고가와 비교하되 ROI 값으로 체결(ROI 2%, 고가 5%면 2%에 청산), 단 "Exits are never below the candle"
- 결론 문장: "backtesting will **never** replace running a strategy in dry-run mode."
- `--timeframe-detail`: 메인 타임프레임(예: 1h)으로 신호를 계산하고, 신호가 있거나 포지션이 있는 캔들만 더 작은 타임프레임(예: 5m)으로 봉 내 움직임을 재현. 문서는 "last part of strategy development"에 써서 전략이 백테스트 가정을 악용하지 않는지 확인하라고 권고.

**Lookahead / recursive 분석 [원문 확인]**
- `lookahead-analysis`: 전체 백테스트로 기준선을 만든 뒤 "additional backtest runs for every entry and exit separately"를 돌려 잘라낸 데이터프레임과 기준선의 지표값·신호 위치가 달라지는지 비교. 코드 정적 분석이 아니라 결과 차이로 판정 — [lookahead-analysis.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/lookahead-analysis.md)
- 문서가 드는 편향 예: `shift(-10)`, `populate_*` 안의 `iloc[]`, rolling 없이 `.mean()/.min()/.max()`를 전체 데이터프레임에 적용, 통제 안 된 for 루프. "Usually the bias in the strategy is THE driving factor for 'too good to be true' profits." — [lookahead-analysis.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/lookahead-analysis.md)
- 한계: 트리거되지 않은 신호는 검증되지 않아 거짓 음성이 날 수 있음. "A negative result of each does not guarantee that there are none of the above errors" — [strategy-customization.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/strategy-customization.md)
- 추가 금지 패턴: `.resample('1h')`(왼쪽 경계 라벨로 미래 데이터 유입 → `label='right'` 사용), 긴 타임프레임을 `.merge()`로 붙이기("date refers to open date, not close date") — [strategy-customization.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/strategy-customization.md)
- `recursive-analysis`: 백테스트는 전체 구간 데이터를 쓰지만 라이브는 거래소가 주는 제한된 캔들 수만 쓰므로 EMA·RSI 같은 재귀 지표 값이 달라진다. 서로 다른 `startup_candle_count`로 마지막 행 지표값을 계산해 편차(%)를 표로 보고. 예시 표에서 startup 20개일 때 `rsi_14` 편차 24.141%, 100개일 때 0.007% — [recursive-analysis.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/recursive-analysis.md)

**NautilusTrader 바 실행·체결 모델·지연 [원문 확인]**
- 바는 "does not record when each price occurred within that interval or whether the high preceded the low. Bar-based execution thus simulates a plausible intrabar path rather than reconstructing the original trades." 각 바를 4개의 합성 업데이트로 쪼개 주문 매칭 — [bar-execution.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/bar-execution.md)
- 봉 내 경로: 기본은 `Open → High → Low → Close`. `bar_adaptive_high_low_ordering=True`면 시가에 더 가까운 극값을 먼저 방문. 문서 스스로 "deterministic heuristic, not a reconstruction"이며 정확도 일반화 근거가 없다고 명시. "the path matters when a protective stop and a profit target lie inside the same bar." — [bar-execution.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/bar-execution.md)
- `on_bar`에서 낸 주문은 그 바의 4개 가격점이 모두 처리된 뒤에 도착(= 같은 봉 체결 불가, 다음 봉부터) — [bar-execution.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/bar-execution.md)
- FillModel: `prob_fill_on_limit`(가격 터치 시 지정가 체결 확률), `prob_slippage`(체결마다 1틱 불리하게 밀릴 확률), 재현용 `random_seed`. 기본값은 각각 1.0과 0.0(= 기본은 낙관적). `OneTickSlippageFillModel`, `ProbabilisticFillModel`, `VolumeSensitiveFillModel`, `LimitOrderPartialFillModel` 등 내장 — [fill-models.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-models.md)
- `LatencyModel`: 각 명령을 도착 타임스탬프와 함께 inflight 큐에 넣어 제출·수정·취소 지연을 모사. 샌드박스에서는 inbound 구간만 지연 — [execution-flow.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md)

**LEAN [원문 확인(파일 목록) + 검색 요약]**
- [원문 확인] 내장 체결 모델: `EquityFillModel`, `ImmediateFillModel`, `LatestPriceFillModel`, `FutureFillModel` 등. 내장 슬리피지 모델: `ConstantSlippageModel`, `VolumeShareSlippageModel`, `MarketImpactSlippageModel`, `NullSlippageModel` — [Common/Orders/Fills](https://github.com/QuantConnect/Lean/tree/master/Common/Orders/Fills), [Common/Orders/Slippage](https://github.com/QuantConnect/Lean/tree/master/Common/Orders/Slippage)
- [검색 요약] "stale fill"은 1시간 이상 지난 가격 데이터로 체결되는 것으로 정의되며 `settings.stale_price_time_span`(기본 1시간)으로 조정 가능 — [Trade Fills key concepts](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/trade-fills/key-concepts)
- [검색 요약] QuantConnect는 시간봉·일봉에서 시장가 주문이 오래된 가격으로 체결되던 "stale price loophole"을 막아, 신선한 데이터가 올 때까지 주문을 보류하도록 기본 체결 모델을 변경(백테스트 한정) — [QuantConnect 공지](https://www.quantconnect.com/announcements/20949/closing-the-stale-price-loophole-on-daily-and-hourly-data/)

**기타**
- [원문 확인] Backtrader는 브로커 시뮬레이션에 "slippage, volume filling strategies", "Cheat-on-Close and Cheat-on-Open modes"를 제공(= 같은 봉 종가/시가 체결을 명시적 '치트' 옵션으로 분리) — [mementum/backtrader README](https://github.com/mementum/backtrader)
- [원문 확인] Lumibot은 SEC 재무 데이터를 "as they were known on each date, so backtests never see the future"(point-in-time)로 제공한다고 명시 — [Lumiwealth/lumibot](https://github.com/Lumiwealth/lumibot)

### Inferences
- 사용자의 "다음 봉 시가 체결 + 비용 모델"은 Freqtrade·Nautilus의 기본 가정과 같은 계열로 방향이 맞다. 보강할 것은 (1) **같은 1분봉 안에 TP와 SL이 모두 닿았을 때의 규칙을 명시하고 손절 우선으로 고정**(Freqtrade 방식. Nautilus 기본 O→H→L→C는 롱 포지션에서 익절이 먼저 체결되는 낙관 방향이므로 그대로 베끼면 안 된다), (2) 손절 체결가를 "정확히 손절가"가 아니라 갭 하락 시 봉 시가로 처리(Freqtrade도 "저가가 더 낮아도 손절가에 체결"로 가정해 낙관적이라는 한계가 있다), (3) 틱 단위 불리 체결 확률 같은 단순 슬리피지 노브.
- lookahead 검사는 소규모 도구에서 "절단 재계산 테스트"로 구현할 수 있다: 전체 데이터로 계산한 t 시점 지표/신호 값과, t까지만 잘라 계산한 값이 같은지 무작위 N개 시점에서 비교한다. 자기개선 루프가 피처를 자동으로 추가·변경한다면 이 검사를 루프의 필수 관문으로 넣을 가치가 크다.
- recursive 검사는 REST 폴링 도구에 직접 해당한다: 실시간 루프가 최근 K개 분봉만 가져와 EMA/RSI를 계산하면 백테스트(전 구간 계산)와 값이 달라진다. K별 편차 표를 한 번 만들어 워밍업 봉 수를 정해야 한다. 장 시작 직후(전일 데이터 이어붙임 여부)에도 같은 문제가 생긴다.
- 1분봉보다 작은 데이터가 없으면 `--timeframe-detail` 방식은 쓸 수 없으므로, 대안은 "TP·SL 동시 터치 봉의 비율"을 리포트에 표시해 결과가 봉 내 순서 가정에 얼마나 민감한지 보여 주는 것이다.
- 생존편향 없는 데이터(상장폐지·거래정지 종목 포함)는 종목 선정 단계의 문제로, 고정 워치리스트 방식이면 "오늘 기준으로 고른 종목을 과거에 적용"하는 편향이 남는다는 점을 리포트에 경고로 넣는 정도가 현실적이다.

### Gaps
- LEAN `EquityFillModel`의 세부 체결 규칙과 슬리피지 수식은 원문을 읽지 못했다.
- 한국 주식 특유 요소(호가단위, 동시호가, VI 발동, 상·하한가, 거래정지)를 반영한 체결 모델 사례는 조사 대상 프레임워크에서 찾지 못했다(모두 해외/크립토 중심).
- 생존편향 없는 한국 분봉 데이터 공급원은 본 조사 범위 밖.

---

## 4. 최적화·검증 도구 — Hyperopt 손실함수, walk-forward, Monte Carlo, 표본 외 관행

### Takeaway
Freqtrade Hyperopt는 손실함수 13종(Sharpe/Sortino/Calmar/낙폭/복합지표 등)을 제공하지만 문서 자체에는 walk-forward·Monte Carlo 기능이 없고, 과최적화 방지는 탐색 정밀도 제한과 사용자의 표본 외 검증에 맡겨져 있다. 거래 순서 셔플 Monte Carlo는 Jesse·QuantStats가 내장하고 있으며, 학계 기준(PBO, Deflated Sharpe)은 "많이 시도할수록 최고 성과는 부풀려진다"는 점을 정량화한다.

### Cited Findings
- [원문 확인] Freqtrade 내장 손실함수: `ShortTradeDurHyperOptLoss`, `OnlyProfitHyperOptLoss`, `SharpeHyperOptLoss`, `SharpeHyperOptLossDaily`, `SortinoHyperOptLoss`, `SortinoHyperOptLossDaily`, `MaxDrawDownHyperOptLoss`, `MaxDrawDownRelativeHyperOptLoss`, `MaxDrawDownPerPairHyperOptLoss`, `CalmarHyperOptLoss`, `ProfitDrawDownHyperOptLoss`, `MultiMetricHyperOptLoss` — [hyperopt.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/hyperopt.md)
- [원문 확인] `MaxDrawDownPerPairHyperOptLoss`는 종목별 수익/낙폭 비율 중 **최악값**을 목적함수로 삼아 "one or more pairs with good results from inflating the metrics"를 막는다. `MultiMetricHyperOptLoss`는 수익·낙폭 외에 Profit Factor, Expectancy Ratio, Winrate를 함께 보고 **거래 수가 적은 epoch에 페널티**를 준다 — [hyperopt.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/hyperopt.md)
- [원문 확인] 과최적화 관련 내장 장치: 탐색 공간 소수점 3자리 제한("every value more precise than this will usually result in overfitted results"), 재현을 위한 `--random-state`, 초기 30개 무작위 epoch, trailing 공간은 다른 공간을 "found, validated"한 뒤 따로 최적화하라는 권고 — [hyperopt.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/hyperopt.md)
- [원문 확인] "Why do my backtest results not match my hyperopt results?" 항목: 설정 파일의 `stoploss`/`max_open_trades`/`trailing_stop`이 전략 값을 덮어쓰는 경우, `populate_indicators()`에 둔 하이퍼파라미터가 전 epoch에 한 번만 계산되는 경우 등을 원인으로 열거 — [hyperopt.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/hyperopt.md)
- [원문 확인] Freqtrade 문서 디렉터리 전체에서 "walk-forward", "monte carlo" 문자열 검색 결과 0건(2026-11-19 develop 기준) — [freqtrade docs](https://github.com/freqtrade/freqtrade/tree/develop/docs)
- [원문 확인] Protections는 백테스트·hyperopt에서 지원되지만 `--enable-protections` 플래그로 명시적으로 켜야 함 — [protections.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/includes/protections.md)
- [원문 확인] Jesse: "Monte Carlo Analysis: Stress-test your strategies with trade-order shuffling and candles-based simulations to distinguish skill from luck and guard against overfitting", "significance tests" — [jesse-ai/jesse](https://github.com/jesse-ai/jesse)
- [원문 확인] QuantStats: `qs.stats.montecarlo(returns, sims=1000, bust=-0.20, goal=0.50)`로 파산/목표 도달 확률형 Monte Carlo 제공, HTML tearsheet 리포트 7종 — [ranaroussi/quantstats](https://github.com/ranaroussi/quantstats)
- [검색 요약] Bailey·Borwein·López de Prado·Zhu의 PBO 논문은 CSCV(combinatorially symmetric cross-validation)로 백테스트 과최적화 확률을 추정하며, 단순 hold-out은 투자 백테스트 맥락에서 "unreliable and inaccurate"한 경향이 있다고 주장 — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)
- [검색 요약] Deflated Sharpe Ratio는 "selection bias under multiple testing and non-Normally distributed returns" 두 가지 부풀림 요인을 보정 — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)

### Inferences
- 사용자의 "누적 모의매매로 학습하는 자기개선 루프"는 본질적으로 반복 최적화이므로 다중 검정 문제가 그대로 적용된다. 최소 장치로 (1) **시도 횟수 기록**(몇 개의 파라미터 조합을 평가했는지 리포트에 표시), (2) 시간순 분할의 표본 외 구간을 루프가 절대 보지 못하게 잠그기, (3) 최고점 하나가 아니라 **주변 파라미터도 양호한 "고원"** 선택(파라미터 안정성 히트맵), (4) 거래 수 하한(Freqtrade `MultiMetricHyperOptLoss`의 저거래 페널티와 같은 취지)을 권한다.
- 목적함수는 순수익 단독보다 낙폭을 포함한 복합형(Calmar, Profit-Drawdown)이나 "종목별 최악값"이 과최적화에 덜 취약하다는 것이 Freqtrade 손실함수 구성에서 읽히는 설계 의도다.
- Monte Carlo 거래 셔플은 구현이 매우 싸다(체결 거래 손익 배열을 재배열/복원추출해 낙폭 분포 산출). 비전문가 UI에서는 "운이 나빴다면 최대 낙폭이 이 정도까지 갈 수 있음"을 한 줄로 보여 주는 데 적합하다. 다만 거래 간 자기상관(연속 손실 군집)을 지우므로 낙관적으로 나올 수 있다.
- walk-forward는 1분봉 단타에서 "N주 학습 → 다음 1주 검증"의 굴림 방식으로 구현 가능하며, 페이퍼 트레이딩 자체가 가장 엄격한 walk-forward(진짜 미래 데이터)다. 페이퍼 결과를 학습에 쓰기 시작하면 그 구간은 더 이상 표본 외가 아니라는 점을 데이터 계보에 기록해야 한다.

### Gaps
- LEAN의 파라미터 최적화/walk-forward 기능과 vectorbt(PRO)의 Splitter·교차검증 기능은 이번에 출처를 확보하지 못했다(검색 예산 소진).
- PBO 임계값(예: 0.05), "N회 시도 시 기대 최대 Sharpe ≈ σ·√(2 ln N)" 같은 수식은 2차 요약에서만 보았고 논문 원문으로 확인하지 못했다.
- Freqtrade 사용자 커뮤니티에서 hyperopt 과최적화 불만이 어느 정도 규모인지 보여 주는 정량 자료는 찾지 못했다.

---

## 5. 모니터링·운영 — Telegram 명령, 대시보드, 리포트, 하트비트/워치독, 상태 영속화

### Takeaway
Freqtrade가 사실상의 표준 운영 패턴을 보여 준다: 원격 명령으로 "신규 진입만 중지(/pause)", "전량 청산(/forceexit all)", "완전 정지(/stop)"를 구분하고, 60초 하트비트 로그와 systemd 워치독, `/health`(마지막 루프 시각) 엔드포인트로 생존을 감시한다. 주목할 설계 결함도 문서에 명시돼 있다 — 일시중지 상태는 영속화되지 않아 재시작하면 풀린다.

### Cited Findings
- [원문 확인] Telegram 시스템 명령: `/start`, `/pause | /stopentry | /stopbuy`("Gracefully handle open trades according to their rules. Do not enter new positions."), `/stop`, `/reload_config`, `/show_config`, `/logs [limit]`, `/health`("Show latest process timestamp") — [telegram-usage.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/telegram-usage.md)
- [원문 확인] 상태·거래 명령: `/status`, `/status table`, `/order <trade_id>`, `/trades`, `/count`, `/locks`, `/unlock`, `/forceexit <trade_id>`, `/forceexit all`, `/cancel_open_order`, `/reload_trade`, `/delete`. 성과 명령: `/profit [n]`, `/performance`, `/balance`, `/daily`, `/weekly` — [telegram-usage.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/telegram-usage.md)
- [원문 확인] 경고: "The pause/stopentry signal is ONLY active while the bot is running, and is not persisted anyway, so restarting the bot will cause this to reset." — [telegram-usage.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/telegram-usage.md)
- [원문 확인] 강제 진입 명령(`/forcelong`)은 `force_entry_enable`을 명시적으로 켜야만 동작(기본 비활성) — [telegram-usage.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/telegram-usage.md)
- [원문 확인] FAQ가 권하는 안전 종료 절차: `/stopentry`로 신규 진입을 막고 `/forceexit all`로 전량 청산 — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- [원문 확인] `cancel_open_orders_on_exit`: `/stop`, Ctrl+C, 또는 봇이 비정상 종료될 때 미체결 주문을 취소(포지션에는 영향 없음, 기본 false) — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md)
- [원문 확인] `internals.heartbeat_interval` 기본 60초마다 하트비트 로그; `internals.sd_notify`로 systemd에 keep-alive 핑과 상태(Running/Paused/Stopped)를 보내 "software watchdog monitoring freqtrade bot state and restarting it in the case of failures"로 사용(Docker 안에서는 동작 안 함) — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md), [advanced-setup.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/advanced-setup.md)
- [원문 확인] REST API `/health`는 "Show bot health (last bot loop)". RPC 메시지를 구독하는 WebSocket 엔드포인트 제공. `lookahead-analysis`·`recursive-analysis`도 webserver 모드에서 백그라운드 작업으로 실행 가능 — [rest-api.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/rest-api.md), [lookahead-analysis.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/lookahead-analysis.md)
- [원문 확인] `/reload_config`로 봇을 죽이지 않고 설정·전략을 다시 읽어 재시작 — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- [원문 확인] 상태 영속화: 거래는 SQLite(`tradesv3.sqlite`)에 저장되고 매 루프가 "Fetch open trades from persistence"로 시작 — [bot-basics.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-basics.md), [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- [원문 확인] NautilusTrader는 Redis/PostgreSQL 기반 선택적 상태 영속화를 제공하고, 대사를 위해 모든 실행 이벤트를 캐시 DB에 저장하라고 권고 — [overview.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/overview.md), [reconciliation.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/reconciliation.md)
- [원문 확인] Jesse는 백테스트·페이퍼·라이브 세션에 **동일한 차트 워크플로**(캔들+지표+주문+완료 거래 동기화)를 제공 — [jesse-ai/jesse](https://github.com/jesse-ai/jesse)
- [검색 요약] Knight Capital 사례의 운영 교훈과 직결: 장 시작 전 시스템이 오류를 가리키는 자동 이메일 97통을 보냈으나, 그 이메일이 시스템 경보로 설계되지 않아 수신 즉시 검토되지 않았다(아래 7번 항목 참조) — [WilmerHale 요약](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)

### Inferences
- 로컬 웹 UI에는 세 단계 버튼을 분리해 두는 것이 검증된 패턴이다: **① 신규 진입 중지(보유분은 규칙대로 관리) ② 전량 청산 ③ 완전 정지**. 비전문가에게는 "지금 누르면 무슨 일이 일어나는지"를 버튼 옆에 문장으로 써 준다.
- Freqtrade의 "일시중지가 재시작 시 풀린다"는 약점은 반면교사다. **중지·킬 스위치 상태는 SQLite에 저장하고, 재시작 시 기본값은 '중지'**(사람이 다시 켜야 진입 재개)로 두는 편이 안전하다.
- 하트비트는 "루프가 돌고 있다"만이 아니라 "마지막으로 완성 분봉을 받은 시각"과 "브로커 조회 마지막 성공 시각"을 따로 기록해야 정체 데이터와 프로세스 정지를 구분할 수 있다. 감시 주체는 봇 프로세스 밖(OS 서비스 관리자, 별도 경량 프로세스, 또는 외부 알림)이어야 한다 — 죽은 프로세스는 자기 죽음을 알릴 수 없다.
- 경보는 "읽히는 채널"로 보내야 한다(Knight의 97통 이메일). 단일 사용자 도구라면 휴대폰 푸시/메신저 1개 채널에 심각도 2단계(정보/즉시 조치) 정도로 단순화하는 것이 낫다.
- 리포트는 QuantStats 같은 기존 tearsheet 라이브러리를 그대로 쓰면 구현 비용이 거의 없다. 백테스트·페이퍼·실거래에 같은 리포트·차트 양식을 쓰면(Jesse 방식) 세 단계 간 성과 괴리를 한눈에 비교할 수 있다.

### Gaps
- FreqUI의 구체적 화면 구성·기능 목록(freq-ui.md)은 이번에 상세히 읽지 않았다.
- pyfolio의 현재 유지보수 상태는 확인하지 못했다.
- Discord/웹훅 알림 설정의 세부(webhook-config.md)는 읽지 않았다.

---

## 6. 표준으로 간주되는 리스크 관리 기능

### Takeaway
오픈소스 프레임워크들이 공통으로 내장한 것은 (1) 동시 보유 수 상한, (2) 연속 손절·낙폭 발생 시 자동 거래 중지와 쿨다운, (3) 주문 전 검증(수량·가격·명목금액·잔고·속도 제한), (4) 손익률 기반 킬 스위치다. 규제가 요구하는 통제(7번 항목)와 거의 일대일로 대응하며, 단일 사용자 도구에서도 구현 비용이 낮다.

### Cited Findings

**Freqtrade Protections [원문 확인]** — [protections.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/includes/protections.md)
- 정의: "Protections will protect your strategy from unexpected events and market conditions by temporarily stop trading for either one pair, or for all pairs." 모든 보호 종료 시각은 다음 캔들로 올림("to avoid sudden, unexpected intra-candle buys").
- `StoplossGuard`: `lookback_period` 안에 `trade_limit`건 이상 손절이 나면 `stop_duration` 동안 거래 중지. 기본은 전 종목 대상, `only_per_pair`로 종목별 적용. 예시: 최근 24캔들 내 손절 4회면 4캔들 동안 전 종목 중지. `stop_loss`, `stoploss_on_exchange`, `trailing_stop_loss` 결과 중 손실인 것만 집계.
- `MaxDrawdown`: lookback 구간에 종료된 거래로 낙폭 계산, `max_allowed_drawdown` 초과 시 중지. 계산 모드 2종 — `"ratios"`(레거시, 누적 수익률 기반 근사)와 `"equity"`(시작 잔고+누적 절대손익의 고점 대비 낙폭). 신규 설정은 `"equity"` 권장. 예시: 최근 48캔들·최소 20거래에서 낙폭 20% 초과 시 12캔들 중지.
- `LowProfitPairs`: 종목별 lookback 수익률이 `required_profit` 미만이면 그 종목만 잠금. 예시: 최근 6캔들·최소 2거래에서 2% 미만이면 60분 잠금.
- `CooldownPeriod`: 청산 후 해당 종목 재진입을 `stop_duration` 동안 금지(종목 단위로만 적용, 전체 잠금은 하지 않음).
- 공통 파라미터에 `unlock_at`("HH:MM")이 있어 특정 시각에 잠금 해제 가능. 같은 보호장치를 다른 파라미터로 여러 번 설정해 단기/장기 층을 쌓을 수 있고, 정의된 순서대로 평가.
- 문서 스스로의 주의: "Not all Protections will work for all strategies, and parameters will need to be tuned for your strategy."

**포지션·자본 한도 [원문 확인]**
- Freqtrade `max_open_trades`(필수 설정, 종목당 1개 거래), `tradable_balance_ratio`(기본 0.99, 봇이 쓸 수 있는 잔고 비율), `available_capital`(봇에 배정한 시작 자본) — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md)
- LEAN 내장 리스크 모델: `MaximumDrawdownPercentPerSecurity`, `MaximumDrawdownPercentPortfolio`, `MaximumSectorExposureRiskManagementModel`, `MaximumUnrealizedProfitPercentPerSecurity`, `TrailingStopRiskManagementModel` — [Algorithm.Framework/Risk](https://github.com/QuantConnect/Lean/tree/master/Algorithm.Framework/Risk)

**주문 전 검증·거래 상태 [원문 확인]**
- NautilusTrader `RiskEngine`: 주문당 최대 명목금액, 현금계좌 잔고 영향, 제출·수정 속도 제한, 거래 상태 `ACTIVE`/`HALTED`/`REDUCING`(REDUCING = 포지션 축소 주문만 허용) — [execution/index.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/index.md)

**킬 스위치 [원문 확인]**
- Hummingbot 클라이언트 설정에 `kill_switch_mode`(enabled/disabled)와 `kill_switch_rate`가 있으며 프롬프트는 "At what profit/loss rate would you like the bot to stop? (e.g. -5 equals 5 percent loss)" — [client_config_map.py](https://github.com/hummingbot/hummingbot/blob/master/hummingbot/client/config/client_config_map.py)
- Jesse는 "Built-in helper functions for robust risk management"를 기능으로 명시 — [jesse-ai/jesse](https://github.com/jesse-ai/jesse)

**정체 데이터·시장 상태 [원문 확인]**
- Freqtrade: 오래된 캔들이면 진입 차단(2번 항목) — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- NautilusTrader `MarketHoursFillModel`(정규/비정규 유동성에 따라 합성 스프레드 변경), `instrument_status` 데이터 타입 존재 — [fill-models.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-models.md), [docs/concepts/data](https://github.com/nautechsystems/nautilus_trader/tree/develop/docs/concepts/data)

### Inferences (단일 사용자·롱온리·현금주식·1분봉 도구에 대한 채택 판단)

| 통제 | 판단 | 구현 메모 |
|---|---|---|
| 동시 보유 종목 수 상한 | **필수** | Freqtrade `max_open_trades`. |
| 거래당 위험 기반 수량 산정(손절폭 × 수량 ≤ 계좌의 x%) | **필수** | 조사한 문서들은 고정 금액/잔고 분할이 기본이고 위험 기반 사이징은 콜백(`custom_stake_amount`)으로 사용자에게 맡긴다. 도구가 기본 제공하면 차별점이 된다. |
| 일일 손실 한도(도달 시 당일 신규 진입 금지) | **필수** | Freqtrade `MaxDrawdown`(equity 모드) + `unlock_at`의 조합과 같은 효과. 단타 도구에서는 "당일 실현+평가손익 기준, 다음 거래일 자동 해제"가 자연스럽다. |
| 연속 손절 후 쿨다운 | **필수** | `StoplossGuard`. dip-rebound(하락 매수) 전략은 추세 하락장에서 연속 손절이 군집하므로 가장 직접적인 방어다. |
| 종목별 재진입 쿨다운 | **필수(저비용)** | `CooldownPeriod`. 같은 종목에 청산 직후 다시 들어가는 반복 진입 방지. |
| 저성과 종목 일시 제외 | 권장 | `LowProfitPairs`. 단, 표본이 작으면 잡음에 반응한다. |
| 계좌 낙폭 정지(수동 해제 필요) | **실거래 전 필수** | 일일 한도와 별개로 누적 낙폭 임계 도달 시 자동매매 전체 정지, 사람만 해제. |
| 주문 전 검증: 수량·주문금액 상한, 가격 괴리(price collar), 잔고 확인 | **실거래 전 필수** | Nautilus `RiskEngine` 항목 그대로. 현재가 대비 ±x% 밖 지정가, 설정 금액 초과 주문, 보유수량 초과 매도는 전송 전 거부. |
| 주문 속도 제한·반복 주문 차단 | **실거래 전 필수** | 분당 주문 수 상한, 같은 종목·방향 주문이 N초 내 반복되면 차단. 폭주 루프(runaway loop)에 대한 최후 방어선. |
| 거래 상태 3단계(ACTIVE/REDUCING/HALTED) | **필수** | 5번 항목의 UI 3버튼과 같은 상태 기계. |
| 장 운영시간 가드 | **필수** | 정규장 외 주문 금지, 장 시작 직후·마감 직전 진입 금지 구간, 마감 전 강제 청산(이미 시간 청산이 있음). 휴장일·단축 거래일 달력 필요. |
| 섹터 노출 한도, 레버리지·증거금 검사 | 불필요 | 롱온리 현금·소수 종목에는 과함(종목당 비중 상한 하나로 충분). |

- 이 표의 통제는 **백테스트에서도 같은 코드로 켜져야** 한다(Freqtrade는 `--enable-protections`로 선택, Nautilus는 모든 환경에 상시 적용). 그렇지 않으면 실거래에서만 보호장치가 작동해 백테스트와 성과가 어긋난다.

### Gaps
- "거래당 계좌의 1~2% 위험" 같은 구체적 수치 관행의 1차 출처는 이번에 확보하지 못했다(프레임워크 문서는 수치를 권고하지 않음).
- Freqtrade Edge 모듈(승률 기반 포지션 사이징)의 현재 상태(폐기 여부)는 `deprecated.md`를 읽지 않아 미확인.
- LEAN 리스크 모델들의 기본 파라미터 값은 소스 본문을 읽지 않아 미확인.

---

## 7. 실패 사례와 규제 — Knight Capital, 한맥투자증권, 소매 봇 사고, 15c3-5 / RTS 6 / FIA / KRX

### Takeaway
Knight Capital(2012, 4.6억 달러 손실)과 한맥투자증권(2013, 462억 원 손실·파산)은 모두 "배포·설정 변경 직후, 사전 주문 통제와 자동 차단이 없어서, 수 분~수십 분 만에 회사를 잃은" 사례이며, 이후 규제(SEC 15c3-5, MiFID II RTS 6, FIA 모범규준, KRX 가이드라인)는 공통으로 사전 주문 통제·킬 기능·테스트·변경관리·실시간 경보를 요구한다. 개인용 도구에는 법적 의무가 아니지만 같은 통제를 축소판으로 갖추는 것이 실거래 전 최소 요건이다.

### Cited Findings

**Knight Capital (2012-08-01)**
- [검색 요약] SEC는 2013-10-16 Knight Capital Americas LLC에 Market Access Rule(15c3-5) 위반으로 1,200만 달러 과징금과 독립 컨설턴트 선임을 명령. 15c3-5에 따른 **첫 집행 사례** — [SEC 보도자료 2013-222](https://www.sec.gov/news/press-release/2013-222)
- [검색 요약] 오류로 3억 9,700만 주 이상이 거래되고 수십억 달러 규모의 원치 않는 포지션이 쌓였으며 거래 손실은 4억 6,000만 달러 초과 — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)
- [검색 요약] 원인: 8번째 서버에서 옛 "Power Peg" 코드가 제거되지 않았고 새 RLP 코드도 배포되지 않았는데 아무도 몰랐다. 재사용된 플래그가 달린 주문이 그 서버로 가면서 남아 있던 결함 있는 Power Peg 코드가 작동 — [J.R. Varma 블로그(SEC 명령 요약)](https://www.jrvarma.in/blog/Y2013/Knight-Capital.html)
- [검색 요약] 장 시작 전 시스템이 오류를 가리키는 자동 이메일 97통을 직원들에게 보냈지만, 시스템 경보로 설계된 것이 아니어서 수신 시 검토되지 않았다 — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)
- [검색 요약] SEC 지적 사항에는 자동 경보 없이 사람의 모니터링에 의존해 재무 노출을 관리한 점, CEO 연례 인증서가 통제의 유효성이 아니라 "processes"가 있다고만 서술한 점 포함 — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)
- 명령 원문 위치(이번 세션에서 접속 불가) — [SEC Release No. 34-70694](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf)

**한맥투자증권 (2013-12-12)**
- [검색 요약] 코스피200 옵션 주문 사고로 약 462억 원(법원 자료 인용 기사는 463억 원) 손실. 직원이 옵션 가격 변수 중 이자율 계산식에서 잔여일을 365로 나눠야 하는데 0으로 나누는 식을 넣어, 소프트웨어의 매수 상한·매도 하한 가격이 설정되지 않았다 — [경향신문 2023-05-14](https://www.khan.co.kr/article/202305141457001)
- [검색 요약] 금융감독원은 사고를 '실수'(착오거래)로 결론 — [이투데이](https://www.etoday.co.kr/news/view/849470)
- [검색 요약] 한국거래소가 회원 공동기금으로 대금을 대신 결제 후 구상권 청구. 360억 원대 이익을 본 외국계 헤지펀드로부터 반환받지 못해 파산. 대법원은 2023-04 착오를 이유로 한 거래 취소를 인정하지 않음(거래소 승소 확정) — [이투데이 '한맥證 사태 10년 만의 결론'](https://www.etoday.co.kr/news/view/2248804)

**소매 봇 사고**
- [검색 요약] 3Commas(크립토 봇 플랫폼): 2022-12 약 10만 개의 API 키 유출 확인. 사용자들은 10월부터 문제를 제기했으나 회사는 처음에 피싱 탓으로 돌렸다가 CEO가 자사 유출을 인정. 피해액 추정은 1,490만~2,200만 달러로 출처마다 다름 — [Halborn](https://halborn.com/explained-the-3commas-breach-december-2022/), [Cointelegraph](https://cointelegraph.com/news/3commas-ceo-confirms-api-key-leak-following-warning-from-cz), [ForkLog/HAPI 분석](https://forklog.com/en/api-key-leaks-and-exchange-inaction-a-hapi-analysis-of-the-3commas-incident/)
- [검색 요약] 한국 금융감독원은 2026-04 가상자산 API 거래가 거래대금의 약 30%라고 밝히며 API를 이용한 불공정거래를 경고했고, API 키가 유출되면 본인도 모르게 불법 행위 연루자로 간주될 수 있다고 주의를 줌 — [아시아경제](https://www.asiae.co.kr/en/article/2026041310210890706), [Cointelegraph](https://cointelegraph.com/news/south-korea-api-crypto-trading-30-percent-manipulation-risk)

**SEC Rule 15c3-5 (Market Access Rule, 2010)**
- [검색 요약] 시장접근 브로커-딜러는 사전 설정된 신용·자본 한도를 넘는 주문과 오류로 보이는 주문의 진입을 막도록 합리적으로 설계된 통제를 갖춰야 함. 오류 주문은 "rejecting orders that exceed appropriate price or size parameters, on an order-by-order basis or over a short period of time" 방식으로 방지 — [Federal Register 75 FR 69791](https://www.federalregister.gov/documents/2010/11/15/2010-28303/risk-management-controls-for-brokers-or-dealers-with-market-access), [SEC Small Entity Compliance Guide](https://www.sec.gov/files/rules/final/2010/34-63241-secg.htm)
- [검색 요약] 통제는 브로커-딜러의 "direct and exclusive control" 아래 있어야 하고, CEO가 매년 준수를 인증 — [SEC Small Entity Compliance Guide](https://www.sec.gov/files/rules/final/2010/34-63241-secg.htm)
- [검색 요약] FINRA 2026 감독 보고서는 사전 자본·신용 한도와 "duplicative and erroneous" 주문 임계값을 사업 모델에 비춰 비합리적으로 설정한 사례를 지적 — [FINRA 2026 Market Access Rule](https://finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/market-access-rule)

**MiFID II RTS 6 (Commission Delegated Regulation (EU) 2017/589)**
- [검색 요약] 제12조 kill functionality: "An investment firm shall be able to cancel immediately, as an emergency measure, any or all of its unexecuted orders submitted to any or all trading venues" — [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589); ESMA Q&A는 킬 기능이 절차와 스위치의 조합일 수 있다고 설명 — [ESMA Q&A 1612](https://www.esma.europa.eu/publications-data/questions-answers/1612)
- [검색 요약] 제15조 사전 통제: 권한 없는 상품 주문 자동 차단·취소, 전송한 모든 주문을 즉시 사전 한도 계산에 포함, **반복 자동 체결이 정해진 횟수에 도달하면 시스템을 자동 비활성화하고 지정 직원이 다시 켤 때까지 유지**, 차단된 주문을 그래도 내려면 특정 거래에 한해 일시적·예외적 절차로만 — [legislation.gov.uk 2017/589 Chapter II Section 3](https://www.legislation.gov.uk/eur/2017/589/chapter/II/section/3/data.htm)
- [검색 요약] 업무연속성 체계는 매년 검토·테스트 — [legislation.gov.uk 2017/589](https://www.legislation.gov.uk/eur/2017/589)

**FIA**
- [검색 요약] FIA는 2024-07 "Best Practices for Automated Trading Risk Controls and System Safeguards"를 발표. 목차에 사전 거래 통제와 테스트가 있고, 사전 통제 절은 "fat-finger" 주문 한도와 한도 위반 시 주문 거부를 다룸 — [FIA 발표](https://www.fia.org/fia/articles/fia-releases-best-practices-automated-trading-risk-controls-and-system-safeguards), [FIA PDF](https://fia.org/sites/default/files/2024-07/FIA_WP_AUTOMATED%20TRADING%20RISK%20CONTROLS_FINAL_0.pdf)
- [검색 요약] FIA의 2025-01 CME·ICE 리스크 통제 개요 자료는 kill switch와 order cancel on disconnect를 거래소 통제 목록에 포함 — [FIA Exchange Risk Controls overview](https://www.fia.org/fia/articles/exchange-risk-controls-overview-cme-and-ice-risk-controls)

**한국 (KRX·금융당국)**
- [검색 요약] 한국거래소 「알고리즘거래 위험관리 가이드라인」(2014-11): 목차에 알고리즘거래 프로그램 로직의 완전성 확보, 호가 입력 오류 방지 기능, 관련 법규 이해, 운용 방법 점검, 회원시스템의 **누적호가수량한도 및 위험노출액한도** 점검 항목 포함 — [가이드라인 PDF 사본(smallake.kr)](https://www.smallake.kr/wp-content/uploads/2010/11/20160124_111425.pdf)
- [검색 요약] 한맥 사태 이후 거래소는 파생상품시장에 **실시간 가격제한**(직전 체결가 ± 변동폭을 벗어난 호가는 접수 자체를 거부)과 **착오거래 구제제도**를 2014-09-01 시행 — [이투데이](https://www.etoday.co.kr/news/view/975435)
- [검색 요약] KRX는 실시간 가격 밴드와 함께 알고리즘 거래 계좌의 모든 주문을 거래소가 취소할 수 있는 킬 스위치 기능을 추가(기사 날짜 미확인) — [WatersTechnology](https://www.waterstechnology.com/node/2362551)
- [검색 요약] 2023-04-25부터 고속 알고리즘 거래를 하려는 투자자는 거래소 사전 등록 의무 — [머니투데이 2023-01-27](https://www.mt.co.kr/stock/2023/01/27/2023012715350053929); 2026-09 거래소는 ETF LP 계좌를 고속 알고리즘거래 계좌로 신고하지 않은 미래에셋증권에 회원경고 — [SBS Biz](https://biz.sbs.co.kr/amp/article/20000336958)

### Inferences — 단일 사용자 도구용 체크리스트(규제 요구의 축소 번역)

> 아래는 위 규제·사고에서 연구자가 도출한 것이며 법적 의무가 아니다(규제 대상은 브로커·회원사). 실거래 주문 코드를 쓰기 전에 충족할 조건으로 제안한다.

**A. 사전 주문 통제 (15c3-5의 price/size 파라미터, RTS 6 제15조, KRX 호가 입력 오류 방지)**
1. 주문 1건당 최대 금액·최대 수량 하드 상한(설정 파일이 아니라 코드 상수 또는 별도 잠금 설정).
2. 가격 괴리 검사: 최근 체결가 대비 ±x% 밖의 지정가 주문 거부. 한맥 사고의 본질은 가격 상·하한 검증이 꺼진 것이다.
3. 일일 누적 주문 금액·주문 건수 상한(KRX의 누적호가수량한도·위험노출액한도 개념).
4. 중복 주문 차단: 같은 종목·방향·수량 주문이 짧은 시간 내 반복되면 거부(FINRA가 말하는 duplicative order 통제).
5. 반복 실행 자동 정지: N회 연속 체결/거부 등 비정상 패턴 시 자동 비활성화, **사람이 다시 켜기 전까지 유지**(RTS 6 제15조의 repeated automated execution throttle).
6. 입력값 검증: 0·음수·NaN·0으로 나누기·자릿수 오류를 계산 단계에서 예외로 처리하고 주문을 내지 않는다(한맥의 "0으로 나눔").

**B. 킬 기능 (RTS 6 제12조, FIA, KRX 킬 스위치)**
7. 한 번의 조작으로 미체결 주문 전량 취소 + 신규 주문 차단. UI 버튼과 별도로 프로세스 밖에서 작동하는 수단(예: 플래그 파일, 브로커 앱에서 API 키 비활성화 방법 안내)을 둔다.
8. 연결 끊김·프로세스 종료 시 미체결 주문 처리 정책을 명시(FIA의 cancel on disconnect, Freqtrade의 `cancel_open_orders_on_exit`).

**C. 배포·변경 관리 (Knight의 직접 원인)**
9. 사용하지 않는 코드·플래그는 삭제한다. 옛 플래그를 다른 의미로 재사용하지 않는다(Power Peg).
10. 실행 중인 코드 버전(커밋 해시)과 설정 해시를 시작 로그와 UI에 표시하고, 버전이 바뀐 뒤 첫 실행은 페이퍼 모드로 강제하거나 사용자 확인을 요구한다.
11. 전략 파라미터 변경(자기개선 루프의 산출물 포함)은 자동 적용하지 않고 변경 이력·승인 기록을 남긴다. 되돌리기(rollback) 경로를 미리 만든다.
12. 실거래/페이퍼 전환은 설정 한 줄이 아니라 명시적 다단계 확인으로 한다.

**D. 감시·경보 (Knight의 97통 이메일, 15c3-5의 자동 경보 요구)**
13. 경보는 실제로 보는 채널로, 심각도에 따라 구분해 보낸다. "오류 로그가 파일에 쌓이기만 하는" 상태를 금지.
14. 예상 밖 포지션(전략이 낸 적 없는 보유, 수량 불일치)을 주기적 대사로 탐지하고 발견 즉시 정지.
15. 손익·노출의 자동 임계 경보(사람의 눈에 의존하지 않기).

**E. 테스트 (RTS 6의 테스트 요구, FIA 테스트 절, KRX 로직 완전성)**
16. 주문 경로 전체를 가짜 브로커(모의 어댑터)로 자동 테스트: 타임아웃, 부분 체결, 거부, 중복 응답, 재시작 중 체결.
17. 재시작 복구 테스트: 주문 전송 직후·체결 직후·청산 주문 대기 중에 프로세스를 죽이고 재시작해 상태가 맞는지 확인.

**F. 자격증명 (3Commas, 금감원 경고)**
18. API 키는 로컬 OS 보안 저장소나 권한 제한 파일에 두고 저장소·로그·UI·LLM 프롬프트에 절대 넣지 않는다. 브로커가 허용하면 출금·이체 권한 없는 키, IP 제한을 쓴다. 제3자 서비스에 키를 맡기지 않는다(로컬 도구라는 구조 자체가 이 위험을 줄인다).

- 한맥 사례에서 개인 사용자에게 주는 추가 교훈: 착오 주문은 체결되면 **취소되지 않는다**(대법원 2023 판단). 사후 구제에 기대지 말고 사전 차단에 투자해야 한다.
- 고속 알고리즘거래 등록제는 1분봉 REST 폴링 도구와는 성격이 다르나, 브로커(토스증권)가 API 이용약관으로 주문 빈도·자동매매 범위를 제한할 수 있으므로 약관 확인이 필요하다.

### Gaps
- **미검증 사전지식(원문 재확인 필요, [SEC 명령 원문](https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf))**: Knight 사고가 약 45분간 지속되고 154개 종목에서 약 400만 건이 체결됐다는 수치, 순매수 약 35억 달러·순매도 약 31.5억 달러 포지션, Power Peg가 2003년부터 미사용이었다는 점, 기술자 1명이 수동 배포했고 2인 검토 절차·서면 절차가 없었다는 점, 사고 대응 중 정상 서버에서 새 코드를 제거해 상황을 악화시켰다는 점, Knight에 통합 킬 스위치·사고 대응 절차가 없었다는 점. 이번 세션에서는 sec.gov 접속 불가·검색 예산 소진으로 원문 대조를 못 했다. Doug Seven의 글 등 2차 자료도 열람하지 못했다.
- **미검증 사전지식([RTS 6 원문](https://eur-lex.europa.eu/eli/reg/2017/589/oj))**: 제15조가 price collars, maximum order values, maximum order volumes, maximum messages limits를 명시적으로 열거한다는 점, 제5~7조의 알고리즘 테스트(적합성 테스트·비실거래 테스트 환경·통제된 배포), 제9조의 연례 자체평가, 제16조의 실시간 모니터링, 제17조의 사후 통제. 검색 요약은 이 조항들을 확인해 주지 못했다.
- 15c3-5 조문에서 "duplicative orders"라는 정확한 문구는 검색 요약에서 확인되지 않았다(FINRA 보고서의 표현으로만 확인).
- FIA 2024 문서의 통제 목록 전체(메시지 스로틀, 자기매매 방지, 드롭 카피 등)와 하트비트 권고의 정확한 출처 문서는 확인하지 못했다.
- KRX 2014 가이드라인의 조문별 세부 내용과 현행 개정 여부, 킬 스위치의 정확한 도입 시점·적용 시장(주식시장 포함 여부)은 미확인. 착오거래 구제 손실 기준(검색 요약상 "10억 원"과 "100억 원"이 혼재)도 원문 확인이 필요하다.
- 주식시장에서 개인의 API 자동매매를 직접 다루는 금융감독원 유의사항 문서는 찾지 못했다.
- 소매 사용자의 "폭주 루프"나 거래소 장애로 인한 구체적 손실 사례는 신뢰할 만한 출처를 찾지 못했다(일화 수준 자료만 존재할 가능성).

---

## 8. 페이퍼→실거래 전환 관행

### Takeaway
프레임워크 문서들은 일관되게 "백테스트는 dry-run을 대체하지 못하고, 페이퍼도 실거래의 체결을 재현하지 못한다"고 명시한다. 페이퍼 체결은 구조적으로 낙관적(시장충격·대기열·지연 미반영)이므로, 실거래 전환은 최소 수량으로 시작해 예상 체결가 대비 실제 체결가를 기록·비교하는 단계가 필요하다.

### Cited Findings
- [원문 확인] Freqtrade: "backtesting will **never** replace running a strategy in dry-run mode"; `--timeframe-detail`에서도 유사한 성과가 나오는 전략은 dry/live에서 잘 될 가능성이 높지만 "only forward-testing (dry-mode) can really confirm a strategy" — [backtesting.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/backtesting.md)
- [원문 확인] Freqtrade: "We recommend starting the bot in the Dry-run mode to see how your bot will behave"; 실거래 전환 시 새 DB 사용; "In production mode, the bot will engage your money. Be careful, since a wrong strategy can lose all your money." — [configuration.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/configuration.md)
- [원문 확인] Freqtrade 백테스트는 dry/live보다 손절 청산이 더 많이 나오는 구조적 차이를 스스로 명시("Stoploss is evaluated before ROI within one candle") — [backtesting.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/backtesting.md)
- [원문 확인] NautilusTrader: "The same strategy and execution-algorithm code can run across backtest and live systems, reducing deployment divergence. Live execution still introduces venue, transport, timing, persistence, external-activity, and reconciliation behavior that a simulation may not reproduce." — [overview.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/overview.md)
- [원문 확인] NautilusTrader는 backtest와 live 사이에 **sandbox** 환경(실시간 데이터 + 모의 체결, 지연 모델 적용 가능)을 둔다 — [execution-flow.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md), [execution/index.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/execution/index.md)
- [검색 요약] Alpaca 페이퍼 트레이딩: 체결 가능한 주문의 10%에 무작위 크기의 부분 체결을 일부러 발생시킨다 — [Alpaca Paper Trading 문서](https://docs.alpaca.markets/docs/paper-trading). Alpaca 직원 설명으로는 실거래에서 부분 체결은 드물지만 알고리즘이 이를 처리하는지 검증하도록 의도적으로 높인 것 — [Alpaca 포럼](https://forum.alpaca.markets/t/alpaca-paper-trading-partial-order-fill/2683)
- [검색 요약] Alpaca 페이퍼 체결은 NBBO 호가 기준(매수는 매도호가, 매도는 매수호가) — [Alpaca 포럼](https://forum.alpaca.markets/t/does-a-paid-account-give-more-accurate-paper-market-fills/14303)
- [검색 요약] 제3자 글이 Alpaca 문서를 인용해 페이퍼가 반영하지 않는 것으로 시장충격, 정보 누출, 지연에 따른 슬리피지, 비시장성 지정가의 대기열 순서, 가격 개선을 열거(Alpaca 원문으로는 미확인) — [TradersPost](https://blog.traderspost.io/article/paper-trading-vs-live-results)
- [검색 요약] Alpaca 포럼에는 페이퍼 지정가 주문이 가격 교차 후 50~260초 늦게 체결됐다는 사용자 보고가 있음(페이퍼 환경 자체의 불완전성) — [Alpaca 포럼](https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223)
- [원문 확인] Lumibot은 주문·체결·의사결정 기록을 점검할 수 있게 하는 것을 핵심 가치로 내세움("The decision reaches a broker. Inspect the orders, fills and decision records.") — [Lumiwealth/lumibot](https://github.com/Lumiwealth/lumibot)

### Inferences
- 단계적 전환 설계 제안(연구자 종합): **백테스트 → 페이퍼(현재 단계) → 섀도 모드(실계좌 잔고·호가 조회는 실제로 하되 주문은 전송 직전에 기록만) → 최소 수량 실거래(종목당 1주 또는 최소 금액, 일일 손실 한도는 잃어도 되는 금액) → 단계적 증액**. 각 단계 진입 조건을 사전에 숫자로 적어 둔다(최소 거래 수, 최소 거래일 수, 페이퍼 대비 성과 괴리 허용폭, 무사고 일수).
- 섀도 모드는 조사한 프레임워크 문서에서 그 이름으로 확인되지는 않았지만 Nautilus의 sandbox가 가장 가깝다. 사용자의 도구는 "실주문 코드 없음" 상태이므로, 실주문 코드를 작성하되 전송을 막아 둔 섀도 단계를 거치면 주문 생성·검증·대사 로직을 돈을 걸지 않고 검증할 수 있다.
- **드리프트 모니터링 지표**(구현 비용이 낮은 순): ① 신호 시점 가격 대비 실제 체결가의 차이(구현 부족분, bp), ② 백테스트가 같은 날 같은 데이터로 냈을 거래 목록과 페이퍼/실거래 거래 목록의 일치율(신호 일치율), ③ 체결 지연(신호→체결 초), ④ 미체결·부분 체결 비율, ⑤ 청산 사유 분포(익절/손절/시간청산 비율)의 백테스트 대비 변화. ②는 "매일 장 마감 후 당일 데이터로 백테스트를 재실행해 페이퍼 거래와 비교"하는 자동 리플레이로 구현하면 백테스트-라이브 일치성을 지속적으로 검증할 수 있다.
- 한국 소형주·저유동 ETF에서는 1분봉 "다음 봉 시가 체결" 가정이 실제 호가 스프레드와 물량을 무시한다. 페이퍼 체결을 호가(매수는 매도1호가) 기준으로 보수화하는 Alpaca 방식을 따르는 것이 좋다.
- REST 폴링 지연 때문에 "다음 봉 시가"는 실제로는 "다음 봉 시작 후 수 초~수십 초 뒤 가격"이 된다. 페이퍼 단계에서 이 지연 분포를 측정해 백테스트 비용 모델에 되먹임해야 한다.

### Gaps
- 실거래 전환 기준에 대한 업계 표준 수치(예: 최소 페이퍼 기간, 최소 거래 수)는 신뢰할 만한 1차 출처를 찾지 못했다. Alpaca의 "Paper Trading vs. Live Trading: A Data-Backed Guide" 글은 존재만 확인하고 내용은 열람하지 못했다 — [Alpaca Learn](https://alpaca.markets/learn/paper-trading-vs-live-trading-a-data-backed-guide-on-when-to-start-trading-real-money)
- QuantConnect의 라이브 대사(reconciliation) 차트 기능, 예상 대비 실현 슬리피지 모니터링 도구에 관한 문서는 확보하지 못했다.
- Toss 모의투자 환경 제공 여부와 그 체결 규칙은 본 조사 범위 밖.

---

## 9. 자동매매 도구의 AI/LLM (2025~2026)

### Takeaway
2025~2026년의 실시장 벤치마크(StockBench, FINSABER, LiveTradeBench, Alpha Arena)는 일관되게 "범용 LLM 능력이 매매 수익으로 이어지지 않는다"고 보고하며, 업계 제품은 LLM을 코드 작성·전략 초안·설명 쪽에 배치하고 실행은 결정론적 엔진에 맡기는 방향으로 수렴하고 있다. 사용자의 "AI는 점수만, 주문은 안 함" 원칙은 이 흐름과 일치한다.

### Cited Findings

**프레임워크 내 ML/AI 기능**
- [원문 확인] FreqAI는 LLM이 아니라 전통적 예측 ML 자동화: "automate a variety of tasks associated with training a predictive machine learning model to generate market forecasts". 기능: 라이브 중 자기 적응 재학습("Self-adaptive retraining … in a supervised manner"), 재학습을 추론·매매와 별도 스레드에서 수행, 주기적 재학습을 모사하는 백테스트, 이상치 제거, 자동 정규화, NaN 정리, 크래시 복구용 모델 저장 — [freqai.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/freqai.md)
- [원문 확인] FreqAI 예제 전략에는 "Not for production" 위험 경고가 붙어 있음. 라벨은 "intentionally look into the future"(학습 목표)이므로 `lookahead-analysis`가 FreqAI 타깃을 편향으로 잘못 표시한다는 주의도 있음 — [freqai.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/freqai.md), [lookahead-analysis.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/lookahead-analysis.md)
- [원문 확인] NautilusTrader는 "AI training"(RL·진화전략 에이전트 학습용 고속 시뮬레이션)을 기능으로 명시 — [overview.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/overview.md)
- [원문 확인] Hummingbot Condor: "connects LLM-powered decision-making to **deterministic trade execution** via the Hummingbot API, controlled through Telegram or its web dashboard" — [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot)

**상용 플랫폼의 AI 보조**
- [검색 요약] QuantConnect "Mia"는 에이전트형 코딩 보조로, 알고리즘 코드를 쓰고 실행하고 오류를 고쳐 다시 실행하는 과정을 반복. Mia V2는 전략 아이디어 구상·코드 작성·백테스트 디버깅을 독립 수행한다고 발표(2025-11 공개 베타). 범위는 "research, backtesting, and paper trading" — [QuantConnect Mia 문서](https://www.quantconnect.com/docs/v2/ai-assistance/predefined-agents/mia), [QuantConnect 공지 'Your AI Quant Developer'](https://www.quantconnect.com/announcements/19846/your-ai-quant-developer/)
- [검색 요약] QuantConnect 자체 벤치마크 주장: Mia가 동작하는 QuantConnect 코드를 75% 사례에서 생성(OpenAI o3는 25%) — 회사 자체 수치로 독립 검증 없음 — [QuantConnect 공지](https://www.quantconnect.com/announcements/19846/your-ai-quant-developer/)
- [검색 요약] Composer "Trade with AI"(2025-10-21 출시): 자연어 프롬프트로 전략을 만들고 백테스트·실행 — [BusinessWire](https://www.businesswire.com/news/home/20251021050436/en/Composer-Supercharges-Investing-Platform-with-New-Trade-With-AI-Tool)
- [원문 확인] Lumibot은 2026년 README에서 "Build AI trading agents"를 전면에 내세우되, 의사결정 이후의 수량 산정·게이트·주문·기록("execution gap")을 프레임워크가 담당한다고 설명 — [Lumibot 'The Execution Gap'](https://lumibot.lumiwealth.com/execution_gap.html)

**연구 프레임워크**
- [검색 요약] TradingAgents(UCLA·MIT·Tauric Research, arXiv 2412.20138): 강세/약세 연구원 에이전트의 토론, 리스크 관리 팀, 트레이더 에이전트로 구성. 저자들은 누적수익·Sharpe·최대낙폭에서 기준 모델을 앞섰다고 주장. 향후 과제로 라이브 환경 배치를 언급(= 평가는 과거 데이터 기반) — [arXiv 2412.20138](https://arxiv.org/abs/2412.20138v6)
- [원문 확인] TradingAgents README 면책: "designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. It is not intended as financial, investment, or trading advice." — [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- [원문 확인] TradingAgents 2026년 릴리스 노트는 **시점 무결성 보강**이 연속됨: v0.2.3 "backtesting date fidelity"(2026-03), v0.5.0 "point-in-time integrity across every dated path"(2026-09), v0.5.2 "backtests that see only data published by each analysis date"(2026-09), v0.7.0 "backtests scored from the first close after each decision"(2026-10). README: "One run gives one decision, which cannot tell you whether the system decides well." — [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- [원문 확인] FinGPT: 금융 감성분석 모델(2023-08 공개), FinGPT-Forecaster(2023-11) 등 오픈소스 금융 LLM. 최신 커밋 2026-11-18 — [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT)

**효익/해악 증거**
- [검색 요약] StockBench(arXiv 2510.02209): 2025-03~07 다우존스 종목으로 LLM 에이전트의 수개월 일간 매매를 평가. 핵심 결론은 정적 금융 QA 고득점이 매매 성과를 신뢰성 있게 예측하지 못한다는 것 — [arXiv 2510.02209](https://arxiv.org/abs/2510.02209v1)
- [검색 요약] FINSABER(arXiv 2505.07078, "Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?"): 더 긴 기간·넓은 종목군으로 검증하면 LLM 타이밍 전략은 강세장에서 지나치게 보수적이어서 패시브에 뒤지고 약세장에서 지나치게 공격적이어서 큰 손실을 본다고 보고. 기존 연구들이 대개 1년 미만·10종목 미만으로 평가했다고 비판 — [arXiv 2505.07078](https://arxiv.org/html/2505.07078v3)
- [검색 요약] LiveTradeBench(arXiv 2511.03628): 21개 LLM을 50일간 실시간 평가, LMArena 고득점이 더 나은 매매 성과를 의미하지 않음 — [arXiv 2511.03628](https://www.arxiv.org/pdf/2511.03628)
- [검색 요약] Alpha Arena 시즌 1(nof1, 2025-10-18~11-03, 모델당 1만 달러로 Hyperliquid 크립토 무기한 선물을 사람 개입 없이 매매): 6개 모델 중 절반 넘게 손실. Qwen 3 Max가 약 22% 수익으로 1위, GPT-5는 약 3,733달러만 남겨 최하위. 과도한 매매 빈도와 나쁜 타이밍이 성과를 해쳤다는 분석 — [ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/), [GNcrypto](https://www.gncrypto.news/news/qwen-wins-alpha-arena-season-1-with-22-percent-returns/), [Decrypt](https://decrypt.co/345006/ai-crypto-trading-showdown-deepseek-grok-winning-gemini-implodes)
- [원문 확인, 단 2차 인용] Lumibot 문서가 인용하는 서베이 "Agentic Quantitative Trading"(arXiv 2608.31041, 2026-08): 이런 시스템은 "remain concentrated on signal discovery, while complete integration with portfolio construction, execution, and risk control is still uncommon", 그리고 강한 모델 능력이 "does not reliably translate into trading performance under live market conditions and reliability controls" — [Lumibot 'The Execution Gap'](https://lumibot.lumiwealth.com/execution_gap.html) (원 논문은 미열람)
- [원문 확인, 단 2차 인용] 같은 문서가 인용하는 2026년 오픈소스 DeFi 트레이딩 에이전트 20여 개 리뷰: 거의 모두에서 "nothing checks anything between 'model said yes' and 'transaction broadcasted'"가 공통 실패 양상이고, 두 번째로 큰 공백은 청산 로직 — [Lumibot 'The Execution Gap'](https://lumibot.lumiwealth.com/execution_gap.html)
- [원문 확인] 같은 문서: 에이전트형 AI 거버넌스 프레임워크(싱가포르 IMDA 2026-01, NIST 2026-02)가 공통으로 **identity, traceability, stoppability**를 요구한다고 정리(Lumibot은 준수를 주장하지 않음) — [Lumibot 'The Execution Gap'](https://lumibot.lumiwealth.com/execution_gap.html)
- [검색 요약] TradingAgents에 대해 Hugging Face 커뮤니티 댓글은 모델이 예측 대상 기간의 데이터로 사전학습되어 lookahead가 가중치에 내재한다는 우려를 제기(저자 측 결과가 아닌 커뮤니티 의견) — [Hugging Face papers 2412.20138](https://huggingface.co/papers/2412.20138)

### Inferences
- **LLM에 맡겨도 무리가 없는 역할**(증거와 제품 동향에 부합): ① 코드·전략 초안 작성과 디버깅(Mia), ② 거래 일지 자동 작성과 "왜 이 거래가 났는지" 설명(비전문가 UI에 적합), ③ 이상 징후 리뷰(로그·거래 패턴 요약 후 사람에게 질문), ④ 뉴스·공시의 구조화(이벤트 분류, 거래정지·관리종목 등 위험 플래그), ⑤ 보조 점수 — 단 결정론적 규칙이 낸 후보를 **걸러내는 방향(veto)** 으로만 쓰고 포지션 크기·주문을 직접 정하지 않게.
- **실패했거나 근거가 약한 역할**: LLM이 직접 매매 시점·방향을 결정하는 자율 매매(Alpha Arena, FINSABER, LiveTradeBench), 짧은 기간·소수 종목 백테스트로 성과를 주장하는 것(FINSABER의 비판), 사전학습 기간과 겹치는 백테스트(가중치 내재 lookahead).
- 사용자의 자기개선 루프에서 LLM 점수를 쓴다면 지켜야 할 것: (a) **점수의 시점 무결성** — 과거 데이터에 대해 지금의 LLM으로 점수를 재생성하면 모델이 이후를 "알고" 있을 수 있으므로, 실시간으로 기록된 점수만 학습·평가에 쓴다(TradingAgents가 2026년 내내 point-in-time 보강을 한 것과 같은 문제), (b) 프롬프트·모델 버전·입력·출력을 거래 기록과 함께 저장(traceability), (c) LLM 호출 실패·지연 시 기본 동작을 "진입 안 함"으로(stoppability/fail-closed), (d) LLM 점수의 유무에 따른 성과를 A/B로 계속 비교해 실제로 도움이 되는지 측정 — 도움이 안 되면 끄는 것을 기본값으로.
- FreqAI의 "주기적 재학습 + 재학습을 모사하는 백테스트"는 자기개선 루프의 가장 가까운 선행 사례다. 핵심은 **백테스트도 과거 시점마다 그때까지의 데이터로만 재학습**해야 한다는 것(그렇지 않으면 미래 데이터로 학습한 모델로 과거를 평가하게 된다).
- LLM의 비결정성(온도, 모델 교체)은 재현성을 깨므로, 점수 산출은 캐시하고 모델 버전을 고정하며, 모델이 바뀌면 "새 전략 버전"으로 취급해 페이퍼 단계부터 다시 거치게 한다.

### Gaps
- TradingView Pine Script AI 보조 기능의 출시 시점·기능은 확인하지 못했다(검색 예산 소진).
- LLM 뉴스 감성의 수익 예측력에 관한 학술 근거(예: Lopez-Lira & Tang "Can ChatGPT Forecast Stock Price Movements?")와 LLM 백테스트의 암기·lookahead 편향 연구(Glasserman 등)는 이번 세션에서 출처를 확보하지 못했다.
- 한국어 뉴스·공시에 대한 LLM 감성 점수의 실증 근거는 찾지 못했다.
- TradingAgents 논문의 백테스트 기간·종목(2차 블로그는 AAPL/GOOGL/AMZN이라 함)과 슬리피지 미반영 여부는 원문으로 확인하지 못했다.
- Composer·Mia 등 상용 AI 기능이 사용자 수익에 미친 영향에 대한 독립 평가는 없다(모두 자체 발표).
- Alpha Arena 수치는 크립토 매체 보도이며 17일짜리 단일 시즌이라 통계적 의미가 약하다.

---

## 10. 숙련 사용자들의 불만과 교훈 — 과최적화, 백테스트≠실거래, 복잡성

### Takeaway
프레임워크 문서 스스로가 가장 자주 경고하는 문제는 (1) lookahead로 부풀려진 백테스트, (2) 백테스트 가정(봉 내 순서·무슬리피지)과 실거래의 차이, (3) 설정이 여러 곳에서 덮어써져 생기는 불일치이며, 유지보수 중단(Backtrader, Blankly)과 유료화(vectorbt PRO)는 프레임워크 의존의 위험을 보여 준다. 교훈은 "기능을 더하기보다 가정을 드러내고 검증을 자동화하라"는 것이다.

### Cited Findings
- [원문 확인] lookahead는 "a common pain-point, which can cause huge differences between backtesting and dry/live run methods. Strategies that look into the future will perform well during backtesting, often with incredible profits or winrates, but will fail or perform badly in real conditions" — [strategy-customization.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/strategy-customization.md)
- [원문 확인] 온라인에서 구한 편향 전략은 편향을 제거하면 대개 쓸모없어짐: "Usually the bias in the strategy is THE driving factor for 'too good to be true' profits" — [lookahead-analysis.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/lookahead-analysis.md)
- [원문 확인] 설정 우선순위 혼선: `stoploss`, `max_open_trades`, `trailing_stop`이 설정 파일에 있으면 전략 값을 덮어써 hyperopt와 백테스트 결과가 달라짐 — [hyperopt.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/hyperopt.md)
- [원문 확인] 백테스트는 position stacking을 허용할 수 있지만 "Dry/live runs will **NOT** use position stacking"이라 같은 설정으로 검증해야 함 — [hyperopt.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/hyperopt.md)
- [원문 확인] `--timeframe-detail` 유무로 거래 순서가 크게 달라지는 "Extreme Difference Example"을 문서가 직접 제시(상세 타임프레임 없이는 캔들당 처음 `max_open_trades`개 신호만 평가되고 슬롯은 캔들 끝에야 해제) — [backtesting.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/backtesting.md)
- [원문 확인] 봇 밖에서의 수동 매매가 봇 상태를 깨뜨림: "Freqtrade assumes that the trades it opens are managed only though the bot" — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- [원문 확인] 거래 희소 종목은 "can cause problems with order-filling"이므로 피하라는 권고 — [faq.md](https://github.com/freqtrade/freqtrade/blob/develop/docs/faq.md)
- [원문 확인] NautilusTrader 기본 FillModel은 `prob_slippage=0.0`·`prob_fill_on_limit=1.0`로 낙관적이며, 과거 호가창은 체결 후에도 불변이라 `liquidity_consumption=False`면 같은 표시 물량이 여러 모의 주문을 받쳐 줄 수 있다고 경고 — [fill-models.md](https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-models.md)
- [원문 확인] Lumibot은 2026-06에 자체 백테스트 엔진에서 lookahead 체결·forward-fill된 가짜 봉 체결 문제를 발견해 수정하고 회귀 테스트를 추가 — [Lumibot 저장소 docs/investigations](https://github.com/Lumiwealth/lumibot)
- [검색 요약] QuantConnect는 시간봉·일봉에서 오래된 가격으로 체결되던 허점을 최근에야 막았다 — [QuantConnect 공지](https://www.quantconnect.com/announcements/20949/closing-the-stale-price-loophole-on-daily-and-hourly-data/)
- [검색 요약] QuantConnect AI 보조의 사용량 제한에 대한 불만(Bronze 등급에서 질문 25개는 너무 적다는 포럼 글) — [QuantConnect Mia 문서/포럼](https://www.quantconnect.com/docs/v2/ai-assistance/predefined-agents/mia)
- [원문 확인] 유지보수 중단: Backtrader 2023-04 이후 커밋 없음, Blankly 2024-12 이후 없음 — [mementum/backtrader](https://github.com/mementum/backtrader), [blankly-finance/blankly](https://github.com/blankly-finance/blankly)
- [검색 요약] 단순 hold-out 검증은 투자 백테스트에서 신뢰하기 어렵다는 PBO 논문의 주장 — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)

### Inferences
- 성숙한 프레임워크조차 2026년에 lookahead 체결·stale 가격 체결 버그를 고치고 있다(Lumibot, QuantConnect). 직접 만든 백테스터에는 같은 종류의 버그가 있을 가능성이 높다고 가정하고, **체결 불변식을 테스트로 고정**해야 한다: "체결 시각 ≥ 신호 봉 종료 시각", "체결가는 체결 시각 봉의 고·저 범위 안", "거래량 0 봉에서는 체결 없음", "forward-fill된 봉에서는 체결 없음".
- 설정 단일 출처 원칙: 백테스트·페이퍼·실거래가 **같은 설정 객체**를 쓰고, 각 실행 결과에 사용된 설정 전체의 스냅샷(해시)을 저장한다. Freqtrade의 설정/전략 덮어쓰기 혼선은 설정 출처가 둘 이상일 때 반드시 생기는 문제다.
- 비전문가용 UI에서 과최적화를 막는 실용적 방법: 최적화 버튼 옆에 시도 횟수·표본 외 성과·거래 수를 강제로 함께 표시하고, 표본 내 성과만 좋은 결과는 색으로 경고한다. "최고 수익 파라미터 자동 적용" 기능은 제공하지 않는 편이 낫다.
- 복잡성에 대한 교훈: Freqtrade는 콜백 수십 개, Nautilus는 엔진 다수로 학습 비용이 크다. 단일 전략·단일 사용자 도구는 **기능 수가 아니라 가정의 투명성**(체결 규칙, 비용 모델, 봉 내 순서 규칙을 리포트 첫 화면에 명시)으로 차별화하는 것이 합리적이다.
- 봇과 수동 매매를 같은 계좌에서 섞으면 상태가 깨진다(Freqtrade FAQ). 토스 앱에서의 수동 매매와 도구의 포지션 인식을 어떻게 구분할지(전용 계좌 권장, 또는 외부 변경 감지 시 정지)를 실거래 전에 정해야 한다.

### Gaps
- 사용자 불만의 빈도·규모를 보여 주는 정량 자료(GitHub 이슈 통계, 포럼·Reddit 설문)는 확보하지 못했다. 이 절의 근거는 대부분 프레임워크 문서 스스로의 경고문이다.
- MetaTrader EA, NinjaTrader, TradeStation 사용자들의 전형적 불만(틱 데이터 품질, 최적화 과적합 등)은 조사하지 못했다.
- QuantConnect 클라우드 비용·데이터 제약에 대한 사용자 평가(Trustpilot 등)는 검색 결과 목록에만 있었고 내용은 확인하지 못했다.
