# 단기(장중~수일) 주식 매매 전략의 비용 차감 후 수익성 증거와 개인 데이트레이더 성과 기저율 (2026-11 기준)

> 조사 방법상의 한계(먼저 읽을 것): 이 세션에서는 원문 열람(WebFetch)이 네트워크 허용 목록 문제로 실패했고(nber.org, arxiv.org, koasas.kaist.ac.kr, scholarworks.bwise.kr 모두 DNS 해석 실패), 웹 검색 예산도 중간에 소진되었다. 따라서 아래 수치는 대부분 **논문 초록·저장소 서지 페이지·2차 요약에 대한 검색 결과**에 근거한다. 원문 표를 직접 확인하지 못한 수치는 "(2차 요약)" 또는 "(초록 기준)"으로 표시했다. 기억에만 의존하는 수치는 본문 Cited Findings에 넣지 않고 각 절의 Gaps에 "미검증"으로 적었다.
> 용어: "총(gross)" = 비용 차감 전, "순(net)" = 비용 차감 후. "롱숏" = 공매도가 포함된 포트폴리오(대상 제품은 롱온리이므로 그대로 쓸 수 없음).

## 1. 단기 반전(short-term reversal): 총 엣지는 얼마나 크고, 비용을 빼면 얼마나 남는가

### Takeaway
단기 반전은 실재하는 현상이지만, 학계의 주된 해석은 "유동성 공급(체결을 받아주는 쪽)에 대한 보상"이다. 따라서 시장가로 들어가 스프레드와 세금을 내는 개인(유동성 수요자)에게는 총 엣지의 대부분이 비용으로 사라지고, 순수익이 남았다는 증거는 대형주·저회전·기관급 체결 조건에 한정된다.

### Cited Findings
- Lehmann (1990, QJE, 미국 주식 주간 수익률): 직전 주 "패자"는 다음 주 평균 약 +0.86~1.24%/주, 직전 주 "승자"는 약 −0.35~−0.55%/주(총수익, Table II에 대한 Alpha Architect 2차 요약). 논문 초록은 이 반전이 얇은 거래·매수매도 호가·그럴듯한 거래비용을 보정해도 남는다고 주장 — [NBER w2533](https://www.nber.org/papers/w2533), [Alpha Architect 요약](https://alphaarchitect.com/quantitative-momentum-research-short-term-return-reversal/)
- Avramov, Chordia & Goyal (2006, JF, 미국 개별주): 단기 반전은 비유동성과 강하게 연결되고, 가장 큰 반전과 역추세 수익은 "고회전·저유동성" 종목에서 발생한다. 그러나 **역추세 전략 수익은 예상 거래비용보다 작다**고 결론(초록 기준) — [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:61:y:2006:i:5:p:2365-2394)
- de Groot, Huij & Zhou (2012, JBF, 미국, 1990–2009): 거래비용 타격의 대부분은 소형주 과다 매매에서 온다. 대형주로 유니버스를 제한하고 회전율 제한 규칙을 쓰면 **순 30–50bp/주**의 반전 수익이 남는다고 보고(롱숏, 기관 체결 비용 모형). CXO Advisory는 비용 모형이 약 100만 달러 규모 거래를 가정하므로 개인에게 그대로 적용되지 않을 수 있다고 지적 — [EconPapers](https://econpapers.repec.org/RePEc:eee:jbfina:v:36:y:2012:i:2:p:371-382), [CXO Advisory](https://www.cxoadvisory.com/?p=6251)
- Nagel (2012, RFS, "Evaporating Liquidity", 미국): 단기 반전 전략 수익은 유동성 공급 수익의 대리변수이며, 기대수익이 시간에 따라 크게 변하고 **VIX로 강하게 예측**된다. 금융시장 혼란기(2007–09)에 기대수익과 조건부 샤프비율이 크게 상승. 평균적으로 수익이 거의 없는 산업 포트폴리오 반전도 VIX가 높을 때는 강한 수익(초록 기준) — [NBER w17653](https://www.nber.org/papers/w17653), [RFS 서지](https://econpapers.repec.org/RePEc:oup:rfinst:v:25:y:2012:i:7:p:2005-2039)
- Hendershott & Menkveld (2014, JFE, NYSE 중개인(스페셜리스트) 일별 자료 12년): 가격 압력(일시적 가격 왜곡)은 평균 0.49%, **반감기 0.92일**. 10만 달러 재고 충격당 평균 0.28%의 가격 압력, 소형주에서 훨씬 큼 — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:114:y:2014:i:3:p:405-423), [NBER 초안](https://projects.nber.org/confer/2009/MMf09/Hendershott_Menkveld.pdf)
- Da, Liu & Schaumburg (2014, Management Science, 미국): 애널리스트 추정치 수정으로 현금흐름 뉴스를 제거한 "강화된" 반전 전략은 표준 반전 대비 위험조정수익이 약 4배. 반전은 **롱 측에서는 유동성 충격**, 숏 측에서는 투자심리(공매도 제약)에 기인 — [NY Fed Staff Report 513](https://www.newyorkfed.org/research/staff_reports/sr513.html), [EconPapers](https://econpapers.repec.org/RePEc:inm:ormnsc:v:60:y:2014:i:3:p:658-674)
- Dai, Medhat, Novy-Marx & Rizova (2024, FAJ; NBER w30917, 미국): 표준 반전이 약해 보이는 이유는 신호가 뉴스 효과(실적발표 후 표류, 단기 산업 모멘텀)에 오염되기 때문. 실적발표 조정·산업 대비 반전으로 정제하면 유동성 공급 수익이 선명해진다. **변동성이 높을수록 반전이 강하고 초기에 빠르며**, 회전율이 낮을수록 반전이 오래 지속된다. 고변동·고회전 종목에서는 가장 최근 수익률만 정보가 있고 반전은 길어야 몇 주 — [NBER w30917](https://www.nber.org/papers/w30917), [FAJ](https://rpc.cfainstitute.org/research/financial-analysts-journal/2024/reversals-and-the-returns-to-liquidity-provision), [Alpha Architect](https://alphaarchitect.com/how-volatility-and-turnover-affect-return-reversals/)
- Barrot, Kaniel & Sraer (2016, JFE, 프랑스 개인투자자 2002–2010): 개인이 산 종목 롱·판 종목 숏의 주간 리밸런싱 포트폴리오는 4요인 모형 대비 연 19% 초과수익, 불확실성이 높은 시기에는 최대 연 40%. 그러나 **개별 개인투자자는 이 보상을 얻지 못한다** — 매매 당일 음(−)의 수익을 겪고, 유동성 공급 초과수익이 사라진 한참 뒤에야 포지션을 되돌리기 때문 — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:120:y:2016:i:1:p:146-168)

### Inferences
- "퍼들" 전략(급락 후 반등 매수)은 구조상 유동성 공급 전략과 같은 방향이지만, **다음 봉 시장가 진입**은 유동성을 공급하는 것이 아니라 소비하는 것이다. 문헌에서 반전 수익을 버는 주체(시장조성자, 지정가로 받아주는 쪽)와 비용 구조가 다르다.
- Barrot 등의 결과는 제품 설계에 직접적인 시사점이 있다: 개인의 역추세 매수는 "방향"은 맞지만 "진입 당일 손실 + 너무 늦은 청산"으로 보상을 놓친다. 짧은 시간 제한 청산은 문헌과 부합하는 설계이나, 진입 직후의 불리한 체결가가 핵심 누수 지점이다.
- 반전의 가격 압력 규모(일별 기준 평균 0.49%, 반감기 약 1일)와 왕복 비용 0.2–0.3%를 비교하면, 대형 유동주에서 평균적인 급락 한 번이 주는 총 엣지는 비용과 같은 자릿수다. 평균이 아니라 **조건부로 큰 사건**(고변동성 국면, 무뉴스 급락)만 골라야 산술이 맞는다.
- 롱 측 반전이 유동성 충격에서 온다는 Da 등의 결과는 롱온리 설계에 우호적인 유일한 구조적 근거다(숏 측은 공매도 제약 때문이라 롱온리로는 어차피 못 얻는다).

### Gaps
- Jegadeesh (1990)의 월간 반전 수치(기억상 십분위 스프레드 약 2.49%/월, 1934–1987)와 Lo & MacKinlay (1990)의 역추세 수익 분해(교차 자기상관 기여)는 이번 검색에서 원문·초록으로 확인하지 못했다. 미검증.
- Nagel (2012)의 정확한 효과 크기(일별 반전 수익률 %, VIX 1포인트당 기대수익 증가, 호가 중간값 수익률 사용 시 수익 감소폭)는 원문 접근 실패로 확인하지 못했다.
- de Groot 등의 "순 30–50bp/주"가 대형주 표본 한정 수치인지 전체 결론 수치인지는 초록만으로 구분되지 않는다.
- 위 연구는 모두 일별~주별 주기이며 미국·프랑스 자료다. 1–60분 주기의 순수익 증거는 3절 참조(매우 얇다).

## 2. 장중 특화 증거: 어떤 전략이 표본 외(out-of-sample) 지지를 받는가

### Takeaway
표본 외·교차시장 재현이 가장 탄탄한 것은 "시장 지수 수준의 장중 모멘텀"(초반/장중 수익률이 마지막 30분을 예측)이고, 개별 종목 수준에서는 반대로 "아주 짧은 시차의 반전(1시간 미만 유동성 불균형)"과 "마감 30분의 횡단면 반전"이 보고된다. Zarattini·Aziz 계열 ORB/장중 모멘텀 논문은 수익률이 크지만 동료심사 전 워킹페이퍼이고, 비용·슬리피지 가정에 민감하다는 비공식 재현 결과가 있다.

### Cited Findings
- Heston, Korajczyk & Sadka (2010, JF, 미국): 하루를 13개 30분 구간으로 나눠 횡단면 회귀. **정확히 거래일 배수 시차의 같은 30분 구간에서 수익률 지속**(최소 40거래일), 개장·마감 30분에서 가장 강함. 반면 짧은 시차에서는 반전이 나타나며, 이는 **1시간 미만 지속되는 일시적 유동성 불균형과 호가 바운스**에 기인. 5분 단위 강건성 검증에서도 처음 몇 개 시차의 반전이 가장 뚜렷. 거래량·주문불균형·변동성·스프레드도 비슷한 패턴이지만 수익률 패턴을 설명하지는 못함 — [arXiv 1005.3535](https://arxiv.org/abs/1005.3535), [JF 서지](https://econpapers.repec.org/RePEc:bla:jfinan:v:65:y:2010:i:4:p:1369-1407)
- Gao, Han, Li & Zhou (2018, JFE, 미국 S&P 500 ETF, 1993–2013): 전일 종가 대비 첫 30분 수익률이 마지막 30분 수익률을 예측. 워킹페이퍼 기준 표본 외 R² 1.2% — [JFE 서지](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414), [Alpha Architect](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/)
- Baltussen, Da, Lammers & Martens (2021, JFE): 주식·채권·원자재·통화 60여 개 선물, 1974–2020. 마감 전 마지막 30분 수익률이 그날 나머지 수익률로 양(+)의 예측 — "어디서나 강한 시장 장중 모멘텀". 옵션 시장조성자·레버리지 ETF의 감마 헤지 수요와 연결되며, 예측력은 이후 며칠에 걸쳐 되돌려짐 — [JFE 서지](https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:1:p:377-403)
- 교차국가 확장: 검색 요약에 따르면 16개 시장 중 12개에서 첫 30분→마지막 30분 예측력이 유의하고 표본 외 예측력도 유의했다는 연구가 있음(저자 표기는 검색 요약상 Li·Sakkas, 원문 미확인) — [Hull 저장소](https://hull-repository.worktribe.com/OutputFile/3016448), [Nottingham 저장소](https://nottingham-repository.worktribe.com/OutputFile/5273196)
- 실무 재구현(약한 증거): QuantConnect의 Gao 등 전략 재현은 자체 검증 기간에 논문보다 낮은 수익과 낮은 샤프비율을 보고 — [QuantConnect](https://www.quantconnect.com/learning/articles/investment-strategy-library/intraday-etf-momentum)
- "End-of-Day Reversal" (Da 등, 2025-04 워킹페이퍼): **개별 종목은 마감 전 마지막 30분에 횡단면에서 급격한 장중 수익률 반전**을 보이며, 이는 시장 수준 장중 모멘텀과 별개이고 유동성·감마 헤지 효과로 설명되지 않는다고 주장(초록 기준, 저자 목록 미확인) — [nd.edu EOD.pdf](https://www3.nd.edu/~zda/EOD.pdf)
- Lou, Polk & Skouras (2019, JFE, 미국): 모멘텀 이익은 거의 전부 야간에 발생(야간 3요인 알파 0.95% 유의 vs 장중 0.11% 비유의, 2차 요약). 반면 연구한 14개 전략 중 9개는 프리미엄 전부를 장중에 얻음. 야간·장중 수익 성분은 서로 다른 투자자 집단의 수요를 반영 — [LSE 원고](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf), [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/)
- Bogousslavsky (2021, JFE, 미국): 미스프라이싱 팩터는 장중 내내 양의 수익을 내지만 **장 마감 무렵에는 부진**. 야간 증거금·대차 수수료 때문에 차익거래자가 마감 전 포지션을 줄이는 것이 원인. 학위논문 버전은 소형·비유동 종목이 마지막 30분에 높은 평균수익을 보인다고 보고 — [IDEAS](https://ideas.repec.org/a/eee/jfinec/v141y2021i1p172-194.html)
- Zarattini, Aziz & Barbon (2024 초판, 2025-02 개정; Swiss Finance Institute RP 24-97, SPY 2007-05~2024-04): 변동성 기반 경계 + VWAP 추적 손절을 쓰는 장중 모멘텀. 순 연 19.6%, 샤프 1.33, 최대낙폭 −25%, 누적 1,985%(저자 측 비용 가정). 동료심사 학술지 게재 아님(Quantpedia Awards 2025 4위) — [SFI](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy), [Concretum(저자 소속)](https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/), [CXO Advisory](https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/)
- Zarattini & Aziz (2023, SSRN 4416622, QQQ 5분 ORB, 2016-01~2023-02): CAGR 33.2% vs 매수후보유 14.9%, 1,795회 거래, **슬리피지 0 가정**(CXO 요약) — [SSRN](https://papers.ssrn.com/abstract=4416622), [CXO Advisory](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy)
- ORB 비판적 재현(약한 증거, 블로그): 동일 논문을 5개 지수 CFD(NQ, SPX, Dow, DAX, FTSE), 2015–2026에 적용한 MQL5 블로그 글의 결론은 "총수익은 재현되지만 순수익은 0" — [MQL5 블로그](https://www.mql5.com/en/blogs/post/776235)
- Zarattini, Barbon & Aziz (2024, "A Profitable Day Trading Strategy For The U.S. Equity Market", 미국 7,000여 종목, 2016–2023): 뉴스 등으로 거래가 비정상적으로 몰린 "Stocks in Play"(개장가 5달러 초과, 14일 평균 거래량 100만 주 이상, 개장 구간 상대거래량 상위 20)에 5분 ORB 적용 시 순 누적 1,637%, 샤프 2.81(vs 0.78), 연 알파 36%(수수료 차감, 초기자금 2.5만 달러). QuantConnect 재현은 ATR 필터 설정에 따라 샤프 1.5–2.7 — [Concretum](https://concretumgroup.com/a-profitable-day-trading-strategy-for-the-u-s-equity-market/), [QuantConnect 재현](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/), [RePEc](https://ideas.repec.org/p/chf/rpseri/rp2498.html)

### Inferences
- 문헌의 구도는 "**지수 수준 = 장중 모멘텀, 개별 종목 수준 = 초단기 반전**"이다. 퍼들 전략이 개별 종목의 특이적(idiosyncratic) 급락을 노린다면 반전 문헌 쪽에, 시장 전체가 빠지는 날의 급락을 노린다면 모멘텀 문헌(그날 방향이 마감까지 이어짐)에 걸린다. 즉 **시장 전체가 하락 추세인 날의 종목 급락을 사는 것은 지수 장중 모멘텀 증거와 반대 방향**이다.
- 개별 종목 뉴스 급변(Stocks in Play)에서는 돌파 추종이 높은 수익을 보였다는 결과는, 뉴스·거래량 급증 동반 급락을 "되돌림"으로 매수하는 것이 위험하다는 3절의 결론과 같은 방향이다.
- HKS의 "1시간 미만 유동성 불균형" 반전은 호가 바운스가 섞인 결과다. 체결가 기반 1분봉으로 측정한 반등은 실제로 살 수 있는 가격(매도 호가)으로 환산하면 줄어든다.
- 마감 30분의 개별 종목 반전(2025 워킹페이퍼)은 "시간대 필터" 후보이지만 아직 동료심사 전이고 미국 자료다.

### Gaps
- VWAP 회귀(Zarattini & Aziz의 VWAP 논문 포함)와 갭 페이드(예: Berkman, Koch, Tuttle & Zhang 2012의 야간 수익률-장중 반전) 관련 수치는 검색 예산 소진으로 확인하지 못했다. 신뢰할 만한 출처 미확보.
- Zarattini 계열 논문의 레버리지 사용 여부·정확한 수수료 가정은 원문 미확인(기억상 ORB 논문은 레버리지와 주당 소액 수수료를 가정하나 미검증). 한국의 0.20% 매도세 환경으로 환산한 결과는 존재하지 않는다.
- HKS의 표본 기간·종목 수, Gao 등의 경제적 유의성(시장 타이밍 전략 연 수익률)은 원문 미확인.
- 한국 시장에서의 지수 장중 모멘텀 재현 여부는 4절 참조(직접 증거 미확보).

## 3. "장중 급락 매수/과잉반응" (1–60분 주기) 직접 증거와 승률을 높이는 필터

### Takeaway
분 단위 급락 후 반등은 통계적으로 유의하게 관측되지만, 시장에 따라 스프레드 확대가 이익 대부분을 흡수한다. 필터로서 문헌 지지가 가장 일관된 것은 "뉴스 없는 급락만 사고, 뉴스·정보 동반 급락은 피한다"이며, 거래량은 정보 비대칭이 큰 종목에서는 오히려 지속 신호가 된다.

### Cited Findings
- Zawadowski, Andor & Kertész (2006, Quantitative Finance; arXiv cond-mat/0406696, NYSE·NASDAQ 유동 종목 분 단위 자료): 장중 극단적 가격 하락과 상승 **모두 이후 유의한 반전**. 변동성·거래량·(NYSE의 경우) 스프레드가 사건 시점에 급증하고 며칠간 높게 유지, 변동성 감쇠는 멱법칙(오모리 법칙). **NYSE에서는 스프레드 급확대가 역추세 전략 이익의 대부분을 흡수**하고, NASDAQ에서는 스프레드가 거의 일정해 단기 초과이익이 유의. 표본은 직전 60일간 거래 분의 90% 이상에서 체결이 있고 주가 10달러 초과인 종목 — [arXiv](https://arxiv.org/abs/cond-mat/0406696), [Quantitative Finance 서지](https://ideas.repec.org/a/taf/quantf/v6y2006i4p283-295.html)
- Chan (2003, JFE, 미국): 공개 뉴스가 동반되지 않은 극단적 가격 변동 뒤에는 반전의 증거가 "일부" 있고, **악재 뉴스 뒤에는 강한 표류(지속)**. 두 패턴 모두 주로 소형·비유동 종목에서 나타남(월 단위 연구) — [JFE 서지](https://econpapers.repec.org/RePEc:eee:jfinec:v:70:y:2003:i:2:p:223-260)
- Tetlock (2010, RFS, 미국, Dow Jones 뉴스 아카이브): 뉴스일 수익률은 이후 수익률을 양(+)으로 예측(지속)하고, 고거래량 뉴스일일수록 더 강함. 거래량 유발 반전은 뉴스가 없는 날에 발생(초록·초안 기준, 일별 연구) — [RFS 서지](https://econpapers.repec.org/RePEc:oup:rfinst:v:23:y:2010:i:9:p:3520-3557), [NBER 초안](https://projects.nber.org/confer/2009/MMf09/Tetlock.pdf)
- Savor (2012, JFE, 미국): 큰 가격 충격 중 애널리스트 리포트가 동반된(정보 기반) 것은 이후 표류, 정보 없는 충격은 반전 경향. 정보 기반 충격은 미래 실적 서프라이즈와 더 강하게 상관(일별 연구) — [IDEAS](https://ideas.repec.org/a/eee/jfinec/v106y2012i3p635-659.html)
- Llorente, Michaely, Saar & Wang (2002, RFS, NYSE·AMEX 일별): 위험분담(헤지) 목적 거래가 만든 수익률은 반전하고, 투기적(정보) 거래가 만든 수익률은 지속. 거래량과 수익률 자기상관의 관계는 종목별 정보거래 정도에 따라 횡단면으로 달라짐 — [NBER w8312](https://www.nber.org/papers/w8312)
- Avramov, Chordia & Goyal (2006): 가장 큰 반전은 고회전·저유동성 종목에서 발생하지만 비용을 넘지 못함(1절과 동일) — [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:61:y:2006:i:5:p:2365-2394)
- Nagel (2012): 반전 기대수익은 VIX가 높을 때 크게 상승(1절과 동일) — [NBER w17653](https://www.nber.org/papers/w17653)
- Aït-Sahalia, Fan, Xue & Zhou (2022 NBER w30366, Management Science 게재): 고빈도 수익률 예측 가능성은 초단기 주기에서 체계적으로 존재하지만, 데이터 적시성(밀리초 단위)에 따라 예측력이 달라지며 논문은 "밀리초당 가치"를 계량 — [NBER w30366](https://www.nber.org/papers/w30366)

### Inferences
- 문헌이 지지하는 필터 우선순위(모두 일별 연구를 분 단위로 외삽한 것이므로 가설로 취급해야 함):
  1. **뉴스/공시 필터**: 급락 직전·당일에 종목 뉴스나 공시(실적, 유상증자, 거래정지 사유 등)가 있으면 진입 금지. 뉴스 없는 급락만 대상.
  2. **시장 대비 특이성**: 지수·섹터가 같이 빠지는 급락(시장 전체 요인)은 지수 장중 모멘텀 증거상 지속 가능성이 있어, 종목 수익률에서 지수 수익률을 뺀 "특이적 급락"만 대상.
  3. **변동성 국면**: 시장 변동성(VKOSPI 등)이 높은 날은 반전 보상이 커지는 대신 스프레드·슬리피지도 커지므로, 유동성이 깊은 대형주/ETF에 한정.
  4. **거래량 해석 주의**: 대형주에서 뉴스 없는 고거래량 급락은 유동성 충격(반전) 쪽이지만, 소형·정보 비대칭이 큰 종목의 고거래량 급락은 정보거래(지속) 쪽일 가능성이 높다.
- Zawadowski 등의 결과는 퍼들 전략의 가장 직접적인 선행 증거이자 경고다: "반등은 있다. 다만 사건 직후 스프레드가 벌어지는 시장에서는 못 먹는다." 한국 종목에서 급락 직후 1–3분의 실제 스프레드(호가 단위 대비)를 페이퍼 트레이딩 로그로 반드시 측정해야 한다.
- 1분봉 REST 폴링 + 다음 봉 시장가 진입은 지연이 1–2분 수준이다. 초단기 예측력이 밀리초 단위 속도에 좌우된다는 증거를 감안하면, 순수 미시구조 신호(수초~수십 초에 소멸)는 이 구조로 잡을 수 없고, **수십 분~수 시간 지속되는 느린 반전**만이 현실적 대상이다.

### Gaps
- Zawadowski 등의 구체적 수치(급락 임계값, 평균 반등 크기 %, 표본 기간)는 원문 접근 실패로 미확인. 표본이 2000년대 초 미국이라 현재 한국 시장에 그대로 적용할 수 없다.
- Campbell, Grossman & Wang (1993)의 "고거래량일 후 반전이 더 강하다"는 결과는 이번 검색에서 출처를 확보하지 못했다(기억상 미국 지수·대형주 일별 자료). 미검증.
- "약 10분간 1–2% 하락 후 반등 신호 시 매수"와 동일한 규칙을 비용 차감 후 검증한 동료심사 연구는 **찾지 못했다**. 이 규칙의 직접 증거는 사실상 없으며, 자체 페이퍼 트레이딩 데이터가 유일한 검증 수단이다.
- 뉴스/무뉴스 구분 연구는 모두 일~월 단위이며 장중 분 단위에서 같은 비대칭이 성립하는지는 직접 확인되지 않았다.

## 4. 한국 및 아시아 시장 증거 (KOSPI/KOSDAQ 장중 반전·모멘텀, 가격제한·VI, 개인 주도 종목)

### Takeaway
한국에서는 "개장 방향의 과잉반응 후 장중 반전"(특히 미국장 영향 → 시가 과잉반응)과 마감 무렵 개별주 반전이 보고되어 있고, 개인의 역추세 매매가 그 배경으로 지목된다. 다만 KOSDAQ 급락 후 분 단위 반전을 비용 차감 후 검증한 연구는 찾지 못했고, VI는 평상시 가격 안정에는 효과적이나 직전에 크게 과열·과매도된 경우에는 균형가격 회복 효과가 제한적이다.

### Cited Findings
- KAIST 석사논문 "한국 주식시장의 일중 반전 현상: KOSPI를 중심으로" (2021, KOSPI 809종목 고빈도 자료, 2011–2020): 해외 연구와 달리 **개장 후 첫 30분 수익률의 모멘텀은 발견되지 않고**, 마감 전 1시간 30분~30분 구간에서 반전이 나타남(검색 요약 기준, 원문 미확인) — [KAIST KOASAS](https://koasas.kaist.ac.kr/handle/10203/294938)
- KOSPI 200 선물: 미국 시장 수익률이 한국 시장의 장중(시가→종가) 수익률과 음(−)의 상관. 저자들은 시장 비중이 큰 **개인투자자의 역추세 매매**를 원인으로 지목. KOSPI 200 선물은 2000–2009년에 S&P 500 수익률에 과잉반응했고, 2009년 야간선물 도입 이후 과잉반응이 사라졌다는 결과도 보고됨(검색 요약 기준) — [Durham 저장소](https://durham-repository.worktribe.com/OutputFile/1402814), [Durham DRO](https://dro.dur.ac.uk/15895)
- 미국발 야간 뉴스에 대한 과잉반응으로 KOSPI 200 선물에 시가→종가 유의한 가격 반전이 발생한다는 국내 연구(검색 요약 기준) — [KoreaScience](https://koreascience.kr/article/JAKO201006755715664.page)
- 한국 지수 ETF: 야간 수익률은 유의하게 양(+), 이어지는 장중 수익률은 음(−). 저자들은 주목 효과보다 공매도 제약(의견 불일치 가설)으로 설명(프리프린트) — [Preprints.org](https://www.preprints.org/manuscript/201905.0306)
- 일별 대규모 가격변동(±10% 이상) 후 반전: KOSPI 유통업종 종목(2004–2022)에서 **반전은 일관되게 나타나지 않았음** — [KoreaScience](https://www.koreascience.or.kr/article/JAKO202326343293687.pdf)
- 변동성완화장치(VI) 제도: 동적 VI는 직전 체결가 대비 ±3~6%, 정적 VI는 직전 단일가 대비 ±10% 이상 변동 시 발동, 2분간 단일가 매매 전환 — [뉴시스](https://www.newsis.com/view/NISX20220519_0001878246)
- Eom, Kwon, La & Park (2022, Journal of Risk and Financial Management, 한국): **동적 VI는 가격 안정과 가격발견에 효과적**, 정적 VI 효과는 제한적(기존 가격제한폭과 기능 중복). 안정화는 연속된 두 가격변화의 "반전" 여부에 대한 이항 검정으로 측정. 동적 VI의 안정화 효과는 종가 단일가보다 접속매매 중에 유의하게 큼 — [MDPI JRFM 15(3):105](https://mdpi.com/1911-8074/15/3/105), [Berkeley CDAR 워킹페이퍼](https://cdar.berkeley.edu/sites/default/files/Kwon-Eom-La-Park-VIs-March-1-2018.pdf)
- 같은 저자군의 별도 연구: 동적 VI 발동 직전에 주가가 현저한 수준으로 오버슈팅한 경우, 발동 직후 균형가격 형성 효과는 제한적(검색 요약 기준) — [CORE](https://core.ac.uk/download/512003943.pdf)
- 반대 증거: 주가가 정적 상·하한에 닿을 때 조건부 고유변동성이 오히려 증가(Shin, Naka & Alsunbul 2023) — [Emerald IJOEM](https://www.emeraldinsight.com/insight/content/doi/10.1108/IJOEM-08-2020-0877/full/html)
- 2026년 상반기 VI 발동은 총 29,357건으로 반기 기준 역대 최대 — [SBS Biz](https://biz.sbs.co.kr/amp/article/20000320692)
- 자본시장연구원 "국내 주식시장의 투자자별 매매행태와 주가 움직임" (2026-10-26): 개인은 **주가가 하락한 종목을 매수하는 역추세 성향이 뚜렷**, 기관은 추세 추종. 외국인은 유가증권시장에서는 추세 추종이나 코스닥에서는 비일관. 순매수 이후 성과는 개인이 전반적으로 시장 수익률에 미달, 기관·외국인은 보유기간이 길수록 상대적으로 양호(요약 기준, 세부 수치 미확인) — [KDI 경제정보센터](https://eiec.kdi.re.kr/policy/domesticView.do?ac=0000207901)
- 같은 주제의 상충 결과: 2024년 학술연구는 KOSPI에서 개인 순매수 강도 기반 포트폴리오가 특정 조건에서 양호한 성과를 보였다고 보고. 분석 대상·산출 기간·수익률 계산 방식이 달라 직접 비교는 어렵다는 보도 — [톱스타뉴스](https://www.topstarnews.net/news/articleView.html?idxno=16253648)

### Inferences
- 한국 시장은 개인 비중이 높고 개인이 이미 구조적으로 "하락 종목 매수"를 하고 있다. 퍼들 전략은 **가장 붐비는 거래의 자동화**이며, 개인 순매수 종목의 사후 성과가 시장에 미달한다는 KCMI 결과는 기저율 측면에서 불리한 신호다.
- 동적 VI 발동 임계(±3~6%)는 퍼들 진입 조건(10분간 1–2% 하락)보다 훨씬 크다. 따라서 진입 후 추가 급락으로 VI가 걸리면 2분 단일가 동안 손절(0.5%)이 실행되지 못하고 갭으로 체결될 수 있다 — 손절폭이 보장되지 않는 꼬리 위험.
- 2026년은 VI 발동이 역대 최대인 고변동성 국면이다. Nagel 논리로는 반전 보상이 커지는 환경이지만, 같은 이유로 스프레드 확대·손절 미끄러짐도 커지므로 페이퍼 트레이딩 결과를 평시로 외삽하면 안 된다.
- KAIST 논문의 "개장 30분 모멘텀 없음, 마감 구간 반전"이 맞다면, 한국 개별주에서는 미국식 ORB 추종보다 오후 구간 반전 쪽이 상대적으로 가능성이 있다(단일 석사논문이므로 약한 증거).

### Gaps
- KOSDAQ 종목의 분 단위 급락 후 반전을 직접 다룬 연구, 그리고 거래세·스프레드 차감 후 수익성을 검증한 한국 틱데이터 연구는 **찾지 못했다**.
- 한국 지수(KOSPI200 ETF 등)에서 Gao 등 방식 장중 모멘텀이 재현되는지에 대한 연구는 검색 예산 소진으로 확인하지 못했다.
- 중국·대만·일본 등 다른 아시아 시장의 장중 반전/모멘텀 연구는 이번 조사에서 다루지 못했다.
- 한국거래소 호가가격단위(2023년 개편)와 가격대별 상대 호가단위(%)는 검색 예산 소진으로 출처를 확보하지 못했다. 저가주에서 1틱이 TP/SL 대비 얼마나 큰지는 별도 확인 필요.
- KCMI 2026-10 보고서의 보유기간별 초과수익 수치, 2021년 KAIST 논문의 효과 크기는 원문 미확인.

## 5. 개인 데이트레이더 수익성 기저율과, 수익을 내는 소수의 특징

### Takeaway
대만·브라질·인도의 전수(全數)에 가까운 계좌 자료는 일관되게 "한 해 기준 70–80% 이상이 손실, 비용 차감 후 꾸준히 버는 사람은 1% 미만~수 %"를 보여준다. 한국 자료는 덜 정밀하지만 방향은 같고(과잉거래, 거래비용이 거래이익을 초과), 수익 지속성의 유일하게 확인된 예측변수는 "과거 성과"다.

### Cited Findings
- Barber, Lee, Liu & Odean (2014, Journal of Financial Markets, 대만 전체 데이트레이더, 1992–2006): **비용 차감 후 예측 가능하고 안정적으로 양의 초과수익을 내는 데이트레이더는 전체의 1% 미만**. 전년도 성과 상위 500명은 이후 수수료 전 61.3bp/일, 수수료 후 37.9bp/일을 벌고, 하위 집단은 −11.5bp/일(전), −28.9bp/일(후) — [Berkeley 원고](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf), [JFM 서지](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)
- 같은 대만 자료: 데이트레이더의 합산 순성과는 연구한 **15년 모든 해에 음(−)**. 평균적인 해에 약 36만 명이 데이트레이딩을 하고 그중 약 15%가 그 해 초과수익을 냄(초기 워킹페이퍼 기준). 전년도 손실 이력이 있는 수만 명의 데이트레이더는 이후에도 총 초과수익 −17.5bp/일(순 −34.2bp/일) — [Berkeley 원고(학습)](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/day%20trading%20and%20learning%20110217.pdf), [eScholarship](https://escholarship.org/uc/item/7k75v0qx)
- "Do Day Traders Rationally Learn About Their Ability?" (이후 "Learning, Fast or Slow", Review of Asset Pricing Studies 2020): 성과가 나쁜 트레이더가 그만둘 확률이 더 높지만, **많은 데이트레이더가 손실 이력에도 불구하고 놀랄 만큼 지속**한다(2차 요약 인용) — [RAPS 서지](https://econpapers.repec.org/RePEc:oup:rasset:v:10:y:2020:i:1:p:61-93.), [Berkeley 원고](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/day%20trading%20and%20learning%20110217.pdf)
- Chague, De-Losso & Giovannetti ("Day Trading for a Living?", 브라질 주가지수 선물, 2013–2015년 신규 진입자 전원): **300일 넘게 지속한 사람의 97%가 손실**. 은행 창구직원 수준(하루 54달러) 이상을 번 사람은 0.4%, 최상위 개인도 하루 310달러를 큰 위험을 지고 벌었음. 데이트레이딩을 통한 학습의 증거 없음. (CNN Brasil은 표본 약 1,500명 중 45명만 손실을 보지 않았다고 보도 — 분모 정의에 주의) — [FGV EESP TD 525](https://ideas.repec.org/p/fgv/eesptd/525.html), [Quantpedia](https://quantpedia.com/retail-day-trading-is-an-uphill-battle/), [CNN Brasil](https://www.cnnbrasil.com.br/business/day-trade-o-que-e-como-fazer-e-vale-a-pena/)
- SEBI(인도 증권거래위원회) 연구(2024-07 발표, 현물 주식 장중 매매, 상위 10개 증권사 개인고객 = 전체의 약 86%): FY2022-23에 개인 장중 트레이더의 **71%가 순손실**. 연 500회 초과 거래자는 손실자 비율 80%. 30세 미만은 76%. 손실자는 매매손실의 57%에 해당하는 금액을 거래비용으로 추가 지출(이익자는 이익의 19%) — [Business Standard](https://www.business-standard.com/markets/news/over-70-intra-day-traders-incur-losses-during-fy23-reveals-sebi-study-124072401110_1.html), [Business Today](https://www.businesstoday.in/markets/story/seven-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses-finds-sebi-study-438624-2024-07-24)
- 한국 — 자본시장연구원(2021, 코로나19 국면 개인투자자 분석): 코로나19 이후 1년간 개인의 거래이익 13조 원 vs **거래비용 13.7조 원(증권거래세 9.8조 + 위탁수수료 3.9조)**. 개인의 약 46%가 손실, 신규 투자자는 60% 이상 손실. 원인으로 높은 회전율·잦은 종목 교체·과잉확신 지목 — [뉴데일리](https://biz.newdaily.co.kr/site/data/html/2021/02/26/2021022600078.html), [파이낸셜뉴스](https://www.fnnews.com/news/202104131912345956), [KCMI 보도자료](https://www.kcmi.re.kr/community/press_release_view?bno=344)
- 한국 — 이은정·박경서·장하성(2007, Asia-Pacific Journal of Financial Studies 36(3)): 한국 주식시장에서 데이트레이딩이 전체 거래량의 30% 이상을 차지. 선행 해외 연구 대부분은 데이트레이딩이 수익적이지 않다고 결론(이 논문 자체의 수익자 비율은 미확인) — [한양대 ERICA 저장소](https://scholarworks.bwise.kr/erica/handle/2021.sw.erica/44396)
- 한국 — KOSPI 200 선물 데이트레이딩 연구(2012, 투자자 분류 자료): **국내 개인은 데이트레이딩으로 상당한 손실**, 더 자주·더 크게 거래하는 개인일수록 손실 가능성이 큼. 국내 자산운용사와 외국인 기관은 이익 경향 — [성균관대 Pure](https://pure.skku.edu/en/publications/the-profitability-of-day-trading-an-empirical-study-using-high-qu/)
- 한국 — 박경서·조영현(2010, 한국증권학회지 39(3)) "데이트레이더의 성과지속성과 시장효율성": 개인 데이트레이더 일별수익률의 실제 성과분포가 효율적 시장에서 나올 이론적 분포와 확연히 다름(일부의 지속적 우월 성과 존재를 시사) — [고려대 저장소](https://scholar.korea.ac.kr/handle/2021.sw.korea/118395)
- 한국 — 우민철·최혁(2012, 한국증권학회지 41(5)): ETF 시장에서 데이트레이더 계좌의 55.3%가 이익(검색 요약 기준) — [원문 PDF 사본](https://www.smallake.kr/wp-content/uploads/2024/11/kjfs-2012-41-5-677.pdf)
- 한국 — 공매도 데이트레이더 연구(Journal of Banking & Finance 2017): 개인 공매도 데이트레이더는 거래비용을 감안해도 대체로 양의 이익(공매도 의존 결과 — 롱온리 대상에는 적용 불가) — [EconPapers](https://econpapers.repec.org/RePEc:eee:jbfina:v:79:y:2017:i:c:p:159-172)
- 한국 — 자본시장연구원의 개인 약 20만 명 분석: 이익 종목은 빨리 팔고 손실 종목은 훨씬 오래 보유(처분효과), 과잉거래·투기적 행태 — [아시아경제](https://www.asiae.co.kr/en/article/2026030915095124614)
- 참고(강세장 편향): 신한투자증권의 2025년 1–11월 자료에서 개인투자자의 67.0%가 이익(데이트레이딩이 아닌 전체 주식 매매, 강세장) — [아시아경제](https://view.asiae.co.kr/en/article/2025121813401683002)

### Inferences
- 기저율 요약: "임의의 개인 데이트레이더가 비용 차감 후 지속적으로 이익을 낼 사전확률"은 대만 기준 1% 미만, 브라질 선물 기준 3% 미만이다. 제품 기획은 "수익을 낸다"가 아니라 "**손실을 내는 것이 기본값**"에서 출발해야 한다.
- 한국 수치 중 55.3%(ETF 데이트레이더)·67%(2025 전체 개인)는 기간·상품·강세장 편향이 크고 "계좌 단위 단기 이익 여부"라서 대만 연구의 "지속적 초과수익" 기준과 비교할 수 없다.
- 확인된 성공 예측변수는 과거 성과의 지속성(대만 상위 500명)뿐이다. 이는 도구 설계상 "충분히 긴 표본 외 페이퍼 트레이딩 기록으로 엣지가 지속되는지 먼저 검증"하는 절차를 정당화한다.
- 인도·한국 자료 모두 거래 빈도가 높을수록 손실 확률이 커지고 비용이 손실의 큰 부분을 차지한다. 자동화 도구는 거래 횟수를 늘리기 쉬우므로, **일일 거래 횟수 상한과 비용 누적 표시**가 기저율에 근거한 안전장치다.

### Gaps
- 수익을 내는 소수의 구체적 특징(경험, 거래 종목 집중도, 지정가 주문 사용 등)은 Barber 등의 원문 표를 확인하지 못해 적지 않았다. 미검증.
- 금융감독원/한국거래소의 "데이트레이딩 계좌 손실 비율" 공식 통계는 찾지 못했다. KCMI의 데이트레이딩 전용 보고서도 검색되지 않았다.
- 이은정·박경서·장하성(2007)의 수익자 비율, 박경서·조영현(2010)의 지속적 초과수익자 비율은 원문 미확인.
- 대만 "80% 이상이 6개월간 손실"은 한국 논문의 선행연구 소개를 통한 재인용이라 원문 확인 필요.

## 6. 익절/손절 설계: 손절 규칙의 증거, 비대칭 TP/SL, 시간 청산, 손익분기 승률

### Takeaway
이론과 실증 모두 "손절은 추세(양의 자기상관) 전략에서 가치가 있고, 평균회귀 전략에서는 기대수익을 깎는다"는 쪽이다. 촘촘한 손절은 거래비용 때문에 특히 불리하다. TP 0.9%/SL 0.5%/왕복비용 0.25%에서는 손익분기 승률이 약 54%로, 무작위 진입의 기대 승률 약 36%와의 격차가 매우 크다.

### Cited Findings
- Kaminski & Lo (2014, Journal of Financial Markets): **랜덤워크 가설하에서 단순 0/1 손절 규칙은 항상 전략의 기대수익을 낮춘다**. 수익률이 모멘텀(양의 자기상관)을 가지면 손절 프리미엄이 양(+)이 될 수 있다. 실증(미국 주식 월별 1950–2004, 손절 시 장기국채로 이동)에서는 일부 손절 규칙이 손절 기간 중 월 50–100bp를 추가 — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/114876), [JFM 서지](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:234-254)
- 같은 논문의 평균회귀 사례에 대한 2차 해석: 평균회귀 과정에서는 손절이 이후의 되돌림을 놓치게 만드는 경우가 많다(Advisor Perspectives 2025 논평; 원문 문구 미확인) — [Advisor Perspectives](https://www.advisorperspectives.com/commentaries/2025/10/23/stop-losses)
- Lo & Remorov (2017, Journal of Financial Markets 34:1–15, 미국 개별주 대규모 표본): 자기상관·국면전환·거래비용을 포함한 손절 수익의 닫힌 해를 도출. **촘촘한(tight) 손절 전략은 주로 거래비용 때문에 매수후보유보다 부진**. 자기상관이 충분히 높은 종목에서만 초과성과 가능. 넓은 손절이 더 낫지만 여전히 원수익은 매수후보유보다 낮고, 하방위험 감소 효과는 크지 않음(2차 요약 포함) — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/107017), [CXO Advisory](https://www.cxoadvisory.com/equity-premium/stop-losses-on-stock-positions-in-depth)
- Barrot, Kaniel & Sraer (2016): 개인의 역추세 포지션은 초과수익이 소멸한 한참 뒤에 청산되어 보상을 놓침 — 시간 제한 청산의 근거 — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:120:y:2016:i:1:p:146-168)
- 한국 개인의 처분효과(이익은 빨리 실현, 손실은 오래 보유) — [아시아경제](https://www.asiae.co.kr/en/article/2026030915095124614)

### Inferences
- **손익분기 승률 산술**(시간 청산 없이 TP 또는 SL로만 끝난다고 가정; p = (SL + c) / (TP + SL), c = 왕복 비용):
  - TP 0.9% / SL 0.5%, 비용 0%: 35.7%
  - 비용 0.20%: 50.0%
  - 비용 0.25%: 53.6%
  - 비용 0.30%: 57.1%
  - 손절이 미끄러져 실제 평균 손실이 0.6%가 되고 비용 0.25%면: (0.6+0.25)/1.5 = 56.7%
- 표류 없는 랜덤워크에서 +0.9%에 −0.5%보다 먼저 닿을 확률은 0.5/1.4 ≈ 35.7%다. 즉 진입 신호가 **승률을 약 36%에서 54% 이상으로 18%p 끌어올려야** 본전이다. 동치 표현: 거래당 총 기대수익(p×0.9 − (1−p)×0.5)이 왕복 비용 0.25%를 넘어야 한다.
- 왕복 비용 0.25%는 TP의 28%, SL의 50%에 해당한다. 순 기준 손익비는 (0.9−0.25) : (0.5+0.25) = 0.65 : 0.75 ≈ 0.87로, 명목 1.8:1이던 손익비가 **비용 후에는 1 미만**이 된다.
- 평균회귀 전략에 진입가 근처의 촘촘한 손절(0.5%)을 두는 것은 Kaminski–Lo/Lo–Remorov 논리와 어긋난다: 급락 직후는 변동성이 가장 높은 구간(Zawadowski 등)이라 0.5%는 잡음 범위 안에 있을 가능성이 높고, 되돌림 직전에 손절될 위험이 크다. 문헌에 더 부합하는 대안은 (a) 손절폭을 종목의 최근 분 단위 변동성(ATR 배수)에 연동, (b) 가격 손절보다 **시간 손절**을 주된 청산으로 사용, (c) 재난 방지용 넓은 손절만 유지하는 것이다. 단, 이는 문헌으로부터의 추론이며 해당 규칙의 직접 검증 연구는 없다.
- TP < SL(승률 높고 손익비 낮음)은 평균회귀 시스템에서 흔한 형태지만 비용이 TP를 잠식하는 비율이 커진다. TP > SL(현 설계)은 승률 요구치가 낮은 대신 평균회귀의 수익 분포(작은 반등 다수)와 맞지 않을 수 있다. 어느 쪽이 나은지는 반등 크기 분포의 실측에 달려 있다.

### Gaps
- Lei & Li (2009) "The value of stop loss strategies", Han, Zhou & Zhu의 손절 연구, López de Prado의 삼중 장벽(triple-barrier) 방법은 검색 예산 소진으로 출처를 확보하지 못했다. 삼중 장벽은 TP·SL·시간 제한 중 먼저 닿는 것으로 표본을 라벨링하는 프레임이라는 일반적 이해만 있으며(미검증), 퍼들의 청산 구조와 형식적으로 동일하다.
- 장중 분 단위 평균회귀 전략에서 TP/SL 비율·시간 청산을 체계적으로 비교한 동료심사 실증 연구는 찾지 못했다.
- Kaminski & Lo의 평균회귀 사례 결론은 원문이 아닌 2차 논평에 근거한다.

## 7. 비용과 수용력: 스프레드·시장충격·호가단위·거래세가 단기 엣지를 얼마나 잠식하는가, 왕복 0.25%에서 가능한 보유기간

### Takeaway
고회전 전략은 비용 차감 후 살아남는 경우가 드물고, 살아남는 예외(저변동성 종목의 산업 대비 반전)는 비용 절감형 설계와 기관급 체결을 전제로 한다. 한국은 2026년부터 매도 시 0.20%의 거래세가 붙어, 하루에도 여러 번 회전하는 전략은 세금만으로 연간 수십 %의 고정 손실을 안는다.

### Cited Findings
- Novy-Marx & Velikov (2016, RFS; NBER w20721, 미국): 월 편도 회전율 50% 미만인 이상현상 대부분은 비용 절감형으로 설계하면 유의한 순 스프레드를 유지하지만, **회전율이 더 높은 전략은 소수만** 그렇다. 가장 효과적인 비용 절감 기법은 "매수/보유 스프레드"(진입 기준을 유지 기준보다 엄격하게). 신규 자금 수용력은 회전율과 반비례. 저변동성 종목에 집중한 산업 대비 반전은 비용을 고려한 설계에서 유의한 순 스프레드를 유지 — [NBER w20721](https://www.nber.org/papers/w20721), [RFS 서지](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:104-147.)
- Frazzini, Israel & Moskowitz ("Trading Costs", 대형 기관(AQR)의 실거래 1.7조 달러, 21개 선진시장, 19년): 하루 안에 끝난 거래의 평균 시장충격 약 9bp(중앙값 약 6bp, 금액가중 평균 약 15bp), 그중 약 85%는 영구적이고 24시간 내 되돌려지는 부분은 평균 1.26bp. 실제 비용은 선행 연구 추정보다 한 자릿수 작음 — 단, 수동적 지정가 주문으로 스프레드를 거의 지불하지 않는 체결 방식에 의존 — [SSRN 3229719](https://papers.ssrn.com/abstract=3229719), [Alpha Architect](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/)
- Avramov, Chordia & Goyal (2006): 반전 수익 < 거래비용 — [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:61:y:2006:i:5:p:2365-2394)
- de Groot, Huij & Zhou (2012): 비용 타격은 소형주 매매에서 발생, 대형주 한정 + 회전율 제한으로 순 30–50bp/주 — [EconPapers](https://econpapers.repec.org/RePEc:eee:jbfina:v:36:y:2012:i:2:p:371-382)
- 한국 증권거래세(2026-01-01 체결분부터): 코스피 증권거래세 0.05% + 농어촌특별세 0.15% = **실효 0.20%**(기존 0.15%에서 인상), 코스닥·K-OTC는 단일 0.20%. 금투세 폐지에 따라 2023년 수준으로 환원. 매도 시 원천징수 — [이코노미스트](https://economist.co.kr/article/view/ecn202512220061), [세정일보](https://www.taxtimes.co.kr/news/article.html?no=272624), [더팩트](https://news.tf.co.kr/read/economy/2278747.htm)
- 2026년 상반기 증권거래세 수입은 증시 활황으로 전년 대비 4.5배 — [뉴시스](https://www.newsis.com/view/NISX20260731_0003731197)
- Zawadowski 등 (2006): 급변 직후 NYSE 스프레드 급확대가 역추세 이익 대부분을 흡수 — [arXiv](https://arxiv.org/abs/cond-mat/0406696)
- SEBI(인도): 손실자는 손실의 57%만큼을 비용으로 추가 지출 — [Business Standard](https://www.business-standard.com/markets/news/over-70-intra-day-traders-incur-losses-during-fy23-reveals-sebi-study-124072401110_1.html)

### Inferences
- 세금 드래그 산술: 매도세 0.20%만으로도 하루 1회 왕복·연 250거래일이면 회전 자본 대비 연 약 50%의 고정 비용이다(0.20% × 250). 하루 3회면 약 150%. 수수료·스프레드를 더한 0.25–0.30%면 하루 1회에 연 62–75%.
- 보유기간별 타당성(문헌 수치와의 대조, 추론):
  - 일별 반전의 가격 압력 평균 0.49%(반감기 약 1일, NYSE) → 왕복 0.25%면 평균 사건에서 남는 여지는 최대 0.2%대이며, 반감기가 하루이므로 **수십 분 보유로는 그 일부만** 회수한다.
  - 주간 반전 총수익(1990년 이전 패자 +0.9~1.2%/주) → 0.25%는 감당 가능하지만 이는 감쇠 이전 수치다(9절).
  - 결론적으로 왕복 0.25%에서는 "분 단위 평균 반등"보다 "**수 시간~수일 보유의 조건부로 큰 반전**"이 산술상 더 유리하다. 장중 청산 제약을 유지한다면 진입 조건을 훨씬 엄격하게(더 큰 급락, 무뉴스, 고변동성 국면) 잡아 거래당 총 기대수익을 0.25%보다 충분히 크게 만들어야 한다.
- Novy-Marx & Velikov의 "진입 기준을 엄격하게" 원칙은 퍼들에 그대로 적용 가능하다: 거래 횟수를 줄이고 신호 강도 상위만 거래하는 것이 비용 대비 가장 효과적인 개선이다.
- Frazzini 등의 낮은 비용 수치는 기관의 수동적 체결에 해당하며, 시장가 진입 개인에게는 적용되지 않는다. 소액 개인에게 시장충격은 작지만 **스프레드 절반 × 2 + 세금 + 수수료**는 온전히 부담한다.
- 지정가 진입(급락 중 매수 호가에 대기)은 스프레드를 지불하지 않고 오히려 유동성 공급 보상에 가까워지지만, 역선택(계속 빠질 때만 체결됨) 위험이 있다 — 페이퍼 트레이딩에서 두 방식을 병행 비교할 가치가 있다.

### Gaps
- 국내 상장 ETF 매도 시 증권거래세 면제 여부(일반적으로 주식형 ETF는 면제로 알려져 있음)는 이번 조사에서 출처를 확보하지 못했다. **사실이라면 ETF 대상 퍼들의 왕복 비용은 0.25%가 아니라 수수료+스프레드 수준으로 크게 낮아지므로**, 손익분기 산술이 근본적으로 달라진다. 반드시 별도 확인 필요.
- 토스증권 Open API의 실제 수수료율, 한국 종목의 가격대별 호가단위와 실효 스프레드, 급락 직후 스프레드 확대폭에 대한 자료는 확보하지 못했다.
- 한국 시장에서 개인 시장가 주문의 실효 비용을 계측한 연구는 찾지 못했다.

## 8. 국면 의존성: 장중 평균회귀는 언제 가장 잘 작동하는가

### Takeaway
반전 보상은 변동성이 높고 유동성 공급이 위축된 시기에 커진다(VIX 조건부). 종목 측면에서는 뉴스 없는 유동성 충격, 지수 대비 특이적 움직임에서 강하고, 시간대는 개별주 기준 마감 무렵이 후보다. 다만 "레인지 장세 vs 추세 장세" 식의 구분을 장중 반전에 대해 직접 검증한 학술 증거는 확보하지 못했다.

### Cited Findings
- 변동성 국면: 반전(유동성 공급) 기대수익과 조건부 샤프비율은 VIX가 높을 때 크게 상승, 2007–09 위기에서 극대 — [Nagel, NBER w17653](https://www.nber.org/papers/w17653)
- 불확실성 국면: 개인 역추세 포트폴리오 초과수익은 평시 연 19%, 고불확실성 시기 최대 연 40%(프랑스 2002–2010) — [Barrot, Kaniel & Sraer](https://econpapers.repec.org/RePEc:eee:jfinec:v:120:y:2016:i:1:p:146-168)
- 종목 특성: 변동성이 높은 종목은 반전이 더 강하고 초기에 빠름, 회전율이 낮은 종목은 반전이 오래 지속. 시장조성 역량은 종목 규모에 비례 — [Dai, Medhat, Novy-Marx & Rizova](https://www.nber.org/papers/w30917)
- 종목 특성: 가장 큰 반전은 고회전·저유동성 종목(단, 비용 초과 못함) — [Avramov, Chordia & Goyal](https://econpapers.repec.org/RePEc:bla:jfinan:v:61:y:2006:i:5:p:2365-2394). 순수익은 대형주 한정에서 — [de Groot, Huij & Zhou](https://econpapers.repec.org/RePEc:eee:jbfina:v:36:y:2012:i:2:p:371-382). 저변동성 종목의 산업 대비 반전이 비용 후 생존 — [Novy-Marx & Velikov](https://www.nber.org/papers/w20721)
- 시간대(미국 개별주): 동일 시간대 지속성은 개장·마감 30분에서 가장 강하고, 초단기 반전은 1시간 미만 유동성 불균형 — [Heston, Korajczyk & Sadka](https://arxiv.org/abs/1005.3535). 마감 전 30분 개별주 횡단면 반전 — [End-of-Day Reversal 워킹페이퍼](https://www3.nd.edu/~zda/EOD.pdf). 마감 무렵 차익거래자 포지션 축소로 미스프라이싱 팩터 부진 — [Bogousslavsky 2021](https://ideas.repec.org/a/eee/jfinec/v141y2021i1p172-194.html)
- 시간대(한국 개별주): 개장 30분 모멘텀 없음, 마감 전 1시간 30분~30분 구간 반전(KOSPI 809종목, 2011–2020, 석사논문) — [KAIST](https://koasas.kaist.ac.kr/handle/10203/294938)
- 지수 수준: 그날의 방향이 마지막 30분까지 이어지는 장중 모멘텀(60여 선물, 1974–2020) — [Baltussen 등](https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:1:p:377-403)
- 급변 직후: 변동성·거래량·스프레드가 사건 후 며칠간 높게 유지 — [Zawadowski 등](https://arxiv.org/abs/cond-mat/0406696)
- VI: 직전에 현저히 오버슈팅한 경우 발동 직후 균형가격 회복 효과 제한적 — [CORE](https://core.ac.uk/download/512003943.pdf)

### Inferences
- 문헌 간 긴장: "반전이 가장 큰 곳(고변동·저유동·소형)"과 "비용 후 살아남는 곳(대형·저변동·유동)"이 정반대다. 롱온리·시장가·세금 0.20% 조건에서는 후자(유동 대형주/ETF)에서 **시장 변동성이 높은 날에만** 거래하는 조합이 양쪽 조건을 가장 덜 위배한다.
- 지수 장중 모멘텀과의 충돌을 피하려면 "지수가 그날 강하게 하락 추세인 날"은 종목 급락 매수를 줄이거나 금지하는 국면 필터가 타당하다(지수 방향이 마감까지 이어지는 경향).
- 시간대 가설(검증 필요): 개장 직후는 정보 반영·동일 시간대 지속성이 강해 급락이 정보성일 가능성이 높고, 오후~마감 전은 개별주 반전 증거가 있다. 페이퍼 트레이딩 로그를 시간대별로 분해해 확인할 것.
- 고변동성 국면은 보상과 비용이 동시에 커진다. 2026년처럼 VI 발동이 역대 최대인 시기의 성과는 평시와 분리해 평가해야 한다.

### Gaps
- "레인지 일(range day) vs 추세 일(trend day)" 분류에 따른 장중 평균회귀 성과를 다룬 동료심사 연구는 찾지 못했다. 실무 블로그 수준의 주장만 존재하며 증거로 채택하지 않았다.
- 한국 시장에서 VKOSPI 조건부 반전 수익을 검증한 연구는 확인하지 못했다.
- 점심시간대(유동성 저점) 반전 강도에 대한 직접 증거는 확보하지 못했다.

## 9. 알파 감쇠와 발표 효과: 단기 반전은 소수점 호가제·HFT 이후 약해졌는가

### Takeaway
단기 반전을 포함한 주요 이상현상의 수익은 2001년 소수점 호가제(decimalization) 이후 대략 절반으로 줄었다는 증거가 있고, 단순 역추세 전략의 수익성은 1995년 이후 꾸준히 하락했다. 다만 유동성 공급 보상이라는 성격상 위기·고변동성 국면에서는 다시 커지며, 변동성·회전율에 따른 횡단면 패턴은 최근 20년에도 질적으로 유지된다.

### Cited Findings
- McLean & Pontiff (2016, JF 71(1):5–32, 미국): 97개 예측변수의 표본 외·발표 후 수익 예측력을 검증. 투자자가 학술 발표로부터 미스프라이싱을 학습하며, 마찰이 차익거래를 막는 한 예측력이 완전히 사라지지는 않는다는 해석 — [JF 서지](https://econpapers.repec.org/RePEc:bla:jfinan:v:71:y:2016:i:1:p:5-32)
- Chordia, Subrahmanyam & Tong (2014, Journal of Accounting and Economics 58(1):41–58, 미국): 주요 이상현상 대부분이 약화되었고, **이상현상 기반 포트폴리오 전략의 평균수익은 소수점 호가제 이후 대략 절반**. 헤지펀드 운용자산·공매도 잔고·총 회전율 증가가 원인. 반전도 약화 대상에 포함(대학 요약 기준) — [EconPapers](https://econpapers.repec.org/RePEc:eee:jaecon:v:58:y:2014:i:1:p:41-58), [Emory Goizueta 요약](https://goizueta.emory.edu/node/29561)
- 위 결과에 대한 반론: 2019년 Journal of Economics and Business 논문은 미국 증거가 완전히 강건하지 않으며, 이상현상과 유동성 사이의 음의 관계에 대한 설득력 있는 시계열·횡단면 증거를 찾지 못했다고 보고 — [EconPapers](https://econpapers.repec.org/RePEc:eee:jebusi:v:103:y:2019:i:c:p:61-79)
- Khandani & Lo ("What Happened to the Quants in August 2007?", JFM 2011, 미국): Lehmann/Lo–MacKinlay식 단순 역추세 롱숏 전략의 수익성은 **1995년 이후 꾸준히 하락**했고, 같은 평균 일수익을 유지하는 데 필요한 레버리지는 1998→2007년 약 4.5배로 증가(CXO 2차 요약). 2007년 8월에는 대형 퀀트 포트폴리오의 강제 청산으로 큰 손실 — 저자들은 가설이 간접 증거에 기반한 잠정적 해석임을 명시 — [MIT 논문 페이지](https://web.mit.edu/Alo/www/Papers/august07b.html), [CXO Advisory](https://www.cxoadvisory.com/mutual-hedge-funds/no-fire-exit-at-the-overcrowded-hedge-fund-party)
- 감쇠에도 유지되는 부분: 변동성·회전율에 따른 반전의 횡단면 효과는 표본의 마지막 20년 이전과 그 기간 중에도 질적으로 일관 — [Dai 등, NBER w30917](https://www.nber.org/papers/w30917). 위기 국면에서는 반전 수익이 급증 — [Nagel](https://www.nber.org/papers/w17653)
- 초단기 예측력은 속도 경쟁의 대상: 데이터 적시성이 밀리초 단위로 개선될수록 예측력이 증가 — [Aït-Sahalia 등, NBER w30366](https://www.nber.org/papers/w30366)
- 실무 재현에서의 감쇠 사례(약한 증거): Gao 등 장중 모멘텀의 QuantConnect 재현은 원 논문보다 낮은 성과 — [QuantConnect](https://www.quantconnect.com/learning/articles/investment-strategy-library/intraday-etf-momentum). ORB의 블로그 재현은 "총수익 재현, 순수익 0" — [MQL5 블로그](https://www.mql5.com/en/blogs/post/776235)

### Inferences
- 1990년 논문들의 총 엣지(주 1% 안팎)를 현재의 기대치로 쓰면 안 된다. 감쇠 후 평시의 무조건부 반전 엣지는 개인 시장가 비용보다 작다고 보는 것이 보수적 기본값이다.
- 남아 있는 엣지는 "조건부"다: 고변동성 국면, 유동성 공급자가 물러나는 순간, 뉴스 없는 충격. 이는 상시 가동 전략이 아니라 **조건이 충족될 때만 켜지는 전략**으로 설계해야 함을 뜻한다.
- 공개된 단순 규칙(급락 후 매수)은 HFT·시장조성자가 훨씬 빠르게 수행하므로, 1분 폴링 구조에서 남는 것은 그들이 재고 위험 때문에 받아주지 않는 큰 충격의 잔여 부분뿐이다.
- 자체 백테스트·페이퍼 트레이딩 결과에도 같은 할인(표본 외 감쇠)을 적용해야 한다: 파라미터를 고른 기간의 성과는 실전 기대치의 상한으로 취급.

### Gaps
- McLean & Pontiff의 대표 수치(기억상 표본 외 약 26% 감소, 발표 후 약 58% 감소)는 이번 검색 결과로 확인되지 않았다. 미검증이므로 보고서 인용 전 원문(DOI 10.1111/jofi.12365) 확인 필요.
- Khandani & Lo의 연도별 평균 일수익률 표(기억상 1995년 일 1%대 → 2007년 0.1%대)는 원문 미확인. 미검증.
- 단기 반전 "단독"의 소수점 호가제 전후 수익 변화 수치는 확보하지 못했다(Chordia 등은 이상현상 묶음 기준).
- 한국 시장에서의 반전 감쇠(예: 2023년 호가단위 개편, 대체거래소 넥스트레이드 출범 이후) 연구는 찾지 못했다.
