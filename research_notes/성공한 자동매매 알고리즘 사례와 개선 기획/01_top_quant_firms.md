# 역사상 가장 성공한 자동매매(퀀트) 회사·펀드와 알고리즘 — 리테일 단타 도구에 옮길 수 있는 것과 없는 것 (2026-11 기준)

> 조사 조건 메모: 이 세션에서는 sec.gov, hsgac.senate.gov, institutionalinvestor.com, bloombergquint.com 원문 열람이 네트워크 정책으로 막혀 있었다. 따라서 아래 수치는 모두 "검색 결과에 표시된 해당 페이지 요약"에서 확인한 것이고, 원문 전문을 직접 읽어 대조하지는 못했다. 검색으로 확인하지 못하고 기억에만 의존하는 수치는 각 질문의 "Gaps"에 "기억 기반, 미확인"으로 따로 적었다.
> 전제(의뢰 조건): 토스증권 Open API, 국내 주식·ETF 매수 전용, 1분봉 REST 폴링(지연 약 0.5~수 초), 급락 매수 후 반등 매도(익절/손절/시간 청산), 모의투자, 왕복 비용 약 0.2~0.3%.

## 1. Renaissance Technologies / Medallion Fund — 무엇이 실제로 문서화되어 있나

### Takeaway
Medallion의 수익률(1988~2018 연평균 수수료 전 약 66%, 수수료 후 약 39%)과 수수료·폐쇄 구조는 Zuckerman의 책과 Cornell 논문으로 비교적 잘 문서화되어 있지만, 알고리즘 자체는 "수십 개 전략을 하나의 시스템으로 묶은 단기 통계 신호 + 높은 레버리지 + 거래비용 최소화" 수준까지만 공개되어 있다. "승률 50.75%"는 Mercer가 지인에게 한 말을 Zuckerman이 옮긴 2차 인용이며, Medallion의 실제 거래 통계로 확인된 수치가 아니다.

### Cited Findings
- Zuckerman 책 기준 Medallion의 1988~2018 연평균 수익률은 수수료 전 66.1%, 수수료 후 39.1%로 널리 인용된다. — [Wealth Management (Bloomberg 재게재)](https://www.wealthmanagement.com/alternative-investments/jim-simons-built-the-best-hedge-fund-ever)
- 66.1%는 복리 수익률이 아니라 연도별 수익률의 단순 평균으로 보인다는 지적이 있다. Cornell의 계산으로는 1988~2018년에 100달러가 3억 9,870만 달러가 되었고 복리 수익률은 63.3%다. — [arXiv 2405.10917](https://arxiv.org/pdf/2405.10917v2); [Cornell, "Medallion Fund: The Ultimate Counterexample?" (SSRN 사본)](https://www.scribd.com/document/470291821/SSRN-id3504766-pdf)
- Cornell은 "수백만 건의 거래를 하므로 거래비용이 컸을 텐데, 보고된 총수익률은 거래비용 차감 후"라는 점을 들어 Renaissance가 비용 최소화에 특히 뛰어났다고 추론한다(저자의 추론이지 Renaissance의 공개 자료가 아님). — [Cornell SSRN 사본](https://www.scribd.com/document/470291821/SSRN-id3504766-pdf)
- 수수료는 운용보수 5%·성과보수 20%에서 5%·44%로 올랐다(44% 적용은 2002년부터, 2001년에 단계 인상). — [Bloomberg 2016, "How Renaissance's Medallion Fund Became Finance's Blackest Box"](https://www.bloombergquint.com/markets/how-renaissance-s-medallion-fund-became-finance-s-blackest-box); [Cornell SSRN 사본의 표](https://www.scribd.com/document/470291821/SSRN-id3504766-pdf)
- 2021년 1월부터 운용보수가 5%에서 4%로 내렸고 성과보수 44%는 유지되었다. 같은 Bloomberg 기사는 2012년에 2.5%였다고도 적어 수수료 연표에 불일치가 있다. — [Bloomberg, "Renaissance's Insiders Get an Added Bonus With Medallion Fee Cut"](https://www.bloombergquint.com/markets/renaissance-s-insiders-get-an-added-bonus-with-medallion-fee-cut)
- 1993년에 외부 자금 모집을 중단했고, 2005년까지 외부 투자자 지분을 모두 돌려주어 전·현직 직원 전용 펀드가 되었다. — [Bangkok Post (Bloomberg 재게재, 2016)](https://www.pressreader.com/thailand/bangkok-post/20161122/281994672084794); [Benzinga](https://benzinga.com/z/36965421)
- 펀드 규모는 약 100억 달러 수준으로 유지된다(WSJ 제목 "Renaissance's $10 Billion Medallion Fund"). 2024년 보도에서는 내부 자본 약 120억 달러로 표현했다. — [HFR의 WSJ 기사 색인](https://www.hfr.com/media/in-the-news/wsj-renaissance%C2%92s-10-billion-medallion-fund-gains-24-year-to-date/); [Hedgeweek 2025-01](https://www.hedgeweek.com/renaissance-tech-and-two-sigma-lead-2024-quant-gains/)
- Bloomberg(2016)는 Medallion이 "dozens of 'strategies' that run together as one system"으로 운용된다고 보도했다. — [Bloomberg 2016](https://www.bloombergquint.com/markets/how-renaissance-s-medallion-fund-became-finance-s-blackest-box)
- 1989년 손실 뒤 Simons는 단기 매매를 선호한 Henry Laufer를 다시 부르고 Elwyn Berlekamp를 영입했다. Berlekamp가 이끈 1990년 수익률은 수수료 후 55.9%(Bloomberg는 56%로 표기)였다. — [Quantt, Medallion fund history](https://www.quantt.co.uk/resources/medallion-fund-history); [Bloomberg 2016](https://www.bloombergquint.com/markets/how-renaissance-s-medallion-fund-became-finance-s-blackest-box)
- "50.75%" 인용: Zuckerman 책에 Robert Mercer가 지인에게 "우리는 50.75%만 맞지만, 그 50.75%에 대해서는 100% 맞다. 그렇게 수십억 달러를 벌 수 있다"는 취지로 말했다고 나온다. 책은 Mercer가 회사의 정확한 우위를 밝힌 것은 아닐 것이라고 덧붙인다. 이 세션에서 확인한 것은 독자 발췌(2차 인용)다. — [Goodreads 독자 발췌](https://www.goodreads.com/notes/44698571-the-man-who-solved-the-market/58027759-thomas-wolf/800f9239-07c1-4032-a735-d1e2b9f74842); [Daily Speculations](https://dailyspeculations.com/wordpress/?p=14425)
- Simons 인용(2차 출처, 일시·장소 불명확): "Efficient market theory is correct in that there are no gross inefficiencies. But we look at anomalies that may be small in size and brief in time." — [25iq](https://25iq.com/2014/07/09/a-dozen-things-ive-learned-from-jim-simons/); [Novel Investor](https://novelinvestor.com/wise-words-from-jim-simons)
- Simons 인용(2014년 샌프란시스코 주립대 강연으로 보도됨): "The only rule is you never hit the override button." 다만 실제로는 Simons가 모델을 무시하고 개입한 사례가 있었다는 반론도 있다. — [Benzinga 2025-04](https://benzinga.com/markets/equities/25/04/44916664/jim-simons-stood-by-one-quant-investing-rule-that-helped-him-earn-66-returns-for-30-years-you-ju); 반론 [Morningstar Australia](https://www.morningstar.com.au/insights/personal-finance/247322/the-greatest-investor-youve-never-heard-of)
- 미 상원 상설조사소위원회(PSI) 2014-07-22 보고서 "Abuse of Structured Financial Products": Deutsche Bank와 Barclays가 Medallion에 판 만기 1년 초과 바스켓 옵션 60건의 이익이 약 342억 달러, 회피 세금 60억 달러 이상으로 추정되었다. Levin 의원 모두발언은 1999~2013년 이익을 "300억 달러 이상"이라고 했다. — [Accounting Today](https://www.accountingtoday.com/news/renaissance-avoided-more-than-6-billion-tax-senators-say); [청문회 기록 (govinfo)](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm); [PSI 청문회 페이지](https://www.hsgac.senate.gov/subcommittees/investigations/hearings/abuse-of-structured-financial-products-misusing-basket-options-to-avoid-taxes-and-leverage-limits)
- Renaissance는 같은 청문회 제출문에서 바스켓(배리어) 옵션이 "Medallion 모델의 예측을 최적으로 활용하는 데 필요한 높은 레버리지"를 제공한다고 스스로 밝혔다. 레버리지가 수익 구조의 핵심이라는 1차 진술이다. — [Renaissance 제출문 (PSI)](https://www.hsgac.senate.gov/wp-content/uploads/imo/media/doc/STMT%20-%20Renaissance%20%28July%2022%202014%29.pdf)
- 최근 실적: Medallion은 2024년 약 30% 수익(Zuckerman 인용 보도). — [Hedgeweek 2025-01](https://www.hedgeweek.com/renaissance-tech-and-two-sigma-lead-2024-quant-gains/)
- 외부 투자자용 펀드는 Medallion과 전혀 다르게 움직였다. 2025년 10월 RIEF −14.39%, RIDA −15.6%로 연간 손실 전환, 11월에 12% 이상 반등했으나 9월 수준은 회복하지 못했다. — [Institutional Investor 2025-11](https://www.institutionalinvestor.com/article/renaissance-suffers-huge-losses-october); [Institutional Investor 2025-12](https://www.institutionalinvestor.com/article/premium/renaissances-public-funds-stage-double-digit-comeback-november)

### Inferences
- 문서로 확인되는 Medallion의 구조는 (1) 작고 짧은 이상 현상을 매우 많이 모아 하나의 모델로 운용, (2) 높은 레버리지, (3) 거래비용 최소화, (4) 규모 상한(약 100억 달러)과 이익 전액 분배다. (2)~(4)는 모두 "한 건당 우위가 아주 얇다"는 것과 일관된다. 얇은 우위는 비용이 bp(0.01%) 단위일 때만 남는다.
- 왕복 비용 0.2~0.3%인 리테일 사용자에게 "승률 50.75%"는 본보기가 될 수 없다. 익절폭 TP, 손절폭 SL, 왕복 비용 c일 때 손익분기 승률은 (SL + c) / (TP + SL)이다. TP = SL = 1%, c = 0.25%이면 62.5%, TP = SL = 2%이면 56.25%, TP = SL = 0.5%이면 75%가 필요하다. TP 1.5%, SL 1.0%, c 0.25%이면 50%다. 즉 이 도구에서는 승률보다 "비용 대비 목표 폭"이 먼저 결정되어야 한다.
- 같은 회사가 운용해도 장기·대용량 펀드(RIEF/RIDA)는 2025년 10월 한 달에 −14~15%를 냈다. Medallion의 성과는 "Renaissance의 모델링 능력" 일반이 아니라 단기·저용량·고회전 영역에 국한된 것으로 읽는 편이 맞다.
- 리테일에 옮길 수 있는 것: 재량 개입 금지 원칙(단, 비상 정지는 별도), 여러 약한 신호의 결합, 비용을 수익률 계산에 먼저 넣는 습관, 운용 규모를 우위가 감당하는 범위로 제한하는 태도. 옮길 수 없는 것: 레버리지(바스켓 옵션), 수백만 건 거래에 의한 대수의 법칙, 수십 년 치 정제 데이터, 박사급 인력 수백 명.

### Gaps
- Medallion의 2025년 연간 수익률은 신뢰할 수 있는 출처를 찾지 못했다. WSJ 제목 "Medallion Gains 24% Year to Date"는 연도를 확인하지 못했다.
- Medallion의 Sharpe 비율, 실제 승률, 평균 보유 기간, 신호 종류는 공개된 1차 자료가 없다. 인터넷에 도는 "Sharpe 6 이상" 같은 수치는 출처를 추적하지 못했다.
- 기억 기반, 미확인: PSI 보고서의 "레버리지 최대 20:1", "하루 10만 건 이상 거래"는 흔히 인용되지만 이번 검색에서 원문으로 확인하지 못했다(hsgac.senate.gov 열람 차단).
- 기억 기반, 미확인: Zuckerman 책의 세부(Laufer의 단일 모델 주장, 요일·시간대 효과, Berlekamp와 Kelly의 Bell Labs 인연, 2007년 8월 Medallion 손실과 Simons의 개입, 2008년 수익률)는 책 원문을 대조하지 못했다. 의뢰서의 "거래비용을 'the devil'이라 불렀다"는 표현도 출처를 찾지 못했다.
- Kelly 기준을 Renaissance가 실제 포지션 크기 결정에 썼다는 1차 증거는 찾지 못했다.

## 2. 통계적 차익거래의 역사 — Tartaglia, D. E. Shaw, PDT, Two Sigma, 2007년 8월 "퀀트 퀘이크"

### Takeaway
페어 트레이딩과 단기 반전(떨어진 것을 사고 오른 것을 파는) 전략은 학술적으로 수익이 확인되었지만, 시간이 갈수록 수익이 줄었고 같은 전략에 자금이 몰리면 한꺼번에 무너진다는 것이 2007년 8월에 드러났다. 급락 매수 전략은 본질적으로 이 "단기 반전" 계열이므로 이 역사가 가장 직접적인 참고 사례다.

### Cited Findings
- Gatev, Goetzmann, Rouwenhorst (Review of Financial Studies, 2006): 1962~2002년 일별 자료에서 단순한 페어 매매 규칙이 자기자금조달 포트폴리오 기준 연 최대 11%의 초과수익을 냈다. 저자들은 수익 일부가 시장 미시구조 효과(호가 스프레드에 의한 착시)일 수 있다고 적었다. — [RFS 2006 서지](https://econpapers.repec.org/RePEc:oup:rfinst:v:19:y:2006:i:3:p:797-827); [NBER w7032](https://nber.org/papers/w7032)
- 같은 논문의 역사 서술: Morgan Stanley의 Nunzio Tartaglia 그룹이 함께 움직이는 종목 쌍을 찾는 프로그램을 만들었고 회사에 5,000만 달러 이익을 안긴 것으로 전해지나, 두어 해 부진 뒤 1989년에 해체되었다. — [Alpha Architect 요약](https://alphaarchitect.com/2013/06/pairs-trading-kicks-butt/); [NBER w7032](https://nber.org/papers/w7032)
- Avellaneda & Lee (Quantitative Finance, 2010): PCA 기반 평균회귀 전략의 Sharpe는 1997~2007년 평균 1.44였으나 2003~2007년에는 0.9로 떨어졌다. ETF 기반 전략은 1.1이고 2002년 이후 비슷하게 악화되었다. 거래량 정보를 더한 ETF 전략은 2003~2007년 1.51이었다. 수치는 거래비용 차감 후다. — [NYU 사본 (2008)](https://math.nyu.edu/~avellane/AvellanedaLeeStatArb071008.pdf); [NYU 사본 (2009)](https://www.math.nyu.edu/faculty/avellane/AvellanedaLeeStatArb20090616.pdf)
- Khandani & Lo (2007; 2011 후속): 2007년 8월 손실은 대형 시장중립 포트폴리오 한두 개의 급격한 청산에서 시작되어 다른 펀드의 손절·디레버리징 규칙을 연쇄 발동시켰다는 가설을 제시했다. 8월 10일의 큰 반등이 이 가설과 부합한다. 저자들은 결론이 간접 증거에 기반한 잠정적 추측이라고 명시했다. — [MIT 논문 페이지](https://web.mit.edu/Alo/www/Papers/august07.html); [NBER w14465](https://www.nber.org/papers/w14465)
- 후속 논문은 청산이 2007년 7월에 시작해 연말까지 이어졌고, 8월 6일 주에 시장조성 성격의 자본이 일시 철수했다고 보았다. 두 번의 청산(8월 1일 10:45~11:30, 8월 6일 개장~13:00)을 식별했다. 타격이 컸던 펀드는 서브프라임이 아니라 상장 주식 롱숏 전략을 쓰고 있었다. — [MIT 후속 논문 페이지](https://web.mit.edu/Alo/www/Papers/august07b.html); [NBER w14465](https://www.nber.org/papers/w14465)
- Scott Patterson 인터뷰: Morgan Stanley의 PDT(Peter Muller)는 2007년 8월 며칠 사이 약 6억 달러를 잃었다. PDT는 1990년대 말 한때 회사 전체 이익의 4분의 1을 냈다. 8월 10일 시스템이 무너지지 않은 것은 AQR의 Cliff Asness가 위험을 더 진 것과 Goldman Sachs가 자사 퀀트 펀드에 유동성을 넣은 덕이라고 서술한다. — [Motley Fool의 Patterson 인터뷰](https://www.fool.com/investing/general/2010/07/29/how-wall-streets-quants-lost-billions-and-lived-to.aspx); [EconLib 서평](https://www.econlib.org/archives/2010/01/the_quants.html)
- D. E. Shaw Composite 펀드는 2001년 출범 이후 연평균 순수익률 12.7%(2024년 실적 보도 기준), 2025년 +18.5%. Oculus 펀드는 2004년 출범 이후 연 13.7%. — [BNN Bloomberg 2025-01](https://bnnbloomberg.ca/business/company-news/2025/01/02/de-shaw-to-return-billions-after-flagship-hedge-fund-gains-18); [Yahoo Finance 2025 결산](https://finance.yahoo.com/news/2025-returns-hedge-funds-rolling-234728986.html)
- Two Sigma는 2025년 상반기 Spectrum 펀드 +7.6%. 연간 확정치는 찾지 못했다. — [The Star (Bloomberg 재게재) 2025-07](https://www.thestar.com.my/business/business-news/2025/07/07/quant-funds-reap-gains-amid-volatile-market)

### Inferences
- 학술 문헌의 평균회귀 전략은 거래비용을 매우 낮게 가정하고도 Sharpe가 1 안팎이며 2003년 이후 뚜렷이 약해졌다. 왕복 0.2~0.3% 비용을 내는 리테일 전략이 같은 종류의 우위를 기대하려면 훨씬 드물고 큰 괴리(급락)만 골라야 한다. 거래 횟수가 줄어드는 대가를 치르고 한 건당 기대수익을 키우는 방향이다.
- 2007년 8월의 교훈은 "평균회귀는 평소에 꾸준히 벌다가, 다른 참가자의 강제 청산이 겹치면 며칠 연속으로 같은 방향으로 틀린다"는 것이다. 매수 전용 급락 매수 전략에서는 이것이 "급락이 반등 없이 이어지는 날이 한 종목이 아니라 여러 종목에서 동시에 온다"는 형태로 나타난다. 종목별 손절만으로는 부족하고, 같은 날 동시 보유 종목 수·일일 총손실 한도·시장 전체 급락 시 신규 진입 중단 같은 포트폴리오 수준 규칙이 필요하다.
- 기관은 숏으로 시장 위험을 상쇄하지만 이 도구는 매수 전용이다. 따라서 "평균회귀 수익"과 "시장 하락 손실"이 분리되지 않는다. 성과 평가 때 같은 시간대의 시장(예: 지수 ETF) 수익률을 빼고 봐야 전략의 우위와 시장 방향을 구분할 수 있다.

### Gaps
- 기억 기반, 미확인: Khandani & Lo의 모의 반전 전략 수치(일평균 수익률이 1995년 약 1.38%에서 2007년 약 0.13%로 하락, 2007-08-07~09 사흘 연속 손실 약 −1.16%, −2.83%, −2.86% 후 08-10에 약 +5.92% 반등, 수익 유지를 위해 레버리지 약 8배 필요)는 널리 인용되지만 이번 세션에서 원문 대조를 못 했다. 보고서에 쓰려면 원문 확인이 필요하다.
- 기억 기반, 미확인: Avellaneda & Lee의 거래비용 가정(편도 5bp, 왕복 10bp)은 검색으로 확인하지 못했다.
- Gatev 외 논문이 표본 후반부 수익 감소를 보고했다는 점, Tartaglia 그룹 수익이 1980년대 후반에 줄었다는 "추세"는 이번 검색에서 직접 확인하지 못했다(확인된 것은 "부진 후 1989년 해체"뿐).
- D. E. Shaw의 2007년 8월 손실 규모, PDT의 "하루 3억 달러 손실" 수치는 출처를 찾지 못했다.
- 한국 시장(KOSPI/KOSDAQ) 분봉 단위 단기 반전의 수익성에 대한 자료는 이 노트의 범위에서 조사하지 않았다.

## 3. 고빈도 시장조성 회사 — Virtu, Jane Street, Citadel Securities, HRT, Jump, Tower

### Takeaway
이들의 "거의 지지 않는" 성적은 가격 예측이 아니라 호가 스프레드를 아주 많이, 아주 빨리 받아내고 재고를 즉시 헤지하는 사업 구조에서 나온다. 연구는 수익이 상대적 속도 순위에 좌우되고 소수 회사에 집중된다고 보여 주므로, 수 초 지연의 REST 폴링으로는 같은 수익원을 건드릴 수 없다.

### Cited Findings
- Virtu의 2014년 3월 IPO 신고서(S-1): "As a result of our real-time risk management strategy and technology, we had only one losing trading day during the period depicted, a total of 1,238 trading days." — [Themis Trading의 S-1 인용](https://blog.themistrading.com/?p=5710); [Business Insider](https://businessinsider.in/everyones-talking-about-the-high-frequency-trading-firm-that-just-had-1-day-of-trading-losses-in-1238-days/amp_articleshow/31849923.cms)
- 같은 문장이 2014년 4월 수정 신고서(Amendment No. 2)에는 "1,278 trading days"로 나온다. 두 숫자가 모두 SEC 제출 문서에 존재한다. — [SEC EDGAR 수정 신고서](https://sec.gov/Archives/edgar/data/1592386/000104746914003675/filename2.pdf)
- Virtu는 연차보고서에서 사업 모델을 "대량의 증권을 사고팔며 작은 매수·매도 호가 차이를 번다"고 설명하고, 변동성이 클 때 거래대금당 수취율이 오를 수 있으며, 상대하는 주문 흐름의 질과 개인 투자자 참여 수준이 시장조성 실적을 좌우한다고 적는다. — [Virtu 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1592386/000159238626000009/virt-20251231.htm)
- Virtu의 무손실 기록에 대해서는 "작은 스프레드를 대량으로 받는 사업은 원래 위험이 작다", "유일한 손실일도 기술적·인적 오류였을 것"이라는 회의적 평가가 있었다. — [Themis Trading](https://blog.themistrading.com/?p=5710)
- Baron, Brogaard, Kirilenko (E-mini S&P 500 선물 초기 원고): 중앙값 HFT 회사의 연율 Sharpe는 4.3(2012년 원고는 중앙값 4.5, 범위 3~20). — [CFTC 사본 (2014)](https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf)
- Baron, Brogaard, Hagströmer, Kirilenko (JFQA 2019, 스웨덴 주식): 상대적 지연시간(latency) 차이가 HFT 회사 간 성과 차이를 크게 설명하고, 코로케이션 업그레이드로 속도 순위가 오른 회사는 성과가 좋아졌다. HFT 수익과 거래량의 집중도는 5년 표본 내내 높고 낮아지지 않았다. — [JFQA 2019 서지](https://ideas.repec.org/a/cup/jfinqa/v54y2019i03p993-1024_00.html); [작업 논문 사본](https://www.cb.cityu.edu.hk/ef/doc/GRU/WPS/GRU%232017-018%20Baron%20et%20al.pdf)
- 2025년 순거래수익(Reuters, 익명 소식통·문서 기반, 회사 미확인): Jane Street 396억 달러(사상 최대), Hudson River Trading 약 123억 달러, Citadel Securities 약 122억 달러(전년 대비 +25%). — [Reuters 재게재 (KFGO) 2026-04-24](https://kfgo.com/2026/04/24/jane-streets-40-billion-trading-haul-tops-rivals-sources-say/); [Hedgeweek](https://www.hedgeweek.com/jane-street-outpaces-rivals-with-record-40bn-trading-haul/)
- 규제 리스크 사례: 인도 SEBI는 2025-07-03 잠정 명령으로 Jane Street의 Bank Nifty 지수 조작 혐의(2023-01~2025-03)를 제기하고 약 4,843억 루피(₹4,843 crore)를 묶었다. Jane Street는 항소했고, 2026년 10월 기준 증권항소심판소(SAT)에서 계류 중이며 최종 결론은 확인되지 않았다. — [ThePrint](https://theprint.in/economy/sebi-bans-us-based-jane-street-from-securities-mkt-impounds-illegal-gains-of-rs-4843-cr/2679517/); [Business Today 2026-10-07](https://www.businesstoday.in/markets/story/sebi-asks-jane-street-to-respond-after-sharing-trade-data-in-market-manipulation-case-report-560196-2026-10-07)

### Inferences
- 시장조성 회사의 수익원은 (1) 스프레드 수취, (2) 거래소 리베이트와 낮은 수수료, (3) 속도(호가 갱신·취소가 남보다 빠름), (4) 재고를 초 단위로 헤지하는 능력, (5) 개인 주문 흐름에 대한 접근이다. 이 다섯 가지 모두 자격·규모·설비가 필요하다. 리테일 사용자는 스프레드를 "받는" 쪽이 아니라 "내는" 쪽이고, 한국에서는 매도 시 거래세까지 낸다.
- Baron 외 연구의 핵심은 "절대 속도"가 아니라 "상대 순위"가 수익을 정한다는 점이다. 폴링 주기가 0.5초든 3초든 이 경쟁에서는 같은 꼴찌 그룹이다. 따라서 이 도구는 속도가 승부를 가르는 신호(호가 불균형, 수 초짜리 가격 지연 차익)를 설계 대상에서 빼야 하고, 수 분 이상 지속되는 가격 움직임만 다뤄야 한다.
- "1,238일 중 손실 1일"은 전략의 예측력이 아니라 사업 구조(하루 수백만 건의 작은 독립 거래 + 재고 중립)의 결과다. 하루 몇 건 거래하는 방향성 전략이 이 수치를 목표로 삼으면 손절을 미루는 식의 잘못된 설계로 이어질 수 있다.
- 다만 한 가지는 가져올 수 있다. 시장조성 회사가 변동성이 커질 때 더 많이 번다는 사실은, 급락 직후 구간에서 유동성 공급자(지정가 매수자)에게 보상이 생긴다는 뜻이다. 급락 매수 전략은 이 보상의 느린 부분을 노리는 셈이며, 시장가보다 지정가 주문이 비용 면에서 유리할 가능성이 있다(체결되지 않을 위험과 맞바꿈).

### Gaps
- 1,238일과 1,278일의 차이는 수정 신고서에서 집계 기간이 달라진 것으로 추정되나 원문으로 확인하지 못했다(sec.gov 열람 차단). 집계 기간(기억으로는 2009-01-01~2013-12-31)도 미확인이다.
- Jump Trading, Tower Research의 실적은 비상장이라 신뢰할 수 있는 수치를 찾지 못했다.
- Citadel Securities의 미국 개인 주문 점유율, 주문흐름 대가(PFOF) 규모는 이번 검색에서 출처를 확보하지 못했다.
- Michael Lewis "Flash Boys"와 그에 대한 비판은 이번 세션에서 출처를 검색하지 못했다.
- 한국 시장의 시장조성 구조와 토스증권 API의 실제 체결 지연은 이 노트 범위 밖이다.

## 4. 추세추종 CTA와 Ed Thorp — 문서화된 위험관리·포지션 크기 규칙

### Takeaway
가장 구체적으로 공개된 규칙은 Turtle 규칙(변동성으로 포지션 크기를 정하고 한 단위 손실을 자산의 약 1~2%로 제한, 상관된 포지션 합계에 상한)과 Thorp의 Kelly 기준(우위에 비례해 걸되 실제로는 그보다 작게)이다. 진입 신호는 달라도 이 두 가지 크기 결정 원칙은 급락 매수 전략에 그대로 적용할 수 있다.

### Cited Findings
- Turtle 규칙(원문 사본 기준): N은 20일 평균 변동폭(ATR)이고, 한 단위(unit)는 N만큼의 가격 변동이 계좌의 1%가 되도록 정한다. 손절은 진입가에서 2N이므로 한 단위의 최대 손실은 계좌의 2%다. 다만 한 2차 해설은 "손절 시 손실 약 1%"로 달리 설명한다. — [The Original Turtle Trading Rules 사본](https://studylib.net/doc/5545012/turtletrading); 다른 설명 [MQL5 해설](https://www.mql5.com/en/articles/23448)
- Turtle 진입·청산: 시스템 1은 20일 돌파 진입·10일 반대 돌파 청산, 시스템 2는 55일 돌파 진입. 유리하게 0.5N 움직일 때마다 한 단위 추가. — [TakeProfit 해설](https://takeprofitapp.com/en/learn/turtle-trading-system); [MQL5 해설](https://www.mql5.com/en/articles/23448)
- Turtle 한도: 단일 시장 4단위, 밀접 상관 시장 합계 6단위, 느슨한 상관 시장 합계 10단위, 한 방향 합계 12단위. 2차 자료마다 12단위의 적용 범위 설명이 다르다. — [원문 사본](https://studylib.net/doc/5545012/turtletrading); 다른 설명 [TakeProfit](https://takeprofitapp.com/en/learn/turtle-trading-system)
- Thorp의 Princeton/Newport Partners 성과는 출처마다 다르다: 19년간 연 15.1% 순수익(American Scientist), 존속 기간 연 15.8%·표준편차 4.3%·같은 기간 시장 10.1%(다른 출처), "약 19%, 20년간 손실 분기 없음"(또 다른 출처). 손실 분기가 없었다는 주장에 의문을 제기하는 글도 있다. — [American Scientist](https://www.americanscientist.org/article/bettor-math); [Wikipedia: Edward Thorp](https://www.wikipedia.org/wiki/Edward_Thorp); 의문 제기 [ValueWalk](https://www.valuewalk.com/1901745/)
- Thorp는 Kelly 기준을 블랙잭에 적용한 뒤 금융시장으로 확장했고, 이를 정리한 논문 "The Kelly Criterion in Blackjack, Sports Betting and the Stock Market"을 남겼다. — [Thorp 2006 논문 사본](https://www.gwern.net/doc/statistics/decision/2006-thorp.pdf); [Wikipedia: Edward Thorp](https://www.wikipedia.org/wiki/Edward_Thorp)
- 추세추종의 최근 성과: SocGen CTA 지수는 2025년 6월 초까지 연초 대비 8% 넘게 하락했고, 추세추종 펀드군은 2025년 상반기 −10.1%로 2000년 이후 최악의 반기였다. Man AHL Alpha는 한 보도 시점에 −7.8%. — [Alternatives Watch 2025-06](https://www.alternativeswatch.com/2025/06/02/trend-following-hedge-funds-endure-more-pain-societe-generale-indices/); [The Star (Bloomberg) 2025-07](https://www.thestar.com.my/business/business-news/2025/07/07/quant-funds-reap-gains-amid-volatile-market); [Hedgeweek](https://www.hedgeweek.com/man-groups-quant-hedge-funds-slide-as-market-volatility-roils-trend-strategies/)
- Man AHL은 2025년 논문에서 추세추종 펀드 간 성과 차이가 주로 시스템의 핵심 설계 변수(속도, 시장 구성 등)에서 온다고 설명하고, 부진 구간 뒤에 우호적 환경이 자주 왔다고 주장한다(운용사 자체 자료이므로 마케팅 성격 감안). — [AIMA 게재 Man AHL 글](https://www.aima.org/article/a-trend-following-deep-dive-the-dynamics-of-dispersion.html); [Man Group, "Is this time different?"](https://www.man.com/insights/is-this-time-different)

### Inferences
- 변동성 기반 크기 결정을 이 도구에 옮기면: 종목별 최근 분봉 변동폭으로 손절폭을 정하고, 손절 시 손실이 계좌의 일정 비율(예: 0.5~1%)이 되도록 주문 수량을 역산한다. 종목마다 변동성이 다르므로 "종목당 같은 금액"보다 "종목당 같은 위험"이 일관된 결과를 준다.
- Turtle의 상관 한도는 2007년 8월 교훈과 같은 이야기다. 같은 날 급락한 종목들은 서로 상관이 높으므로(같은 업종, 같은 시장 충격) 동시 보유 수와 합계 위험에 상한을 둬야 한다.
- Kelly 공식(승률 p, 순이익률 b, 순손실률 a일 때 f* = p/a − (1−p)/b)을 단타에 넣어 보면, 예컨대 p = 55%, b = a = 1.25%일 때 f* = 8, 즉 자산의 8배를 걸라는 답이 나온다. 한 건당 폭이 작은 전략에서 Kelly는 레버리지를 요구한다는 뜻이고, Medallion이 레버리지를 쓴 이유와 맞닿는다. 레버리지 없는 매수 전용 사용자에게 Kelly는 상한으로 작동하지 않는다. 실질 제약은 "p 추정이 틀렸을 가능성"이므로, 우위가 검증되기 전에는 Turtle식 고정 소액 위험이 더 맞는 규칙이다.
- 추세추종의 2025년 부진은 "검증된 체계적 전략도 여러 해 손실 구간이 있다"는 사실을 보여 준다. 모의투자 몇 주의 성과로 전략을 채택하거나 폐기하면 안 된다는 근거가 된다.

### Gaps
- Winton(David Harding), Man AHL의 구체적 크기 결정 규칙(변동성 목표 수준 등)과 장기 Sharpe는 이번 검색에서 1차 출처를 확보하지 못했다.
- Thorp의 정확한 수익률(흔히 "19.1%, 손실 분기 없음"으로 인용)은 출처 간 불일치가 있고, "A Man for All Markets" 원문을 대조하지 못했다. 수수료 전/후, 기간(1969~1988/89) 정의 차이로 보이나 확정하지 못했다.
- Thorp 논문의 "실전에서는 Kelly의 절반 이하를 권한다"는 내용은 기억에 근거하며 이번 세션에서 원문 대조를 못 했다.
- Turtle 실험 참가자들의 실제 수익률(흔히 "연 80%")은 출처를 확인하지 않았다.

## 5. 실무자들이 말하는 공통 처방 — 인용과 근거

### Takeaway
출처가 확인되는 발언과 연구를 모으면 공통 요소는 다섯 가지다: 작고 짧은 우위를 많이 모은다, 비용을 뺀 뒤의 수익으로 판단한다, 재량 개입을 막는다, 운용 규모를 제한한다, 위험 통제를 기술로 실시간 집행한다. "엄격한 표본 외 검증"은 누구나 말하지만 이번 조사에서 최상위 회사의 구체적 절차를 보여 주는 1차 자료는 찾지 못했다.

### Cited Findings
- 작고 짧은 우위: Simons, "we look at anomalies that may be small in size and brief in time." (2차 출처) — [25iq](https://25iq.com/2014/07/09/a-dozen-things-ive-learned-from-jim-simons/)
- 얇은 승률 × 많은 횟수: Mercer의 "50.75%" 발언(Zuckerman 책, 2차 인용). — [Goodreads 발췌](https://www.goodreads.com/notes/44698571-the-man-who-solved-the-market/58027759-thomas-wolf/800f9239-07c1-4032-a735-d1e2b9f74842)
- 하나의 시스템: Medallion은 "dozens of 'strategies' that run together as one system". — [Bloomberg 2016](https://www.bloombergquint.com/markets/how-renaissance-s-medallion-fund-became-finance-s-blackest-box)
- 재량 개입 금지: Simons, "The only rule is you never hit the override button." (실제 예외가 있었다는 반론 병기) — [Benzinga](https://benzinga.com/markets/equities/25/04/44916664/jim-simons-stood-by-one-quant-investing-rule-that-helped-him-earn-66-returns-for-30-years-you-ju); [Morningstar Australia](https://www.morningstar.com.au/insights/personal-finance/247322/the-greatest-investor-youve-never-heard-of)
- 비용: Cornell은 Medallion의 총수익률이 거래비용 차감 후라는 점에서 비용 최소화 능력을 핵심으로 추론했다. Avellaneda & Lee도 비용 차감 후 Sharpe를 보고한다. — [Cornell SSRN 사본](https://www.scribd.com/document/470291821/SSRN-id3504766-pdf); [Avellaneda & Lee](https://math.nyu.edu/~avellane/AvellanedaLeeStatArb071008.pdf)
- 실시간 위험 통제: Virtu는 무손실 기록의 원인을 "real-time risk management strategy and technology"라고 스스로 설명했다. — [Themis Trading의 S-1 인용](https://blog.themistrading.com/?p=5710)
- 레버리지와 모델 예측의 결합: Renaissance는 높은 레버리지가 모델 예측을 "최적으로 활용"하는 데 필요하다고 진술했다. — [Renaissance 제출문 (PSI)](https://www.hsgac.senate.gov/wp-content/uploads/imo/media/doc/STMT%20-%20Renaissance%20%28July%2022%202014%29.pdf)
- 전략의 수명: 평균회귀 전략 Sharpe가 1997~2007년 1.44에서 2003~2007년 0.9로 떨어졌다. 우위는 시간이 가면 줄어든다. — [Avellaneda & Lee](https://math.nyu.edu/~avellane/AvellanedaLeeStatArb071008.pdf)

### Inferences
- 통계적으로 "우위가 있다"고 말하려면 필요한 거래 수가 생각보다 많다. 승률의 표준오차는 √(0.25/N)이다. 실제 승률 55%를 50%와 구분(2 표준오차)하려면 약 400건, 52%는 약 2,500건, 50.75%는 약 17,800건이 필요하다. 하루 3~5건 거래하는 도구라면 55% 수준의 우위를 확인하는 데도 4~6개월이 걸린다. 모의투자 기간과 "실전 전환 기준"을 거래 건수로 정해야 하는 이유다.
- 성과는 대략 (한 건당 순기대수익 ÷ 한 건당 변동성) × √(독립 거래 수)에 비례한다(Grinold의 "능동 운용의 기본 법칙"으로 알려진 관계, 이번 세션에서 출처 미확인). 리테일은 거래 수를 기관처럼 늘릴 수 없으므로 한 건당 순기대수익을 키우는 쪽, 즉 비용의 몇 배가 되는 큰 괴리만 고르는 쪽으로 설계해야 한다.
- "여러 약한 신호의 결합"은 이 도구에서 "급락 폭 하나만 보지 말고, 거래량 급증 여부·시장 전체 방향·시간대·종목 유동성 같은 조건을 함께 점수화한다"로 번역된다. Avellaneda & Lee에서 거래량 정보를 더하자 Sharpe가 오른 것(2003~2007년 1.51)이 이 방향의 근거다.
- "재량 개입 금지"와 "비상 정지"는 구분해야 한다. 개별 거래 판단에는 개입하지 않되, 시스템 오작동이나 손실 한도 초과 때 전체를 멈추는 장치는 6번 질문의 사고 사례가 요구하는 필수 요소다.

### Gaps
- 최상위 회사의 표본 외 검증·과최적화 방지 절차를 구체적으로 보여 주는 1차 자료는 이번 조사에서 확보하지 못했다. 이 주제는 학술 문헌(백테스트 과최적화 연구 등)으로 보완해야 한다.
- Simons 발언들은 모두 2차 출처(인용 모음, 기사)에서 확인했고 강연 원문·영상과 대조하지 못했다. "2010년 MIT 강연" 출처 표기는 확인되지 않았다.
- Peter Brown, Berlekamp, Patterson의 직접 인용은 이번 세션에서 출처를 확보하지 못했다.

## 6. 자동매매 실패 사례와 교훈 — Knight, LTCM, Flash Crash, 퀀트 퀘이크, 한맥투자증권

### Takeaway
대형 사고는 대부분 예측 모델이 아니라 운영에서 났다: 배포 누락, 입력값 오류, 주문 상한 부재, 경고 무시, 과도한 레버리지. 주문 전 한도 검사, 손실·주문 건수 기준 자동 정지, 배포 점검, 입력값 검증이 있었다면 피해가 크게 줄었을 사례들이다.

### Cited Findings
- Knight Capital(2012-08-01): 오류로 3억 9,700만 주 이상을 거래해 수십억 달러의 원치 않는 포지션을 쌓았고 4억 6,000만 달러가 넘는 손실을 냈다. — [SEC 보도자료 2013-222](https://www.sec.gov/news/press-release/2013-222); [WilmerHale 해설](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)
- 원인: 여덟 번째 서버로 간 모(母)주문이 남아 있던 옛 코드를 작동시켜 수백만 건의 자(子)주문을 내보냈다. 누적 체결 수량을 확인하는 기능이 코드 이동 후 재검증되지 않았다. 개장 전 시스템이 오류를 알리는 자동 이메일 97통을 보냈지만 경보로 취급되지 않았다. — [Quimbee 사건 요약](https://quimbee.com/cases/in-the-matter-of-knight-capital-americas-llc); [WilmerHale 해설](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)
- 제재: 2013-10-16 SEC와 1,200만 달러에 합의. 2010년 제정된 시장접근 규칙(Rule 15c3-5)의 첫 집행 사례였다. — [SEC 보도자료 2013-222](https://www.sec.gov/news/press-release/2013-222); [WilmerHale 해설](https://www.wilmerhale.com/en/insights/client-alerts/knight-capital-settles-rule-15c3-5-violations-with-sec-agrees-to-pay-12-million)
- 한맥투자증권(2013-12-12, 선물·옵션 동시만기일): 직원이 옵션 가격 계산식의 이자율 항을 "잔여일/365" 대신 "잔여일/0"으로 입력해 프로그램이 호가 상·하한을 설정하지 못했다. 직원이 전원을 내릴 때까지 143초 동안 약 3만 7,900건의 알고리즘 주문이 체결되었고 손실은 462억 원(보도에 따라 463억)이다. — [경향신문 2023-05](https://www.khan.co.kr/article/202305141457001); [이투데이 2023](https://www.etoday.co.kr/news/view/2248804)
- 한맥 후속: 금감원은 '실수(착오거래)'로 결론 냈다. 일부 이익금은 돌려받았으나 약 360억 원을 번 외국계 헤지펀드에서는 돌려받지 못했고 회사는 파산했다. 대법원은 약 10년 뒤 증권사 과실이며 거래를 취소할 수 없다고 판단했다. — [이투데이 2013](https://www.etoday.co.kr/news/view/849470); [이투데이 2014](https://www.etoday.co.kr/news/view/867848); [이투데이 2023](https://www.etoday.co.kr/news/view/2248804); [비즈한국](https://www.bizhankook.com/bk/article/30640)
- 2010-05-06 Flash Crash(CFTC-SEC 합동 보고서, 2010-09-30): 한 대형 투자자(언론은 Waddell & Reed로 지목)가 14:32에 E-mini S&P 500 선물 75,000계약(약 41억 달러) 매도 프로그램을 시작했다. 실행 알고리즘은 가격·시간과 무관하게 직전 거래량의 9%를 목표로 했다. 14:32~14:45에 약 35,000계약이 팔렸다. — [Computerworld](https://www.computerworld.com/article/1540899/regulators-blame-computer-algorithm-for-stock-market-flash-crash.html); [CNN Money](https://money.cnn.com/2010/10/01/markets/SEC_CFTC_flash_crash/index.htm); [Mother Jones](https://www.motherjones.com/kevin-drum/2010/10/what-caused-flash-crash/); [CFTC 보고서 페이지](https://www.cftc.gov/MarketReports/StaffReportonMay6MarketEvents/staffreport050610marketevents.html)
- Kirilenko, Kyle, Samadi, Tuzun (Journal of Finance 2017): HFT가 폭락을 촉발하지는 않았지만 큰 매도 압력에 대한 반응이 변동성을 키웠다. HFT끼리 계약을 주고받는 "hot potato" 현상이 있었고, 펀더멘털 매도·매수 불균형이 HFT의 재고 규모보다 몇 배 컸다. — [CFTC 사본 (2014)](https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_flashcrash0314.pdf); [SSRN](https://papers.ssrn.com/ab_id=1686004)
- LTCM(1998): 1998년 초 자기자본 47억 달러에 차입 1,245억 달러 이상(부채비율 25배 초과)이었고 넉 달이 안 되는 기간에 46억 달러를 잃었다. 1998-09-23 14개 은행·증권사가 36억 달러를 투입했고 연준은 자금을 넣지 않고 협상을 주선했다. — [Wikipedia: LTCM](https://www.wikipedia.org/wiki/LTCM); [Federal Reserve History](https://www.federalreservehistory.org/essays/ltcm-near-failure)
- 2007년 8월: 한 곳의 강제 청산이 같은 전략을 쓰던 다른 펀드의 손절·디레버리징 규칙을 연쇄 발동시켰다는 가설(저자들이 잠정적이라고 명시). — [Khandani & Lo](https://web.mit.edu/Alo/www/Papers/august07.html)

### Inferences
- 사고별로 "있었다면 막았을 통제"를 이 도구의 요구사항으로 옮기면 다음과 같다.
  - Knight → 배포 점검(모든 실행 환경에 같은 버전이 올라갔는지 확인), 쓰지 않는 코드 제거, 주문 누적 수량·금액 상한, 비정상 주문 빈도 감지 시 자동 정지, 경고를 사람이 반드시 보게 하는 알림 경로.
  - 한맥 → 설정값 범위 검증(0으로 나누기, 음수, 상식 밖 값 거부), 가격이 현재가에서 일정 비율 이상 벗어난 주문 차단, 분당 주문 건수 상한, 전원 차단이 아닌 소프트웨어 정지 스위치(미체결 주문 일괄 취소 포함).
  - Flash Crash → 실행 로직에 가격 조건을 넣기(거래량만 보고 시장가로 계속 내지 않기), 시장 전체가 비정상일 때 신규 진입 중단.
  - LTCM·2007년 8월 → 레버리지 금지(이 도구는 이미 해당), 동시 보유·일일 손실 한도, "평소 상관없던 포지션이 위기 때 같이 움직인다"는 가정.
- 급락 매수 전략 고유의 위험: Flash Crash나 한맥 사고처럼 "오류로 생긴 급락"은 반등하면 큰 이익이지만, 거래가 취소되거나 거래 정지(변동성 완화 장치, 단일가 전환)에 걸리면 손절이 작동하지 않는다. 손절 주문이 체결되지 않는 상황을 모의투자 단계에서 별도 시나리오로 다뤄야 한다.
- 모의투자 단계라도 이 통제들을 먼저 구현하는 것이 순서다. 한맥은 143초, Knight는 한 시간 이내에 회사가 무너졌다. 사람이 알아채고 대응하기에는 너무 짧은 시간이므로 정지는 자동이어야 한다.

### Gaps
- 기억 기반, 미확인: Knight 사고의 "45분", "212건의 고객 주문을 처리하려다 400만 건 이상 주문", "154개 종목", "서버 8대 중 7대만 새 코드 배포", "Power Peg"라는 옛 기능 이름은 SEC 명령서에 있는 것으로 기억하나 sec.gov 열람이 막혀 대조하지 못했다. 의뢰서의 "4억 4,000만 달러"는 회사가 사고 직후 발표한 세전 손실 추정치로 기억하며, SEC 문서의 수치는 "4억 6,000만 달러 이상"이다.
- 한맥 사고 이후 한국거래소가 도입한 제도(착오거래 구제, 일괄 주문 취소 기능, 파생상품 가격 제한 등)의 정확한 내용과 시행일은 이번 세션에서 확인하지 못했다. 국내 주식시장의 현재 변동성 완화 장치 기준도 별도 확인이 필요하다.
- Flash Crash 관련해 2015년 기소된 개인 트레이더(Navinder Sarao)의 스푸핑 책임 비중 논쟁은 조사하지 않았다.
- 한맥 사고에서 이익을 본 헤지펀드의 이름, 회수율 세부는 출처마다 달라 적지 않았다.

## 7. 솔직한 평가 — 최상위 회사의 우위 중 리테일 도구가 흉내 낼 수 있는 몫

### Takeaway
최상위 회사 수익의 대부분은 속도·비용·레버리지·주문 흐름·규모라는 구조적 이점에서 나오며 리테일이 복제할 수 없다. 옮길 수 있는 것은 수익원이 아니라 일하는 방식(비용을 먼저 넣은 검증, 작은 위험 단위, 자동 정지, 충분한 표본)이고, 이것은 돈을 벌어 주기보다 잃지 않게 해 주는 쪽에 가깝다.

### Cited Findings
- 속도 우위는 상대 순위로 결정되고 수익은 소수에 집중된다. — [Baron 외, JFQA 2019](https://ideas.repec.org/a/cup/jfinqa/v54y2019i03p993-1024_00.html)
- Medallion조차 높은 레버리지가 "필요하다"고 스스로 진술했다. — [Renaissance 제출문 (PSI)](https://www.hsgac.senate.gov/wp-content/uploads/imo/media/doc/STMT%20-%20Renaissance%20%28July%2022%202014%29.pdf)
- Medallion은 규모를 약 100억 달러로 묶고 외부 자금을 받지 않는다. 같은 회사의 대용량 펀드는 2025년 10월 −14~15%였다. — [HFR의 WSJ 색인](https://www.hfr.com/media/in-the-news/wsj-renaissance%C2%92s-10-billion-medallion-fund-gains-24-year-to-date/); [Institutional Investor 2025-11](https://www.institutionalinvestor.com/article/renaissance-suffers-huge-losses-october)
- 공개된 평균회귀 전략의 비용 차감 후 Sharpe는 1 안팎이고 시간이 갈수록 낮아졌다. — [Avellaneda & Lee](https://math.nyu.edu/~avellane/AvellanedaLeeStatArb071008.pdf)
- 시장조성 회사는 스프레드를 받는 쪽이며 개인 투자자 참여가 늘수록 실적이 좋아진다고 스스로 밝힌다. — [Virtu 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1592386/000159238626000009/virt-20251231.htm)
- 2025년 상위 3개 시장조성 회사의 순거래수익 합계는 약 640억 달러(Jane Street 396억 + HRT 약 123억 + Citadel Securities 약 122억, 익명 소식통 기반). — [Reuters 재게재 (KFGO)](https://kfgo.com/2026/04/24/jane-streets-40-billion-trading-haul-tops-rivals-sources-say/)

### Inferences
- 정량적 비율("우위의 몇 %가 알파인가")을 뒷받침하는 자료는 없다. 정성적으로 나누면 다음과 같다.

| 요소 | 최상위 회사에서의 역할 | 리테일 도구로 이전 가능한가 |
|---|---|---|
| 속도(코로케이션, 마이크로초) | HFT 수익의 핵심, 상대 순위가 결정 | 불가. 속도가 필요한 신호는 설계에서 제외 |
| 스프레드 수취·리베이트·낮은 수수료 | 시장조성 수익의 본체 | 불가. 리테일은 비용을 내는 쪽(왕복 0.2~0.3%) |
| 레버리지·공매도 | Medallion·통계적 차익거래의 필수 요소 | 불가(매수 전용, 무차입). 시장 방향 위험이 남음 |
| 수백만 건의 독립 거래 | 얇은 승률을 확실한 수익으로 바꿈 | 불가. 건당 기대수익을 키우는 쪽으로 대체 |
| 독점 데이터·인력 | 신호 발굴 | 불가. 공개 분봉·거래량 범위에서만 |
| 비용을 넣은 검증 | 모든 회사의 기본 | 가능. 백테스트·모의투자에 0.25~0.3% 고정 차감 |
| 변동성 기반 크기 결정, 건당 소액 위험 | Turtle, CTA | 가능. 그대로 적용 |
| 상관·동시 보유·일일 손실 한도 | 2007년 8월 이후 표준 | 가능 |
| 자동 정지·주문 상한·입력 검증 | Knight·한맥 이후 표준 | 가능. 최우선 구현 대상 |
| 재량 개입 금지, 규칙 고정 후 평가 | Renaissance의 명시 원칙 | 가능. 단 비상 정지는 예외 |
| 충분한 표본으로 판단 | 통계적 기본 | 가능. 수백 건 단위의 평가 기준 필요 |

- 이 도구가 현실적으로 노릴 수 있는 수익원은 하나다. 급락 직후 유동성이 얇아진 구간에서 매수 주문을 대 주는 대가(단기 반전 프리미엄)다. 기관은 이 프리미엄의 빠른 부분(초~분)을 낮은 비용으로 가져가고, 리테일에 남는 것은 느리고 큰 부분(수 분~수십 분, 비용의 몇 배가 되는 괴리)뿐이다. 이 부분이 0.2~0.3% 비용을 넘는지는 문헌으로 답할 수 없고 한국 분봉 데이터로 직접 검증해야 하는 경험적 질문이다.
- 따라서 제품 기획의 정직한 약속은 "최상위 퀀트처럼 번다"가 아니라 "최상위 퀀트가 쓰는 검증·위험 통제 절차로 전략이 비용을 이기는지 확인하고, 이기지 못하면 실전에 쓰지 않는다"가 되어야 한다.
- 왕복 비용 0.25%에서 하루 3건씩 연 250일 거래하면 비용만 연 약 188%(0.25% × 750건, 건당 투입 자금 대비 단순 합)다. 건당 평균 총수익이 0.25%를 넘어야 본전이라는 뜻이며, 거래 빈도를 올리는 기능은 우위가 검증되기 전에는 손실을 키우는 방향으로 작동한다.

### Gaps
- 개인 단타 매매자의 실제 성과 통계(한국·대만·브라질 등 실증 연구)는 이 노트 범위에서 조사하지 않았다. 리테일 이전 가능성 판단을 보강하려면 별도 조사가 필요하다.
- 한국 시장에서 분 단위 급락 후 반등의 평균 폭과 지속 시간, 왕복 비용의 정확한 구성(수수료, 증권거래세, 호가 스프레드, 미끄러짐)은 확인하지 않았다.
- 구조적 이점과 모델 우위의 기여를 수치로 분해한 연구는 찾지 못했다. 위 표는 인용 자료에 근거한 판단이지 측정값이 아니다.
