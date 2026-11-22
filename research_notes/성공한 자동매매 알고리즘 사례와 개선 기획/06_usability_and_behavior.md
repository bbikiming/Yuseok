# 06. 비전문가용 자동매매·리테일 투자 제품의 사용성과 행동 영향 (2026-11 기준)

> 조사 방법과 한계(먼저 읽을 것)
> - 조사일: 2026-11-22. 웹 검색 약 45회로 수집했다. 이 세션에서는 원문 페이지 열람(WebFetch)이 네트워크 정책으로 전부 차단되었고(osc.ca, fca.org.uk, iosco.org, nber.org, pmc.ncbi.nlm.nih.gov, nngroup.com, webkit.org 등), 마지막 검색 묶음 8건은 세션 공용 검색 한도 소진으로 실행되지 않았다.
> - 따라서 아래 수치는 **검색 결과에 노출된 초록·보도·요약 기준**이다. 논문 본문의 표본 수·세부 계수까지 직접 확인하지 못한 항목은 "(초록 기준)" 또는 "(원문 확인 필요)"로 표시했다.
> - 한국 언론 기사 일부는 검색 요약에서 "어느 기사가 어느 문장을 말했는지"가 완전히 분리되지 않았다. 그런 항목은 관련 기사 2건을 함께 걸고 "(출처 매핑 근사)"로 표시했다.
> - 검증하지 못한 배경지식은 사실로 쓰지 않고 각 절의 **Gaps**에 "미검증"으로 적었다.
> - 표기: 증거 강도 = **강**(무작위 실험/자연실험 + 동료심사), **중**(규제기관 실험·작업논문·관찰 연구), **약**(업체 자료·실무 통념).

---

## 1. 성공한 제품 사례 — 무엇이 쉬웠고, 어떤 가드레일을 두었나

### Takeaway
쉬움의 공통 공식은 "용어를 생활 언어로 바꾸고, 한 화면에 한 가지 결정만 두고, 기본값(프리셋)으로 시작하게 하고, 실전 전에 과거 검증·모의 단계를 끼워 넣는 것"이다. 그러나 가장 크게 성장한 제품들(토스증권, Robinhood)은 바로 그 쉬움·실시간 순위·알림 때문에 과당매매·위험 축소 표현 논란과 규제 조치를 겪었고, **사용자 성과가 좋아졌다는 공개 데이터는 어느 제품에서도 찾지 못했다** — 공개되는 것은 가입자·거래대금 같은 참여 지표뿐이다.

### Cited Findings

**토스증권 (MTS + PC 웹 WTS)**
- 누적 가입자 1,000만 명 돌파(2026년 7월 기준, 출범 5년 4개월), 같은 달 MAU 650만 명(회사 집계). 2030 비중은 초기 약 70% → 약 50%, 40대 이상 약 43%. 2026년 2월에는 누적 860만·MAU 550만이었다 — [머니투데이 2026-08-06](https://www.mt.co.kr/stock/2026/08/06/2026080609444670123); [SBS Biz](https://biz.sbs.co.kr/amp/article/20000326984)
- 수익은 해외주식에 크게 의존: 2025년 외화증권 수탁수수료 4,494억 원으로 업계 1위, 2026년 1분기에는 외화증권 수수료가 전체 수탁수수료의 99% 이상. 2026년 1분기 영업이익 1,117억 원(+34.3%), 상반기 영업이익 3,195억 원 보도 — [CEO스코어데일리 2026-08-18](https://ceoscoredaily.com/page/view/2026081816091001353); [CEO스코어데일리 2026-05-07](https://ceoscoredaily.com/page/view/2026050715075969166) (출처 매핑 근사)
- 2025년 연간 영업이익은 보도에 따라 4,458억 원과 4,521억 원으로 엇갈린다(전년 대비 약 3배). 공시로 확인 필요 — [데일리안](https://www.dailian.co.kr/news/view/1633904/); [더팩트](https://news.tf.co.kr/read/ogmeta/2351906.htm) (출처 매핑 근사)
- 쉬운 말: '매수/매도'를 '구매하기/판매하기'로 바꿔 거래를 일상 소비처럼 느끼게 했다는 분석. 가격 설정과 수량 결정을 서로 다른 화면으로 나눠 한 화면에 한 결정만 두는 구조 — [요즘IT](https://yozm.wishket.com/magazine/detail/919/); [브런치 uibowl "사용성 1위 토스증권 vs 증권앱 1위 미래에셋증권"](https://brunch.co.kr/@uibowl/410) (출처 매핑 근사, 2차 자료)
- 쉬운 말의 부작용 사례: '미수거래'를 '외상구매'로 표기한 것이 '빚투'를 부추길 수 있다며 금융감독원이 시정을 요구했고, 토스증권은 용어를 바꾸는 방향으로 정리했다(2024년 11월 보도) — [메트로신문 2024-11-19](https://www.metroseoul.co.kr/article/20241119500746)
- 실시간 순위: '오늘의 발견' 탭에서 1분 단위로 급등·급락 종목을 순위로 보여준다(회사 측 인터뷰 기사) — [이코노미스트](https://economist.co.kr/article/view/ecn202210130063) (출처 매핑 근사)
- 주식모으기(2022-03 출시, 적립식 자동 매수): 2025년 8월 말 누적 이용자 200만 명. 2024년 8월부터 주식모으기 거래 수수료 무료, 1년간 고객 수수료 절감 32억 원. 이용자 1인당 평균 3.6건 설정, 주기는 매일 54%·매주 29%·매월 17% — [데일리안](https://m.dailian.co.kr/news/view/1675172); [더밸류뉴스](https://thevaluenews.co.kr/news/200595) (출처 매핑 근사)
- PC 웹(WTS): 2024년 7월 정식 출시. 사전 설문에서 고객 30%가 PC 투자 경험을 원했다. 모바일 QR 촬영으로 로그인, 관심종목 실시간 연동 — [SBS Biz](https://biz.sbs.co.kr/amp/article/20000182295); [비즈워치 2024-03-14](https://news.bizwatch.co.kr/article/market/2024/03/14/0024); [디자인컴퍼스 2024-07-19](https://designcompass.org/2024/07/19/toss-invest-pc/)
- WTS 2025년 10월 개편: 홈·종목상세·사이드창 개선, 보유·관심종목 사이드창이 PIP(화면 속 화면)로 떠 있고 위치 이동 가능. 2026년 6월: 최대 4개 멀티차트, 차트 내 주문. 2026년 2월: AI 어닝콜 실시간 번역 PC 버전 — [뉴데일리 2025-10-28](https://biz.newdaily.co.kr/site/data/html/2025/10/28/2025102800134.amp.html); [헤럴드경제 2026-06-03](https://www.heraldk.com/article/2026060316513470589); [바이라인네트워크 2026-02-02](https://byline.network/2026/02/0202-2/)
- 비판·약점: 전산 장애 반복이 "남겨진 과제"로 지적됨. 2026년 8월에는 한 이용자 거래내역에서 약 2년간 주문 거부·실패 76건이 확인됐다는 보도(정상 거부가 섞였을 가능성도 함께 언급) — [데일리안](https://www.dailian.co.kr/news/view/1633904/); [더팩트 2026-08](https://news.tf.co.kr/read/economy/2358451.htm)

**Robinhood**
- 성장: Funded Customers 2025년 2분기 2,650만 → 3분기 2,680만 → 4분기 2,700만(전년 대비 +7%). 2025년 매출 45억 달러(사상 최대) — [Robinhood IR, Q4·FY2025 실적](https://investors.robinhood.com/news-releases/news-release-details/robinhood-reports-fourth-quarter-and-full-year-2025-results)
- 게이미피케이션 제재: 2024-01-18 매사추세츠 증권당국과 750만 달러 과징금 + 디지털 참여 기법 전면 개편에 합의. 당국이 문제 삼은 요소는 색종이(confetti) 애니메이션, 디지털 복권 긁기, 무료 주식 보상 등. Robinhood는 "앱이 게임화되어 있다는 전제를 거부한다"고 밝혔다. confetti는 제소 이후인 2021년에 중단(이번 조사에서 '3월'까지는 미확인) — [WealthManagement](https://www.wealthmanagement.com/regulation-compliance/robinhood-pays-75m-settle-massachusetts-gamification-charge); [Insurance Journal 2024-01-19](https://www.insurancejournal.com/news/east/2024/01/19/756246.htm)
- SEC: 2021년 디지털 참여 기법(DEP) 의견수렴에서 출발한 2023년 7월 '예측 데이터 분석 이해상충' 규칙안은 2025년 6월 다른 13개 안과 함께 철회되었다. SEC는 향후 필요하면 새 제안으로 다루겠다고 밝혔다 — [Alston & Bird 2025-06](https://www.alston.com/en/insights/publications/2025/06/sec-withdraws-multiple-rule-proposals); [Proskauer](https://www.proskauer.com/alert/sec-withdraws-fourteen-rule-proposals); [SEC 규칙안 S7-12-23](https://www.sec.gov/rules/2023/07/s7-12-23)
- 앱 표시 방식이 성과에 미친 영향: Robinhood 이용자가 하루에 가장 많이 산 종목의 이후 20일 비정상수익률은 평균 −4.7%. 저자들은 'Top Mover' 목록의 독특한 노출 방식이 쏠림을 키운다고 본다 — [Barber, Huang, Odean & Schwarz, Journal of Finance 77(6), 2022](https://econpapers.repec.org/RePEc:bla:jfinan:v:77:y:2022:i:6:p:3141-3190)

**TradingView**
- Strategy Tester의 Deep Backtesting은 Premium 이상 요금제, 최대 200만 봉·100만 거래까지, 결과는 차트가 아니라 Strategy Report 탭에만 표시 — [TradingView 지원 문서](https://www.tradingview.com/support/solutions/43000666265-how-deep-backtesting-works/)
- Bar Replay는 과거 가격을 한 봉씩 재생해 손으로 전략을 연습하게 하는 기능. Paper Trading은 실시간 시세에 가상 자금으로 주문을 넣는 계좌 — [TradingView 지원 문서(Bar Replay)](https://ru.tradingview.com/support/solutions/43000712747); [CMC Markets 가이드](https://www.cmcmarkets.com/en-gb/tradingview/how-to-backtest-trading-strategies-on-tradingview)

**Composer (미국, 노코드·AI 전략 빌더)**
- 전략('symphony')을 시각 편집기로 만들거나 평문 영어로 AI에게 설명해 만든다. 'Trade with AI'는 2025-10-21 출시. 회사 공개 수치는 누적 거래대금 200억 달러 이상, 주문 1,200만 건 이상(회사 자료, 사용자 성과 아님) — [Composer 도움말](https://help.composer.trade/article/217-9-creating-a-new-composer-symphony-with-ai); [Product Hunt 출시 페이지](https://www.producthunt.com/products/composer-2/launches); [Composer 홈페이지](https://www.composer.trade)
- 백테스트는 벤치마크나 다른 전략과 나란히 비교하는 형태로 보여준다. 독립 리뷰는 "첫 로그인에서 작동하는 백테스트까지 약 3시간", "실계좌 배포는 클릭 한 번"이라고 적었고, 노코드는 "이미 규칙이 분명한 사람에게 가장 잘 맞는다"고 평가. Trustpilot 평점 2.9(25건) — [Benzinga 리뷰](https://benzinga.com/money/composer-review); [dev.to 리뷰 2026-01](https://dev.to/pickuma/composer-review-automated-trading-strategies-without-writing-code-lj3); [Trustpilot](https://ca.trustpilot.com/review/composer.trade)

**Streak/Zerodha와 인도의 리테일 알고 규제**
- 인도 SEBI/NSE 리테일 알고 체계: 알고 주문은 브로커에 등록한 고정 IP에서만 인정. 벤더는 자체 고정 IP로 접속해 개별 사용자가 IP를 따로 둘 필요가 없다. 시행일은 2025-08-01 → 2025-10-01로 연기되었고 이후 "2026-04-01부터 전 브로커 의무"라는 2차 자료가 있어 날짜는 상충 — [Zerodha Z-Connect: SEBI 알고 규정 설명](https://zerodha.com/z-connect/business-updates/explaining-the-latest-sebi-algo-trading-regulations); [Zerodha Z-Connect: NSE 회람 개요](https://zerodha.com/z-connect/general/a-comprehensive-overview-of-nses-circular-on-the-new-retail-algo-trading-framework)

**국내 HTS/MTS 자동주문**
- 키움 영웅문 자동감시주문: 감시조건과 주문설정을 저장하면 조건 충족 시 **서버가** 자동 주문(HTS를 꺼도 동작). 스탑로스는 '보유종목'과 '잔고편입' 두 탭. 트레일링 스탑은 감시를 재시작하거나 조건을 수정하면 기준 고가·스탑가가 초기화되고, 기준가를 감시 시작 시점 현재가로 잡으면 손실 구간에서도 조건이 충족될 수 있다는 주의 문구가 도움말에 있다. 설정은 ID별이며 여러 단말 동시 사용 불가 — [키움 도움말 0621 주식 StopLoss](https://download.kiwoom.com/hero4_help_new/0621.htm); [키움 도움말 0624 자동감시주문](https://download.kiwoom.com/hero4_help_new/0624.htm)
- 미래에셋도 손실제한/이익실현 가격 도달 시 자동 또는 반자동으로 주문이 나가는 스탑로스 화면을 제공 — [미래에셋 도움말 0600](https://securities.miraeasset.com/kairos/0600.htm)

**로보어드바이저**
- 핀트(디셈버앤컴퍼니): 운용자산 2022년 1,306억 원 → 2026-04-29 기준 5,200억 원(약 4배), 고객 약 135만 명. 코스콤 테스트베드 기준 투자일임 '계약자 수'의 72%(운용자산 점유율 아님). 2025년 3월 퇴직연금 IRP 로보 일임 허용 — [벤처스퀘어](https://www.venturesquare.net/1079328/); [쿠키뉴스 2026-04-30](https://www.kukinews.com/article/view/kuk202604300022) (출처 매핑 근사)
- 로보어드바이저의 행동 효과(인도 브로커 포트폴리오 최적화 도구): 도입자는 처분효과·추세추종·순위효과가 줄었지만 완전히 없어지지는 않았고, 도입 후 **거래는 늘었으며 평균 성과 효과는 없었다** — [D'Acunto, Prabhala & Rossi, RFS 32(5), 2019](https://econpapers.repec.org/RePEc:oup:rfinst:v:32:y:2019:i:5:p:1983-2020.); [CESifo WP 6907](https://www.cesifo.org/DocDL/cesifo1_wp6907.pdf)

**eToro류 카피트레이딩**
- 실험 자산시장에서 다른 사람의 성과 정보를 보여주면 위험 감수가 유의하게 늘고, 직접 복사 기능이 있으면 더 커진다. 저자 결론은 "카피트레이딩은 과도한 위험 감수로 이어진다" — [Apesteguia, Oechssler & Weidenholzer, Management Science 66(12), 2020](https://econpapers.repec.org/RePEc:inm:ormnsc:v:66:y:12:i:2020:p:5608-5622); [CEPR 칼럼](https://cepr.org/article/copy-trading-platforms-and-risk-taking)

### Inferences
- 이 도구가 이미 가진 것(쉬운 문장 설명, 원화 순손익, 5단계 경로, 과거 검증 판정)은 성공 제품의 "쉬움" 공식과 일치한다. 차별화 여지는 성공 제품들이 **하지 않는** 쪽에 있다: 순위·급등락 목록·축하 연출을 두지 않고, 참여가 아니라 "규칙을 지켰는가/비용 후 얼마 남았는가"를 중심 지표로 삼는 것.
- '외상구매' 사례는 쉬운 말 원칙의 한계를 보여준다. 쉬운 말이 **위험의 무게를 줄이면** 규제기관도 문제 삼는다. 이 도구에서 "연습/실전", "손실 한도", "수수료·세금" 같은 말은 쉬우면서도 위험을 숨기지 않아야 한다.
- 키움 트레일링 스탑 도움말의 주의 문구(재시작 시 기준 초기화, 손실 구간에서도 발동 가능)는 자동주문의 대표적 "사용자가 오해하는 지점"이다. 이 도구의 신호 상세 화면에 "언제 파는가"를 설명할 때 같은 종류의 경계 조건(재시작·장 마감·데이터 끊김 시 어떻게 되는가)을 문장으로 밝히는 것이 필요하다.
- 토스증권의 전산 장애·주문 거부 보도와 MTS 사고 통계(8절 참고)는 "API가 항상 응답한다"는 가정이 위험함을 뜻한다. 홈의 한 문장 상태에 **데이터·연결 신선도**를 포함해야 한다.
- Composer의 "배포는 클릭 한 번"은 참여에는 좋지만 보호에는 반대 방향이다. 실전 전환은 의도적으로 느리게 설계하는 편이 근거(5절)에 맞다.

### Gaps
- 토스증권·Robinhood·Composer·TradingView 어느 곳도 **이용자 수익률, 잔존율, 과당매매 지표**를 공개한 자료를 찾지 못했다. 공개 수치는 가입자·MAU·거래대금뿐이다.
- 토스증권 '주식모으기'나 실시간 순위가 과열 투자를 부른다는 직접 비판 기사, toss.tech 디자인 블로그의 주문 흐름 설계 글은 이번 검색에서 확보하지 못했다.
- TradingView 이용자 수(흔히 인용되는 1억 명), Trade Republic, Public, 3Commas, Pionex, Streak의 온보딩·프리셋 세부, 한국투자증권 MTS 자동주문, 파운트·불릴레오 수치는 검색 한도 소진으로 확인하지 못했다(미검증).
- Robinhood S-1(2021)의 계정 수·중앙값 잔고, confetti 중단의 정확한 월은 미확인.

---

## 2. 앱 디자인이 투자자 행동·성과를 바꾼다는 연구

### Takeaway
증거가 가장 일관된 결론은 "주의를 끄는 장치(푸시 알림, 포인트·경품, 인기/급등 목록, 축하 연출)는 거래 횟수와 위험 감수를 늘리고, 그렇게 유도된 거래는 평균적으로 성과가 나쁘다"는 것이다. 반대로 정보를 **덜 자주, 덜 눈에 띄게** 보여주는 조치(단기 수익률 표시 금지, 매입가 숨기기, 자동 손절 사전 설정)는 거래량과 편향을 측정 가능하게 줄였다.

### Cited Findings

**주의 유발과 쏠림 (증거: 강)**
- Robinhood 이용자의 일별 최다 매수 종목은 이후 20일 비정상수익률 평균 −4.7%. 언론 요약은 극단적 쏠림 사건에서 약 9% 반전을 전한다. 앱 장애 때는 주목도 높은 종목의 거래가 유독 크게 줄었다 — [Barber et al., JF 2022](https://econpapers.repec.org/RePEc:bla:jfinan:v:77:y:2022:i:6:p:3141-3190); [UC Davis 보도자료](https://gsm.ucdavis.edu/news/what-effect-brokerage-robinhood-having-stock-market)
- 스마트폰으로 거래하면 같은 투자자라도 더 위험한 복권형·비분산 자산과 과거 급등·급락 종목을 더 산다(독일 은행 2곳 거래 자료, 투자자-시점 내 비교). 복권형 주식 매수 확률 증가폭은 "무조건부 평균의 67%"로 보고되나, 2차 보도는 8~10%p로 표현해 기준이 다르다. 효과는 장 마감 후에 더 크고, 다른 채널로 옮겨가지도 않는다 — [Kalda, Loos, Previtero & Hackethal, NBER WP 28363](https://www.nber.org/papers/w28363); [SAFE 보도자료 2021-04-27](https://safe-frankfurt.de/news-latest/all-news/news-view/trading-via-smartphone-tempt-people-to-gamble.html)

**푸시 알림 (증거: 강~중, 성과 방향은 혼재)**
- CFD 브로커의 표준화된 종목 푸시 알림을 이용한 이중차분: 알림은 위험 감수를 늘린다. 작업논문판 기준 알림 직후 거래는 레버리지가 평균 19%p 높았고, 젊은·남성·경험 적은 투자자에서 효과가 컸다. 후속 작업논문은 알림이 분산은 개선하지만 거래 성과는 낮춘다고 보고 — [Arnold, Pelster & Subrahmanyam, JFE 143(2), 2022](https://econpapers.repec.org/RePEc:eee:jfinec:v:143:y:2022:i:2:p:846-875); [작업논문판](https://www.jbs.cam.ac.uk/wp-content/uploads/2020/08/2020-06-conference-paper-arnold-pelster-subrahmanyam.pdf); ["Paying Attention"](https://voxeu.org/system/files/2023-02/Paying%20Attention.pdf)
- FCA 온라인 실험(9,000명 이상, 2024-06-20 발표, DEP 4종 검증): 푸시 알림은 거래 횟수 +11%, 포인트·경품 추첨은 +12%. 위험 자산 거래 비중은 각각 +8%, +6%. 여성은 알림·포인트에서, 18~34세는 대부분 기능에서 포트폴리오 위험이 더 커졌고, 금융 이해도가 낮은 집단은 깜빡이는 가격과 리더보드에서 거래가 더 늘었다. 다만 실험 종료 시점 포트폴리오가 통계적으로 더 위험해진 기능은 없었다 — [FCA Research Note](https://www.fca.org.uk/publications/research-notes/research-note-digital-engagement-practices-trading-apps-experiment); [FCA 보도자료](https://www.fca.org.uk/news/press-releases/fca-keeps-trading-apps-under-review-over-gaming-concerns)
- Robinhood의 "보유 종목 장중 5% 변동" 알림: 이후 15분간 리테일 거래 최소 +25%. 이 논문은 알림 이후 거래가 미래 수익률을 더 잘 예측한다며 "DEP는 무지한 거래만 늘린다"는 통념과 다르다고 주장 — [Moss, 작업논문](https://austinsmoss.github.io/austinmoss.me/Moss_JMP_How-Do-DEPs-Affect-Retail-Investor-Information-Processing-and-Trading.pdf); 반대로 Robinhood 알림이 처분효과를 악화시킨다는 작업논문도 있다 — [콜로라도대 작업논문](https://scholar.colorado.edu/downloads/pr76f4811)

**게이미피케이션 (증거: 강~중)**
- OSC(온타리오 증권위) 실험(2022-11, Staff Notice 11-796, 가상 자금 1만 달러 모의 거래): 매매할 때마다 경제적 가치가 거의 없는 포인트를 준 집단은 통제 집단보다 거래가 39% 많았다. '많이 거래된 종목' 목록을 본 집단은 그 목록 종목을 사고팔 확률이 14% 높았다. OSC는 이 목록을 현저성과 사회 규범의 결합으로 본다 — [OSC Staff Notice 11-796](https://www.osc.ca/sites/default/files/2022-11/sn_20221117_11-796_gamification-report.pdf); [OSC 보도자료](https://www.osc.ca/en/news-events/news/osc-study-finds-gamification-techniques-influence-retail-investors)
- 쾌락형 게이미피케이션(색종이, 성취 배지)은 평균 거래량을 약 5.17% 늘렸다. 게임형 플랫폼과 비게임형 플랫폼의 거래 격차 가운데 약 70%는 자기선택(그런 앱을 고르는 사람이 원래 많이 거래), 약 30%가 디자인 자체 효과. 가격 추세 알림은 신념이 정확한 사람의 학습은 돕고 틀린 사람의 실수는 강화한다 — [Chapkovski, Khapko & Zoican, Management Science 2024](https://pubsonline.informs.org/doi/epdf/10.1287/mnsc.2022.02650); [phys.org 요약](https://phys.org/news/2024-07-gamified-investment-sites-novice-investors.html)
- 같은 저자들의 후속 실험(605명): '보유 유도' 넛지는 위험 감수를 늘리고 변동성이 클 때 더 그렇다. 금융 이해도가 1표준편차 높아질 때마다 효과가 56% 줄어든다 — [Chapkovski, Khapko & Zoican, "Gamified risk-taking", JBEF 2025](https://ideas.repec.org/a/eee/beexfi/v46y2025ics2214635025000309.html)

**확인 빈도와 근시안적 손실회피 (증거: 강, 일반화에는 이견)**
- 결과 피드백을 매 라운드 받는 집단보다 3라운드마다 받는 집단이 위험 자산에 더 많이 투자했다(근시안적 손실회피) — [Gneezy & Potters, QJE 112(2), 1997](https://econpapers.repec.org/RePEc:oup:qjecon:v:112:y:1997:i:2:p:631-645.)
- 시카고상품거래소 전문 트레이더는 학부생보다 이 편향이 더 강했다 — [Haigh & List, Journal of Finance 60(1), 2005](https://ideas.repec.org/a/bla/jfinan/v60y2005i1p523-534.html)
- 전문 FX 트레이더 대상 자연 현장실험(가격 실현 86만 4천 건 이상): 가격 정보를 덜 자주 받은 트레이더가 위험을 약 1/3(33%) 더 지고 이익이 약 절반(53%) 더 컸다(초록 기준, 수치 원문 확인 권장) — [Larson, List & Metcalfe, NBER WP 22605](https://www.nber.org/papers/w22605)
- 반론: 937명 온라인 연구 등은 근시안적 손실회피가 일반적으로 관찰되지 않고 경험·성격 효과가 섞인다고 보고(검색 요약 기준, 원문 확인 필요) — [인스브루크대 작업논문 2021-12](https://www2.uibk.ac.at/downloads/c4041030/wpaper/2021-12.pdf)
- 이스라엘 규제 자연실험: 2010년부터 퇴직연금 펀드가 12개월 미만 수익률을 표시하지 못하게 하자(투자자가 직접 계산은 가능) 최근 1개월 수익률에 대한 자금 민감도가 떨어지고, **거래량이 비교 집단 대비 약 30% 감소**했으며, 가계가 더 위험한 펀드로 이동했다. 저자는 이것이 더 나은 결정인지는 판단하지 않는다 — [Shaton, FEDS 2017-043](https://www.federalreserve.gov/econres/feds/the-display-of-information-and-household-investment-behavior.htm); [Chicago Booth Review](https://www.chicagobooth.edu/review/how-to-get-investors-to-take-long-term-view)

**처분효과와 인터페이스 (증거: 강, 실험실)**
- 매입가를 화면에 크게 보여주는 조건에서는 처분효과가 나타났고, 매입가를 아예 표시하지 않은 조건에서는 처분효과가 25% 작았다 — [Frydman & Rangel, JEBO 107, 2014](https://ideas.repec.org/a/eee/jeborg/v107y2014ipbp541-552.html)
- 손절·익절 자동 매도를 미리 걸 수 있게 하면 처분효과가 유의하게 줄었다. 줄어든 이유는 손실 실현이 늘어서이고(이익 실현 비율은 비슷), **계획을 상기시키는 알림만 준 조건은 효과가 없었다** — [Fischbacher, Hoffmann & Schudy, RFS 30(6), 2017](https://econpapers.repec.org/RePEc:oup:rfinst:v:30:y:2017:i:6:p:2110-2129.)

**색상 (증거: 강, 한국 직접 증거 없음)**
- 8개 실험: 금융 데이터를 빨강으로 표시하면 위험 선호·미래 수익 기대·거래 결정이 달라진다. 빨강은 검정 대비 위험 감수를 15~30% 낮추고 손실 뒤 비관적 기대를 오래 끌었다. 노랑·파랑은 같은 효과가 없었고, 색각 이상자에게는 나타나지 않았으며, 빨강이 번영을 뜻하는 중국에서는 약했다 — [Bazley, Cronqvist & Mormann, Management Science 67(9), 2021](https://econpapers.repec.org/RePEc:inm:ormnsc:v:67:y:2021:i:9:p:5616-5641); [KU News 2021-03-29](https://news.ku.edu/news/article/2021/03/29/red-color-impacts-investor-behavior-financial-research-reveals)

**과잉거래의 기저율 (증거: 강)**
- 미국 할인 브로커 66,465가구(1991~1996): 가장 많이 거래한 가구의 연 수익률 11.4% 대 시장 17.9%(초기 판본 수치, 다른 판본은 회전율 상위 20%의 순수익률 10.0% 대 시장 17.1%) — [Barber & Odean, Journal of Finance 55(2), 2000](https://econpapers.repec.org/RePEc:bla:jfinan:v:55:y:2000:i:2:p:773-806); [저자 페이지](https://faculty.haas.berkeley.edu/odean/papers/returns/returns.html)
- 브라질 주가지수 선물 데이트레이딩(2013~2015 시작자): 300일 이상 지속한 사람의 97%가 손실, 은행 창구 직원 급여 이상을 번 사람은 0.4~0.5%(판본별) — [Chague, De-Losso & Giovannetti, "Day Trading for a Living?"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101); [Quantpedia 요약](https://quantpedia.com/retail-day-trading-is-an-uphill-battle/)
- 대만 데이트레이더(1992~2006): 수수료 차감 후 예측 가능하게 초과수익을 내는 사람은 1% 미만, 전형적인 반기에 10명 중 8명 이상이 손실 — [Barber, Lee, Liu & Odean, Journal of Financial Markets 18, 2014](https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html); [작업논문](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf)
- 한국: 자본시장연구원(국내 4개 증권사 표본, 2020년 3~10월 일별 자료)은 거래회전율·일중거래 비중·종목교체율이 높을수록 초과수익률이 낮고, 처분효과·단기 군집거래와 이후 수익률 반전을 확인했다. 코로나19 이후 1년간 개인의 거래이익 약 13조 원에 대해 세금·수수료가 13.7조 원이었다. 모바일 투자자는 회전율·일중거래 비중이 높고 성과가 저조 — [파이낸셜뉴스 2021-04-13](https://www.fnnews.com/news/202104131912345956); [뉴데일리 2021-02-26](https://biz.newdaily.co.kr/site/data/html/2021/02/26/2021022600078.html); [자본시장연구원 보고서](https://www.kcmi.re.kr/report/report_view?report_no=1243)

**한국 규제 동향 (2024~2026)**
- 금융감독원은 거래금액·거래횟수에 따라 현금·상품권을 주는 증권사 이벤트를 2027년 1월부터 금지하는 방안을 추진(2026-10-28 보도, 과당매매 유인 차단 취지. 수수료 할인은 허용, 레버리지·인버스 ETP와 해외 고위험 상품 이벤트도 제한 대상). 보도 시점 기준 '추진'이며 확정 규정은 아님 — [비즈워치 2026-10-28](https://news.bizwatch.co.kr/article/market/2026/10/28/0010); [토요경제](https://sateconomy.co.kr/news/view/1065587352031607); [SBS Biz](https://biz.sbs.co.kr/amp/article/20000342648)
- 2025-12-15부터 개인이 해외 파생상품을 처음 거래하려면 사전교육 1시간 이상 + **모의거래 3시간 이상**을 이수해야 한다(해외 레버리지 ETP는 사전교육 1시간). 배경 수치로 개인의 해외 파생 손실이 연평균 약 4,500억 원대(보도별 4,490억~4,580억)로 제시됨 — [데일리안](https://www.dailian.co.kr/news/view/1502047/); [경향신문 2025-11-16](https://www.khan.co.kr/article/202511161310001/); [아시아경제 2025-12-14](https://core.asiae.co.kr/article/2025121413165630022)
- 그 밖에 2026년 금감원은 미수거래 유도 영업 자제 요청(6월), 준법감시인 간담회에서 상품 기획 단계부터 투자자 보호 강화 주문(9월), 해외주식 마케팅 경고 등을 이어갔다 — [머니투데이 2026-06-24](https://www.mt.co.kr/article/2026062409233612697); [토요경제](https://sateconomy.co.kr/news/view/1065580430228390); [더팩트](https://news.tf.co.kr/read/economy/2275219.htm)

### Inferences
- **참여↑·성과↓ 가 확인된 패턴**: 포인트/보상(+39% 거래), 인기·급등 목록(+14% 해당 종목 거래, 쏠림 종목 −4.7%), 가격 변동 푸시(+11~25% 거래, 레버리지↑), 축하 연출(+5%), 스마트폰 채널 자체(복권형 종목↑). 이 도구는 이 다섯 가지를 "넣지 않을 것 목록"으로 명문화할 수 있다.
- 확인 빈도 연구의 방향을 주의해서 읽어야 한다. 덜 자주 보면 **위험을 더 진다**(장기 투자자에게는 대체로 이득). 이 도구의 목적은 위험을 더 지게 하는 것이 아니라 **자동 규칙에 손대지 않게** 하는 것이므로, 적용 포인트는 "장중 평가손익을 덜 눈에 띄게 하고, 평가 단위를 하루/주 단위로 묶는다"이다. Shaton의 거래량 −30%가 이 목적에 가장 직접적인 근거다.
- Fischbacher 등의 결과는 설계 원칙을 하나 준다: **알림(상기)은 약하고 자동 실행(사전 약속)이 강하다.** 손절 계획을 푸시로 알려주는 것보다 규칙이 스스로 실행되는 구조가 처분효과를 줄인다. 자동매매 도구의 본질적 장점이므로 "사람이 중간에 끼어들 수 있는 지점"을 최소화하는 것이 근거에 맞다.
- 한국은 빨강=상승이므로 Bazley 등의 "빨강=위험 회피" 효과가 그대로 적용된다고 볼 수 없다(중국에서 약화). 한국 이용자 대상 직접 증거가 없으니 색에 의미를 과하게 싣지 말고, 색 관례는 따르되 요약 화면의 채도를 낮추는 정도가 안전한 선택이다.
- 한국 당국이 해외 파생에 "모의거래 3시간"을 의무화한 것은 이 도구의 "연습→실전 5단계"와 같은 방향의 제도적 선례다. 기획서에서 단계 설계의 정당화 근거로 쓸 수 있다.
- Chapkovski 등의 "격차의 70%는 자기선택"은 반대 방향 교훈도 준다. 디자인을 얌전하게 만든다고 과잉거래 성향이 사라지지는 않으므로, 디자인 절제에 더해 **구속력 있는 한도**(5절)가 필요하다.

### Gaps
- OSC의 2024년 후속 보고서 "Gamification Revisited: New Experimental Findings in Retail Investing"(소셜 피드·카피트레이딩 계열 실험)은 제목과 존재만 확인했고 수치는 열람하지 못했다 — [OSC 페이지](https://osc.ca/en/gamification-revisited-new-experimental-findings-retail-investing). OSC 2022 실험의 표본 수(약 2,400명으로 기억)는 미검증.
- FCA 실험에서 리더보드·깜빡이는 가격의 전체 표본 평균 효과 크기는 확인하지 못했다(하위집단 효과만 확인).
- 푸시 알림이 수익률에 미치는 순효과는 연구마다 다르다(Moss: 정보성 개선 / Arnold 등: 성과 하락 / 콜로라도 논문: 처분효과 악화). 주식 현물·한국 시장 대상 연구는 찾지 못했다.
- Sicherman, Loewenstein, Seppi & Utkus "Financial Attention"(타조 효과), Benartzi & Thaler(1995) 원 논문, 금융위·금감원의 MTS 게이미피케이션 **직접** 가이드라인은 검색 결과에서 확인하지 못했다. 한국 규제의 중심은 UI 요소가 아니라 거래 연동 보상·고위험 상품 이벤트·용어였다.
- 수수료·비용 표시의 현저성이 개인 트레이더 행동에 미치는 효과를 직접 검증한 실험은 이번 조사에서 찾지 못했다(원화 순손익 표시의 근거는 기저율 연구에서 간접 추론).

---

## 3. 설명 가능성과 자동화에 대한 신뢰

### Takeaway
설명은 양날의 검이다. 평이한 이유 설명은 이해를 돕지만, 연구는 설명이 **틀린 추천에 대한 의존까지 높일 수 있음**을 보여준다. 근거가 있는 처방은 (1) 사용자에게 작지만 실제적인 조정 권한을 주고, (2) 설명 옆에 불확실성·과거 적중 기록·표본 수를 함께 두고, (3) 중요한 결정 지점에서는 사용자가 한 번 스스로 생각하게 만드는 것이다. 백테스트는 "시도한 조합 수"를 숨기면 쉽게 과적합되고, 관례적 경고 문구는 효과가 약하다.

### Cited Findings
- 알고리즘 회피 극복: 사람들은 불완전한 알고리즘이라도 예측을 **조금이라도** 수정할 수 있으면 훨씬 더 많이 사용했고 성과도 좋아졌다. 수정 허용 폭의 크기에는 둔감했다(원하는 것은 '더 많은 통제'가 아니라 '약간의 통제'). 수정 권한을 받은 사람은 과정 만족도가 높고 알고리즘을 더 우수하다고 믿었으며 이후에도 알고리즘을 선택했다 — [Dietvorst, Simmons & Massey, Management Science 64(3), 2018](https://ideas.repec.org/a/inm/ormnsc/v64y2018i3p1155-1170.html); [논문 PDF](https://marketing.wharton.upenn.edu/wp-content/uploads/2020/07/Dietvorst-Overcoming-Algorithm-Aversion.pdf)
- 설명과 과신뢰: 설명은 AI가 틀렸을 때에도 추천에 대한 의존을 높였다. 설명이 내용으로 평가되기보다 '유능함의 신호'로 읽히고 예측에 닻을 내리게 한다는 해석 — [Bansal et al., "Does the Whole Exceed its Parts?", CHI 2021](https://aiweb.cs.washington.edu/ai/pubs/bansal-chi21.pdf)
- 인지 강제 기능(답을 보기 전에 먼저 스스로 판단하게 하는 등)은 단순 설명 제공보다 AI 과의존을 유의하게 줄였다 — [Buçinca, Malaya & Gajos, "To Trust or to Think"](https://ar5iv.labs.arxiv.org/html/2102.09692)
- 설명 유형에 따라 다르다: 사례 기반 설명은 과의존을 줄였고 특징 기반 설명은 그렇지 않았다는 결과가 있다 — ["Evaluating the Influences of Explanation Style on Human-AI Reliance"](https://arxiv.org/html/2410.20067v1). 조건에 따라 설명이 과의존을 줄일 수 있다는 연구도 있다(제목 수준 확인) — ["Explanations Can Reduce Overreliance on AI Systems During Decision-Making"](https://ar5iv.labs.arxiv.org/html/2212.06823)
- 설명과 불확실성 표시는 함께 쓸 수 있고, 모델 확신도와 사용자 자신의 확신도 모두 의존·이해·신뢰에 영향을 준다 — [Papantonis & Belle, "Why not both?"](https://ar5iv.labs.arxiv.org/html/2304.14130)
- 로보어드바이저는 편향을 줄였지만 거래를 늘렸고 평균 성과는 바꾸지 못했다(1절) — [D'Acunto, Prabhala & Rossi, RFS 2019](https://econpapers.repec.org/RePEc:oup:rfinst:v:32:y:2019:i:5:p:1983-2020.)
- 백테스트 과적합: 비교적 적은 수의 전략 조합만 시험해도 높은 성과는 쉽게 얻어진다. 대부분의 제안서가 시도한 조합 수를 밝히지 않아 과적합 정도를 평가할 수 없다. 기억 효과가 있는 시계열에서는 과적합 전략의 표본 외 기대수익이 0이 아니라 **음수**가 된다. 동반 논문은 해당 데이터에서 45개를 넘는 변형을 시험하면 참 샤프비율이 0 이하여도 우연히 1.0 이상이 나올 수 있다고 계산 — [Bailey, Borwein, López de Prado & Zhu, "Pseudo-Mathematics and Financial Charlatanism"](https://scholarworks.wmich.edu/math_pubs/40/); [논문 PDF](https://carmamaths.org/jon/backtest.pdf)
- Deflated Sharpe Ratio는 다중 시험에 따른 선택 편향과 비정규 수익 분포를 보정한다. 여러 시도 중 최고 성과의 분포는 임의의 한 시도의 분포와 다르기 때문 — [Bailey & López de Prado, SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- "과거 성과가 미래를 보장하지 않습니다"류 문구: SEC 의무 경고가 "심각하게 부적절"하며 더 강한 경고는 "높은 수익은 대체로 지속되지 않는다"를 분명히 해야 한다는 주장. 원 실험 논문(2010)의 결과 수치는 직접 확인하지 못했고, 2차 보도는 "많은 투자자가 그 경고를 무시한다"고 요약 — [Mercer, Palmiter & Taha, "Worthless Warnings?", JELS 7(3), 2010](https://ideas.repec.org/a/wly/empleg/v7y2010i3p429-459.html); [Palmiter & Taha, Georgia Law Review 46(2)](https://digitalcommons.law.uga.edu/glr/vol46/iss2/3)
- 위험 전달 형식: 아이콘 배열은 수리력이 낮은 사람과 고령자의 (의료) 위험 이해를 도왔다 — [Galesic, Garcia-Retamero & Gigerenzer, 2009](https://pure.mpg.de/pubman/item/item_2099767_5/component/file_2562291/MG_Using_2009.pdf). 아이콘은 백분율·자연빈도 대비 더 정확한 추정과 비율 추론을 이끌었다 — [Psychological Research 2018](https://link.springer.com/article/10.1007/s00426-018-1041-4). 다만 자연빈도의 이점은 맥락에 따라 안정적이지 않다는 반대 결과도 있다(제목 수준 확인).
- 반복 위험 선택 과제에서 아이콘 배열: 무작위로 흩어 놓은 배열은 손실 확률이 더 크게 지각되어 위험 감수를 줄였다(실험실 도박 과제이며 투자 공시 형식 실험은 아님) — [Judgment and Decision Making 17(2), 2022](https://dlab.sauder.ubc.ca/sjdm/journal/21/210615/jdm210615.html)
- FCA "Beyond disclosure — slow down and think": 행동과학을 반영한 위험 고지는 주로 **현저성과 단순한 문구**를 통해 위험 이해를 높였다 — [FCA 연구 글](https://www.fca.org.uk/publications/research-articles-fca-research/beyond-disclosure-high-risk-investments-slow-down-and-think)

### Inferences
- 현재의 "왜 샀고 언제 파는지 평문 + 차트" 설명은 이해에는 좋지만 Bansal 등에 비추면 그 자체로 **신뢰를 과하게 올릴 위험**이 있다. 설명 카드에 반드시 붙일 세 가지: (a) 이 유형 신호의 과거 기록을 빈도로("같은 조건 지난 40번 중 23번 이익, 17번 손실"), (b) 표본이 적으면 "아직 판단하기 이름"이라는 명시, (c) 이 규칙이 잘 틀리는 상황 한 줄.
- Dietvorst의 "약간의 통제"는 이 도구에서 **안전한 방향의 손잡이만** 주는 것으로 옮길 수 있다: 일시정지, 1회 투자금 상한 낮추기, 관심종목 제외. 손절을 넓히거나 한도를 올리는 손잡이는 즉시 적용하지 않는다(5절 Heimer 등 근거).
- "과거로 테스트" 화면의 통과/실패/보류 판정은 Bailey 등의 근거와 잘 맞는다. 보강할 점: 판정에 **몇 가지 설정을 시험해 보았는지**를 누적 기록해 보여주고(설정을 많이 바꿔 볼수록 통과 기준을 엄격하게), 단일 수익률 대신 "거래 수, 이긴 횟수/진 횟수, 가장 나빴던 구간, 비용 차감 후 범위"를 기본 표시로 삼고, 검증에 쓰지 않은 기간(표본 외) 결과를 따로 보여준다.
- 관례적 면책 문구는 효과가 약하므로, 같은 내용을 **구체적이고 눈에 띄는 한 문장**으로 바꾼다. 예: "과거에 통과한 규칙도 실제로는 절반 이하의 성과를 내는 일이 흔합니다. 이 결과는 설정을 N번 바꿔 본 뒤 가장 좋았던 것입니다."
- 위험은 백분율보다 "100번 중 N번" 빈도 표현 + 단순한 아이콘 배열이 비전문가에게 유리할 가능성이 높다. 다만 근거가 의료 분야 중심이라 **중간 강도의 추론**으로 표시해야 한다.
- 실전 전환, 한도 상향처럼 드문 고위험 결정에는 인지 강제(예: "지난 20번 연습 거래에서 손실 난 횟수는 몇 번이었을까요?"를 먼저 묻고 실제 값을 보여주기)를 쓰고, 일상 화면에는 쓰지 않는다(매번 쓰면 피로와 불만이 커진다는 것이 해당 연구의 알려진 절충).

### Gaps
- Zhang, Liao & Bellamy(2020, 확신도 표시가 신뢰 보정에 미치는 효과)의 본문 결과, Buçinca 등 연구의 표본·효과 크기는 직접 확인하지 못했다(검색 요약은 저자를 다르게 적기도 했다).
- **비전문 개인 트레이더에게 백테스트를 어떤 형식으로 보여줄 때 과신이 줄어드는가**를 직접 실험한 연구는 찾지 못했다. 위 권고는 과적합 통계 문헌 + 위험 전달 문헌에서의 추론이다.
- 로보어드바이저 UX(온보딩 설문, 성과 표시)의 사용자 연구, 투자 위험 고지 형식(위험 등급 표시 등)의 리테일 대상 이해도 실험은 확보하지 못했다.

---

## 4. 결과를 개선하는 의사결정 보조 장치 (한도, 사전 약속, 일지, 모의→실전)

### Takeaway
사전 약속 장치는 **구속력이 있을 때만** 작동한다. 실제 트레이더는 손실이 쌓이면 스스로 정한 손실 한도를 넓히고, 한도를 "설정하라"고 권유만 하는 것은 순손실을 바꾸지 못했다. 반면 자동 실행되는 손절은 처분효과를 줄였다. 매매 일지와 모의투자의 효과에 대한 통제된 연구는 놀랄 만큼 부족하다.

### Cited Findings
- 사전에 이익·손실 한도를 정해야 하는 온라인 브로커 자료: 계획은 손실에서 빠져나오는 것이었지만 실제 행동은 달랐고, 누적 손실에 대한 **가장 흔한 반응은 손실 한도를 넓히는 것**이었다. 실험실에서도 비슷한 결과 — [NBER 학회 발표 논문](https://conference.nber.org/conf_papers/f134975/f134975.pdf); [Chicago Booth Review "The Two Big Strategic Mistakes That Investors Make"](https://www.chicagobooth.edu/review/two-big-strategic-mistakes-investors-make)
- 자동 손절·익절 주문은 처분효과를 인과적으로 줄였고 계획 상기 알림은 효과가 없었다(2절 재인용) — [Fischbacher, Hoffmann & Schudy, RFS 2017](https://econpapers.repec.org/RePEc:oup:rfinst:v:30:y:2017:i:6:p:2110-2129.)
- 온라인 도박 무작위 실험(핀란드 사업자): 가입 시·첫 입금 전·첫 입금 후에 자발적 입금 한도 설정을 **권유**해도 권유받지 않은 고객과 이후 순손실 차이가 없었다(한도 설정 비율은 올랐다). 한도를 올리거나 없애는 행동은 문제 도박의 표지일 수 있다. 사전 약속의 효과에 대해 체계적 문헌고찰 3편은 명확한 증거를 찾지 못했다 — [Ivanova, Magnusson & Carlbring, Frontiers in Psychology 2019](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.00639/full)
- 냉각 기간: 영국 FCA는 고위험 투자에 최소 24시간 냉각 기간을 의무화했고, 점검 결과 모든 대상 회사가 이를 구현했다. 냉각 기간이 끝나면 "계속"과 "그만두기"를 **동등한 눈에 띔**으로 제시해야 하고, 투자 유인 인센티브는 금지 — [FCA 다수 회사 점검 보고](https://www.fca.org.uk/publications/multi-firm-reviews/financial-promotions-high-risk-investments)
- 마찰의 효과와 비용: FCA 실험에서 긍정적 마찰은 부적절한 자기 인증을 줄였지만(여전히 상당 비율은 통과), 일부 마찰은 사람들을 절차에서 아예 이탈하게 했다 — [FCA "Beyond disclosure … slow down and think"](https://www.fca.org.uk/publications/research-articles-fca-research/beyond-disclosure-high-risk-investments-slow-down-and-think)
- 모의→실전 격차(AI 암호화폐 전략 실험, arXiv 프리프린트 1건): 네 방법 중 셋이 실전에서 모의보다 누적수익이 낮았고 격차는 최대 6.38%p. 그래도 모의투자는 백테스트보다 실전에 가까웠다(알파 기준 평균 절대 격차 58.85%p → 28.51%p). 남은 격차는 주로 체결가·주문 금액의 차이에서 나왔다 — [arXiv 2609.34510](https://arxiv.org/pdf/2609.34510)
- 실무 자료의 일치된 설명: 모의투자는 완벽한 체결을 가정하고, 실전은 슬리피지·부분 체결·호가 공백을 겪으며, 심리적 압박이 없다(통제 연구 아님) — [TradersPost 블로그](https://blog.traderspost.io/article/paper-trading-vs-live-results)
- 행동 통계: Alpaca Trading API 이용자 중 2024-06-01~2025-05-31에 실거래를 한 사람의 67.2%는 모의 단계 없이 곧바로 실전으로 시작했다(성과 자료 아님) — [Alpaca "Paper Trading vs. Live Trading"](https://alpaca.markets/learn/paper-trading-vs-live-trading-a-data-backed-guide-on-when-to-start-trading-real-money)
- 한국의 제도적 선례: 해외 파생상품 첫 거래 전 모의거래 3시간 의무(2절) — [데일리안](https://www.dailian.co.kr/news/view/1502047/)
- 매매 일지: 통제 실험을 찾지 못했다. 유일한 정량 자료는 일지 도구 업체의 관찰 자료(자기선택 편향)이며, 브로커 가이드는 "일지가 더 나은 결과를 보장하지 않는다"고 명시 — [CMC Markets 가이드](https://www.cmcmarkets.com/en-au/cfd/learn/trading-guides/how-to-use-a-trading-journal); [JournalPlus(업체 자료)](https://journalplus.co/blog/trading-journal-roi-study)

### Inferences
- 설계 규칙으로 옮기면: **한도는 기본값으로 켜져 있고, 조이는 것은 즉시, 푸는 것은 지연**(다음 거래일 장 시작부터 적용 + 한 번 더 확인). Heimer 계열 결과(손실 중 한도 확대)와 도박 연구(권유만으로는 무효)를 함께 만족시키는 유일한 형태다.
- 일일 손실 한도·하루 최대 거래 수·연속 손실 후 당일 중단은 "알림"이 아니라 **엔진이 강제하는 규칙**이어야 한다(Fischbacher: 상기는 무효, 자동 실행은 유효). 화면에는 "오늘 한도의 몇 %를 썼는지"만 보여준다.
- 실전 전환에는 FCA식 냉각을 차용할 수 있다: "실전 전환 신청 → 24시간 뒤에야 활성화 → 활성화 화면에서 '그대로 연습 유지'와 '실전 시작'이 같은 크기 버튼". 단일 사용자 도구에서도 구현 비용이 낮다.
- 모의 결과를 그대로 믿게 하면 안 된다. 연습 거래 손익에 **보수적 체결 가정**(다음 틱/다음 호가 체결, 슬리피지 가산)을 적용하고, 화면에 "연습 결과는 실제보다 좋게 나오는 경향이 있습니다(체결·심리 차이)"를 수치 예시와 함께 고정 표시한다. 실전 소액 단계에서는 "같은 신호의 연습 체결가 대 실제 체결가" 차이를 지표로 보여준다.
- 67.2%가 모의를 건너뛴다는 행동 통계는 "5단계 경로를 건너뛸 수 없게 하는 것" 자체가 보호 장치임을 뜻한다.
- 일지는 증거가 약하므로 사용자가 글을 쓰게 강요하지 말고, **자동으로 채워지는 복기**(규칙대로 실행된 비율, 사람이 개입한 거래와 그 결과를 규칙만 따랐을 때와 비교)로 구현하는 편이 비용 대비 낫다. 효과 가설로 표시하고 과신하지 않는다.

### Gaps
- 개인 주식 트레이더에게 구속력 있는 일일 손실 한도·거래 횟수 한도·잠금(lock-out)을 무작위로 부여해 실현 손실을 측정한 연구는 찾지 못했다. 위 권고는 브로커 관찰 자료 + 도박 무작위 실험 + 손절 실험에서의 추론이다.
- 위 NBER 논문의 정식 제목·저자(Heimer, Iliewa, Imas & Weber, "Dynamic Inconsistency in Risky Choice"로 기억)와 수치는 검색 한도 소진으로 재확인하지 못했다(미검증).
- 체크리스트가 트레이딩 성과를 개선한다는 직접 증거, 모의투자가 초보자의 실전 성과를 개선한다는 통제 연구, 단계적 증액(소액 실전)의 효과 연구는 찾지 못했다. arXiv 2609.34510은 프리프린트 1건이고 암호화폐·AI 전략 대상이라 일반화에 주의.

---

## 5. 알림 설계

### Takeaway
거래 앱의 푸시는 거래를 11~25% 늘리고 위험 감수를 키우는 것으로 측정되었으므로, 자동 규칙을 지켜보기만 하면 되는 도구에서는 **알림을 적게, 묶어서, 행동이 필요한 경우에만** 보내는 것이 근거에 맞다. 알림을 하루 3번으로 묶으면 스트레스가 줄고, 알림을 완전히 끄면 오히려 불안이 늘었다.

### Cited Findings
- 푸시 알림 → 거래 +11%, 위험 거래 비중 +8%(FCA, 9,000명 이상) — [FCA Research Note 2024](https://www.fca.org.uk/publications/research-notes/research-note-digital-engagement-practices-trading-apps-experiment)
- 가격 5% 변동 알림 → 15분 내 리테일 거래 최소 +25% — [Moss 작업논문](https://austinsmoss.github.io/austinmoss.me/Moss_JMP_How-Do-DEPs-Affect-Retail-Investor-Information-Processing-and-Trading.pdf)
- 종목 푸시 직후 거래의 레버리지 +19%p, 젊은·남성·저경험 투자자에서 더 큼 — [Arnold, Pelster & Subrahmanyam 작업논문](https://www.jbs.cam.ac.uk/wp-content/uploads/2020/08/2020-06-conference-paper-arnold-pelster-subrahmanyam.pdf)
- 가격 추세 알림은 신념이 틀린 투자자의 실수를 강화. 게임형 스타일 선호 투자자는 가격 상승 알림 뒤 매도 확률이 약 32% 높고 하락 알림 뒤 보유 확률이 약 38% 높았다(언론 요약) — [Chapkovski, Khapko & Zoican 2024](https://pubsonline.informs.org/doi/epdf/10.1287/mnsc.2022.02650); [phys.org](https://phys.org/news/2024-07-gamified-investment-sites-novice-investors.html)
- 알림 묶음 무작위 현장실험(237명, 2주, 인도): 알림을 하루 3회 예측 가능한 시각에 묶어 받은 집단은 주의력·생산성·기분이 좋아지고 스트레스가 낮았다. 알림을 전혀 받지 않은 집단은 이점이 거의 없고 불안이 높았다 — [Fitz, Kushlev et al., Computers in Human Behavior 2019 (Duke Scholars)](https://scholars.duke.edu/publication/1402953); [저자 해설](https://communities.springernature.com/posts/batching-notifications-can-improve-attention-well-being-and-productivity)
- 손절 계획을 상기시키는 알림은 처분효과를 줄이지 못했다 — [Fischbacher, Hoffmann & Schudy 2017](https://econpapers.repec.org/RePEc:oup:rfinst:v:30:y:2017:i:6:p:2110-2129.)
- 푸시는 뉴스 소비와 종목 탐색을 유발한다(약 7%의 알림이 기술 문제로 도달하지 못한 것을 이용한 준실험, 예비 결과) — [Chen, INSEAD 작업논문](https://afajof.org/management/viewp.php?n=135464)

### Inferences
- 현재의 "연습 거래가 열리거나 닫힐 때마다 푸시"는 건당 실시간 알림이다. 근거에 비추면 기본값을 다음처럼 바꾸는 것이 낫다.
  - **기본: 장 마감 후 하루 1회 요약**(오늘 거래 수, 비용 차감 후 원화 손익, 규칙 준수 여부, 내일 할 일 "없음").
  - **즉시 알림은 '사람이 해야 할 일이 있는 경우'만**: 연결 끊김·API 키 만료·주문 실패·일일 손실 한도 도달로 자동 중단됨·데이터 지연. 제목 첫머리에 "조치 필요/조치 불필요"를 붙인다.
  - 건당 체결 알림은 선택 사항(끄기가 기본)으로 내리고, 켜더라도 가격 변동률·"지금 +3.2%" 같은 자극적 수치 대신 "규칙대로 매수함. 할 일 없음"으로 쓴다.
  - **가격 변동·급등락·관심종목 알림은 만들지 않는다**(FCA·Arnold·Moss 근거).
- 알림을 완전히 없애는 것은 답이 아니다(Fitz 등: 무알림 집단의 불안↑). 예측 가능한 시각의 요약이 "확인하러 자주 들어오는 행동"을 대체한다.
- 조용한 시간(장 시작 전·야간), 알림 채널별 심각도 분리(Telegram/ntfy의 우선순위 기능 활용)는 실무적으로 타당하지만 거래 맥락의 직접 증거는 없다 — 약한 근거로 표시.
- 알림 문구에도 "축하 금지" 원칙을 적용한다: 이익 실현 알림에 이모지·감탄 표현·연속 기록을 쓰지 않는다(2절 게이미피케이션 근거).

### Gaps
- 경보 피로(alert fatigue)의 정량 연구(임상 의사결정 지원의 경고 무시율 등)와 "행동 가능한 알림"의 조건에 대한 HCI 연구는 검색에서 확보하지 못했다.
- 묶음 알림과 실시간 알림을 **거래 맥락**에서 비교한 연구, 조용한 시간의 효과 연구는 찾지 못했다. Fitz 등은 일반 스마트폰 알림 대상이며 인도 표본이다.

---

## 6. 비전문가를 위한 대시보드·시각화

### Takeaway
"한눈에 보는 상태"에서 무엇을 **가장 크게** 보여주느냐가 행동을 바꾼다. 단기 수익률·매입가·빨간 숫자를 크게 보여줄수록 거래와 편향이 늘어난다는 증거가 있으므로, 대표 숫자는 실시간 평가손익이 아니라 "비용 차감 후 누적 원화 손익 + 규칙이 정상 작동 중인지"가 되어야 하고, 세부는 단계적으로 펼쳐 보이게 한다.

### Cited Findings
- 12개월 미만 수익률 표시를 금지하자 거래량이 약 30% 줄었다(정보 자체는 계산 가능했음에도) — [Shaton, FEDS 2017-043](https://www.federalreserve.gov/econres/feds/the-display-of-information-and-household-investment-behavior.htm)
- 매입가를 표시하지 않으면 처분효과가 25% 작아진다 — [Frydman & Rangel 2014](https://ideas.repec.org/a/eee/jeborg/v107y2014ipbp541-552.html)
- 빨강 표시는 서구 표본에서 위험 감수를 15~30% 낮추고 비관을 오래 끌지만, 색각 이상자에게는 효과가 없고 빨강이 번영을 뜻하는 중국에서는 약하다 — [Bazley, Cronqvist & Mormann 2021](https://econpapers.repec.org/RePEc:inm:ormnsc:v:67:y:2021:i:9:p:5616-5641)
- 깜빡이는 가격과 리더보드는 금융 이해도가 낮은 집단의 거래를 더 늘렸다 — [FCA Research Note 2024](https://www.fca.org.uk/publications/research-notes/research-note-digital-engagement-practices-trading-apps-experiment)
- '많이 거래된 종목' 목록은 해당 종목 거래 확률을 14% 높였다 — [OSC Staff Notice 11-796](https://www.osc.ca/sites/default/files/2022-11/sn_20221117_11-796_gamification-report.pdf)
- 행동과학 기반 위험 고지는 현저성과 단순한 문구로 이해를 높였다 — [FCA "Beyond disclosure"](https://www.fca.org.uk/publications/research-articles-fca-research/beyond-disclosure-high-risk-investments-slow-down-and-think)
- 개인의 거래이익(약 13조 원)보다 세금·수수료(13.7조 원)가 컸던 국내 사례는 비용 차감 표시의 필요성을 보여준다 — [뉴데일리 2021-02-26](https://biz.newdaily.co.kr/site/data/html/2021/02/26/2021022600078.html)
- 토스증권 WTS는 보유·관심종목 사이드창을 항상 떠 있는 PIP로 제공한다(참여 지향 설계의 예) — [뉴데일리 2025-10-28](https://biz.newdaily.co.kr/site/data/html/2025/10/28/2025102800134.amp.html)

### Inferences
- 홈의 "한 문장 상태"는 유지하되 내용 우선순위를 다음처럼 잡는다: ① 시스템이 정상인가(마지막 시세 수신 시각, 엔진 상태) ② 오늘 사람이 할 일이 있는가(대부분 "없음") ③ 비용 차감 후 누적 원화 손익(기간: 이번 주/이번 달 기본, '오늘'은 한 단계 아래).
- 오른쪽 패널의 '실시간' 영역과 보유 종목의 장중 평가손익은 Shaton·Frydman 근거상 **기본 접힘**이 낫다. 보유 종목 줄에는 매입가·현재 수익률 대신 "규칙상 매도 조건까지 남은 거리"와 "최대 손실 한도(원)"를 먼저 보여준다. 매입가는 펼치면 보이게 한다(숨기되 감추지는 않음 — 투명성 유지).
- 깜빡임·틱 단위 색 번쩍임·숫자 롤링 애니메이션은 넣지 않는다(FCA: 저이해도 집단 거래↑).
- 관심종목 화면에 등락률 순 정렬·급등 배지를 기본으로 두지 않는다(OSC·Barber 근거). 정렬 기본값은 이름 또는 사용자 지정 순서.
- 색: 한국 관례(상승 빨강, 하락 파랑)를 따르되 **색만으로 의미를 전달하지 않는다** — 부호(+/−), 화살표(▲/▼), "이익/손실" 글자를 함께 쓴다. 요약 숫자는 채도를 낮추고, 경고(시스템 문제)는 등락 색과 겹치지 않는 별도 색·아이콘을 쓴다. 한국에서 빨강이 '이익'과 '위험 경고' 두 의미로 충돌한다는 점이 특히 중요하다.
- 손익은 원화가 기본, 백분율은 보조. 비용은 별도 줄로 "지금까지 수수료·세금으로 나간 돈"을 누적 표시해 거래 횟수의 대가를 보이게 한다.

### Gaps
- 한국 이용자(빨강=상승) 대상 색상 효과 실험, 한국 색각 이상 유병률 수치, WCAG/KWCAG 조항 확인은 검색 한도 소진으로 하지 못했다(색만으로 정보를 전달하지 말라는 것은 WCAG 1.4.1의 일반 원칙으로 알고 있으나 이번 세션 미검증).
- "대표 숫자 하나 + 단계적 공개 + 평문 요약"이 금융 대시보드 이해도를 높인다는 통제 연구, Nielsen Norman Group의 관련 지침은 확보하지 못했다. 위 구조 권고는 행동 연구에서의 추론 + 일반 UX 통념이다.
- 원화 표시 대 백분율 표시가 개인 투자자 판단에 미치는 효과의 직접 실험은 찾지 못했다.

---

## 7. 모바일·설치형 동반 화면 패턴

### Takeaway
모바일은 "거래 채널"이 되면 위험 감수가 늘어나는 것으로 측정된 매체이므로, 이 도구의 모바일 화면은 **보는 용도(상태 확인)와 멈추는 용도(일시정지)만** 갖추는 것이 근거에 맞다. iOS에서 웹앱 푸시는 홈 화면에 설치해야만 동작하고, 무음 백그라운드 갱신이나 잠금화면 실시간 표시(Live Activity)는 웹앱으로 기대하기 어렵다.

### Cited Findings
- 스마트폰 거래는 같은 투자자의 복권형·급등락 종목 매수를 늘리고 장 마감 후에 효과가 더 크다 — [Kalda et al., NBER WP 28363](https://www.nber.org/papers/w28363)
- 모바일 투자자는 회전율·일중거래 비중이 높고 성과가 저조(자본시장연구원 분석) — [자본시장연구원 보도자료](https://www.kcmi.re.kr/community/press_release_view?bno=344)
- iOS/iPadOS 16.4부터 홈 화면에 추가한 웹앱에서만 웹 푸시와 배지(Badging API)가 동작한다 — [MobiLoud: PWA 푸시](https://www.mobiloud.com/blog/pwa-push-notifications); [MobiLoud: iOS PWA](https://www.mobiloud.com/blog/progressive-web-apps-ios)
- Declarative Web Push: 서비스 워커 없이 구독·표시 가능, iOS/iPadOS 18.4(2025-03)에서 공개 출시, 홈 화면 웹앱에서 동작하며 메시지에 앱 배지 갱신을 실을 수 있다 — [WebKit "Meet Declarative Web Push"](https://webkit.org/?p=16535); [Apple WWDC25 세션 235](https://developer.apple.com/videos/play/wwdc2025/235/)
- 한계: Safari는 웹 알림의 이미지·액션 버튼을 지원하지 않고(Android Chrome은 지원), 무음 푸시가 불가능해 푸시는 항상 눈에 보이는 알림이어야 하므로 푸시로 백그라운드 내용 갱신을 할 수 없다. 2026-10 기준 Chrome·Edge·Firefox는 Declarative Web Push 미지원이라 서비스 워커 유지 필요(2차 자료 1건) — [MobiLoud](https://www.mobiloud.com/blog/pwa-push-notifications); [Aimtell 2026](https://aimtell.com/blog/state-of-declarative-web-push-2026)
- 토스증권 WTS는 모바일 QR 촬영으로 PC 로그인을 처리한다(기기 간 연결의 국내 익숙한 패턴) — [SBS Biz](https://biz.sbs.co.kr/amp/article/20000182295)

### Inferences
- 모바일 화면 범위 제안: (보기) 한 문장 상태, 오늘/이번 주 순손익, 한도 사용률, 연결 상태 / (하기) **일시정지와 비상 정지만**. 설정 변경·한도 상향·실전 전환은 PC에서만, 또는 모바일에서 신청해도 지연 적용. Kalda 등의 "스마트폰·장 마감 후 위험 감수↑"와 맞물린다.
- 현재의 Telegram/ntfy 알림 채널은 iOS 웹 푸시의 제약(설치 필수, 액션 버튼 없음, 무음 갱신 불가)을 피하는 합리적 선택이다. 웹앱 자체에서는 **배지 숫자를 "조치 필요 건수"로만** 쓰는 것이 좋다(읽지 않은 체결 수가 아니라).
- 잠금화면 실시간 표시 대용: ntfy/Telegram의 고정(pin) 메시지나 하루 1회 요약 메시지를 "오늘의 상태판"으로 쓰고 수정(edit)으로 갱신하는 방식이 웹앱만으로 가능한 현실적 대안이다(구현 추론, 직접 근거 없음).
- 홈 화면 설치 안내는 iOS에서 푸시의 전제 조건이므로 온보딩 체크리스트의 한 항목으로 넣되, 푸시를 Telegram/ntfy로만 쓸 경우 필수가 아님을 밝혀 단계를 줄인다.

### Gaps
- 웹앱에서 Live Activity·홈 화면 위젯을 쓸 수 없다는 점은 검색 결과가 직접 확인해 주지 않았다(네이티브 ActivityKit 기능이라 불가로 가정하는 것이 합리적이나 미검증).
- "모니터링 전용 동반 앱"의 화면 구성이 과잉거래를 줄인다는 직접 연구는 없다. Android 위젯/PWA 바로가기 등 대안의 현황, iOS 27의 웹앱 변경 사항은 2차 자료 1건뿐이라 신뢰도 낮음.

---

## 8. API 키와 다단계 검증 경로가 필요한 도구의 온보딩

### Takeaway
이 주제는 **업체 자료 위주이고 통제된 증거가 약하다.** 다만 인접 증거 두 가지는 분명하다: 사용자 대부분은 주어지면 모의 단계를 건너뛰고(67.2%), 마찰은 보호 효과와 이탈 비용을 함께 낳는다. 따라서 "쉽게 만들 곳"(키 입력·연결 확인·데모 데이터)과 "일부러 느리게 만들 곳"(실전 전환)을 구분해야 한다.

### Cited Findings
- 실거래를 한 Alpaca API 이용자의 67.2%는 모의 없이 실전으로 시작했다(2024-06~2025-05) — [Alpaca](https://alpaca.markets/learn/paper-trading-vs-live-trading-a-data-backed-guide-on-when-to-start-trading-real-money)
- FCA 실험에서 일부 마찰은 참가자를 절차에서 이탈하게 했다(마찰은 공짜가 아님) — [FCA "Beyond disclosure"](https://www.fca.org.uk/publications/research-articles-fca-research/beyond-disclosure-high-risk-investments-slow-down-and-think)
- 업체 자료(통제 연구 아님): 빈 화면에 미리 채운 데모 데이터를 두면 기능 탐색이 15~20% 늘어난다는 주장(출처 연구 없음), 체크리스트는 3~5개 항목을 실제 활성화 성과에 연결하라는 권고, 반대로 '아하 순간'은 대개 사용자 자신의 데이터에서 오므로 데모 데이터가 활성화를 늦출 수 있다는 지적 — [Produktly 가이드](https://produktly.com/guides/how-to-use-empty-states-for-onboarding); [Supademo](https://supademo.com/blog/onboarding-ux-best-practices)
- Composer 사례: 첫 로그인에서 작동하는 백테스트까지 약 3시간(독립 리뷰 1건), 노코드는 "이미 규칙이 분명한 사람"에게 가장 잘 맞는다는 평가 — [dev.to 리뷰](https://dev.to/pickuma/composer-review-automated-trading-strategies-without-writing-code-lj3); [Benzinga](https://benzinga.com/money/composer-review)
- 인도 리테일 알고 체계는 고정 IP 등록 부담을 벤더가 대신 지게 해 개별 사용자의 설정 단계를 없앴다(규제 차원의 온보딩 부담 이전 사례) — [Zerodha Z-Connect](https://zerodha.com/z-connect/general/a-comprehensive-overview-of-nses-circular-on-the-new-retail-algo-trading-framework)
- 키움 자동감시주문은 ID별 설정이고 여러 단말 동시 사용이 안 된다는 제약을 도움말에서 미리 알린다(제약을 설정 시점에 고지하는 사례) — [키움 도움말 0624](https://download.kiwoom.com/hero4_help_new/0624.htm)
- 토스증권 주문 거부·실패 보도와 10대 증권사 MTS 사고 57건(2025~2026 상반기, 단독 보도) — 외부 시스템 실패는 흔하다 — [더팩트](https://news.tf.co.kr/read/economy/2358451.htm); [머니투데이 2026-09-07](https://www.mt.co.kr/article/2026090714281792837)

### Inferences
- **API 키 없이도 돌아가는 데모 모드**(녹화된 하루치 시세로 신호 상세·결과·알림이 어떻게 보이는지 재생)는 키 발급 전 이탈을 줄일 가능성이 높다. 단, 데모 데이터에는 화면 전체에 "예시 데이터" 표시를 고정해 실제 성과로 오인하지 않게 한다(업체 자료의 상반된 주장을 감안해 중간 이하 근거로 표시).
- 키 입력 단계는 "붙여넣기 → 즉시 연결 시험 → 사람이 읽을 수 있는 실패 사유(키 오타/권한 부족/IP 미등록/서버 점검)"로 구성한다. 토스증권 API의 거부·실패가 드물지 않으므로 오류 문구 품질이 곧 온보딩 품질이다.
- 5단계 경로는 이미 체크리스트 구조다. 보강점: 각 단계의 **통과 조건을 숫자로**(예: 연습 거래 30건 이상, 20거래일 이상, 비용 차감 후 판정 '통과') 보여주고 현재 진행도를 표시하되, 단계 건너뛰기 버튼은 두지 않는다(67.2% 근거).
- 빈 화면(연습 거래 0건, 관심종목 0개)은 "다음에 일어날 일"을 설명하는 자리로 쓴다: "장이 열리면 규칙이 조건을 살핍니다. 조건이 맞지 않으면 아무것도 하지 않는 것이 정상입니다." — '아무 일도 없음'이 고장이 아님을 알려 불필요한 개입을 막는다.
- 실전 전환 구간에서는 이탈을 걱정하지 않는다. 이 도구에서 그 지점의 이탈은 손실이 아니라 보호다(참여 지표와 사용자 성과가 갈리는 대표 지점).

### Gaps
- Nielsen Norman Group의 온보딩·튜토리얼 연구, 진행 표시 효과(endowed progress, Nunes & Drèze 2006), 설정 체크리스트의 완료율 효과에 대한 1차 자료는 접근 차단·검색 한도로 확보하지 못했다. 이 절의 UX 권고는 **약한 근거**다.
- API 키가 필요한 개인용 금융 도구의 단계별 이탈률 공개 자료는 찾지 못했다.
- 토스증권 Open API 자체의 발급 절차·제약은 이 노트의 범위 밖(다른 조사 노트 참조 필요).

---

## 9. 윤리·소비자 보호 관점과 이 도구의 설계 규칙

### Takeaway
규제기관의 방향은 일관된다: 거래를 부추기는 보상·연출·불균형한 선택지를 문제 삼고, 문구 고지만으로는 부족하다고 본다. 미국 SEC의 규칙안은 2025년에 철회되었지만 영국(Consumer Duty, 고위험 투자 냉각 기간), 캐나다(OSC 실험), IOSCO(2025-05 최종 보고서), 한국(거래 연동 이벤트 금지 추진, 용어 시정, 모의거래 의무)은 같은 방향으로 움직이고 있다. 단일 사용자 도구에도 그대로 옮길 수 있는 규칙들이다.

### Cited Findings
- IOSCO는 2025-05-19 디지털 참여 기법(DEP) 최종 보고서를 핀플루언서·온라인 모방 거래 보고서와 함께 발표했다(리테일 투자자 온라인 안전 로드맵 3차). 알림·넛지·게이미피케이션을 다루며 DEP의 편익과 위험을 모두 인정하고, 규제기관이 고려할 '좋은 관행'을 제시(구속 규칙 아님). 게이미피케이션이 조언과 마케팅의 경계를 흐려 투자자 행동을 왜곡할 수 있다고 지적 — [Regulation Tomorrow 2025-05](https://www.regulationtomorrow.com/2025/05/iosco-reports-on-finfluencers-online-imitative-trading-practices-and-digital-engagement-practices/); [CMS 요약](https://cms.law/en/int/regulatory-news/iosco-digital-engagement-practices); [IOSCO 보고서 PDF](https://www.iosco.org/library/pubdocs/pdf/IOSCOPD794.pdf)
- FCA는 2024-06 실험 결과를 내며 거래 앱 설계를 Consumer Duty 아래에서 계속 면밀히 보겠다고 밝혔다 — [FCA 보도자료](https://www.fca.org.uk/news/press-releases/fca-keeps-trading-apps-under-review-over-gaming-concerns)
- Consumer Duty와 다크 패턴: 회사가 고객의 인지·행동 편향을 고려해야 한다는 기대를 통해 다크 패턴과 연결된다 — [Linklaters 해설](https://financialregulation.linklaters.com/post/102iech/what-you-need-to-know-about-dark-patterns-and-the-consumer-duty)
- FCA 고위험 투자 규칙: 최소 24시간 냉각, 냉각 후 '계속'과 '이탈' 선택지의 동등한 눈에 띔, 투자 유인 인센티브 금지 — [FCA 점검 보고](https://www.fca.org.uk/publications/multi-firm-reviews/financial-promotions-high-risk-investments)
- 다크 패턴 정의(OECD 2022-10): 디지털 선택 설계를 이용해 소비자의 자율·선택을 훼손하는 영업 관행. 컨펌셰이밍 포함. 한쪽 선택지에 시각적 무게를 더 줄 때에도 다른 선택지를 분명히 설명하고 눈에 띔의 균형을 맞추라는 실무 지침 — [Taylor Wessing 2022-12](https://www.taylorwessing.com/de/insights-and-events/insights/2022/12/what-is-a-dark-pattern); [OECD 문서](https://one.oecd.org/document/DSTI/CP(2021)12/FINAL/en/pdf)
- 슬러지: 소비자가 원하는 행동을 하기 어렵게 만드는 과도하거나 정당화되지 않는 마찰. 단 "모든 마찰이 슬러지는 아니다" — [영국 CMA 온라인 선택 설계 증거 검토](https://www.gov.uk/government/publications/online-choice-architecture-how-digital-design-can-harm-competition-and-consumers/evidence-review-of-online-choice-architecture-and-consumer-and-competition-harm)
- 표준화된 손실 비율 고지 사례: ESMA는 2018년 CFD 리테일 계좌의 74~89%가 손실(고객당 평균 손실 1,600~29,000유로)임을 근거로, 사업자별 "최근 12개월 리테일 계좌 중 손실 비율"을 마케팅에 표준 문구로 표시하게 했다. FCA 자체 표본에서는 82%가 손실 — [ESMA 발표](https://www.esma.europa.eu/node/84933); [FCA 보도자료](https://www.fca.org.uk/news/press-releases/fca-proposes-stricter-rules-contract-difference-products)
- 미국: 매사추세츠 대 Robinhood 750만 달러 합의(2024-01), SEC 규칙안 철회(2025-06) — [WealthManagement](https://www.wealthmanagement.com/regulation-compliance/robinhood-pays-75m-settle-massachusetts-gamification-charge); [Alston & Bird](https://www.alston.com/en/insights/publications/2025/06/sec-withdraws-multiple-rule-proposals)
- 한국: 거래 연동 현금성 이벤트 2027-01 금지 추진(2026-10-28), '외상구매' 용어 시정(2024-11), 해외 파생 사전교육·모의거래 의무(2025-12-15) — [비즈워치](https://news.bizwatch.co.kr/article/market/2026/10/28/0010); [메트로신문](https://www.metroseoul.co.kr/article/20241119500746); [데일리안](https://www.dailian.co.kr/news/view/1502047/)
- OSC는 게이미피케이션이 투자자에게 이롭게 쓰일 수 있다는 관점도 함께 다룬다(기사 제목 수준 확인: "Gamification that's good for investors") — [Advisor.ca](https://www.advisor.ca/industry-news/industry/gamification-thats-good-for-investors/)

### Inferences — 이 도구의 설계 규칙으로 번역
1. **거래를 축하하지 않는다.** 체결·이익 실현에 색종이, 이모지, 효과음, 연속 기록, 배지, 등급을 쓰지 않는다. (Robinhood 합의, OSC +39%, Chapkovski +5%)
2. **축하할 것이 있다면 '절제'다.** 굳이 긍정 피드백을 준다면 "이번 주 규칙을 한 번도 건드리지 않음", "한도 안에서 운영됨" 같은 과정 지표에만 조용히 준다. (OSC의 '이로운 게이미피케이션' 관점 + Fischbacher의 사전 약속 근거. 효과는 가설)
3. **순위·급등락·인기 목록을 만들지 않는다.** (Barber −4.7%, OSC +14%)
4. **결과는 항상 비용 차감 후 원화로, 비용은 따로도 보여준다.** (자본시장연구원 13조 대 13.7조, Barber & Odean)
5. **'아무것도 하지 않기'가 가장 쉬운 기본값이다.** 모든 확인 창에서 "그대로 두기"와 "진행"은 같은 크기, 기본 포커스는 "그대로 두기". 연습 유지는 클릭 0번, 실전 전환은 여러 단계 + 24시간 대기. (FCA 동등 눈에 띔·냉각 기간)
6. **보호를 푸는 방향은 느리게, 조이는 방향은 즉시.** 한도 상향·손절 확대·실전 전환은 지연 적용, 일시정지·한도 하향은 즉시. (Heimer 계열 브로커 자료, 도박 RCT)
7. **기저율을 숨기지 않는다.** 실전 전환 관문에 "데이트레이딩을 300일 이상 한 사람의 97%가 손실(브라질), 수수료 후 꾸준히 버는 사람은 1% 미만(대만)"을 ESMA식 표준 문구처럼 한 문장으로 고정 표시하고, 그 아래 **사용자 본인의 연습 기록**을 같은 형식으로 보여준다. (ESMA 고지 사례, Chague 등, Barber 등)
8. **쉬운 말이 위험을 가리지 않게 한다.** 용어 목록을 만들어 '연습'과 '실전', '손실'과 '비용'을 완곡하게 바꾸지 않는다. ('외상구매' 시정 사례)
9. **면책 문구 대신 구체적 한 문장.** "과거 성과는 미래를 보장하지 않습니다" 대신 표본 수·시도 횟수·최악 구간을 넣은 문장. (Mercer 등, FCA 현저성·단순 문구)
10. **마찰은 보호 지점에만.** 조회·정지·해지(키 삭제, 데이터 내보내기)는 마찰 0, 위험 확대에만 마찰. 정당화되지 않는 마찰은 슬러지다. (CMA)

### Gaps
- IOSCO 2025 최종 보고서의 '좋은 관행' 목록 원문, FCA Consumer Duty(PRIN 2A) 지침의 슬러지·동등 눈에 띔 관련 조문은 열람하지 못했다. 링크한 IOSCO PDF 번호(PD794)가 DEP 보고서와 정확히 대응하는지도 미확인.
- 24시간 냉각 기간이 실제로 해로운 투자 결정을 줄였는지 측정한 결과 자료는 찾지 못했다(규칙 존재와 구현 여부만 확인).
- 금융위·금감원이 MTS의 UI 요소(랭킹, 알림, 연출)를 직접 겨냥한 가이드라인은 이번 조사에서 확인되지 않았다. ASIC(호주) 자료도 확보하지 못했다.

---

## 10. (종합) 단일 사용자·로컬·모의투자 우선 도구에 적용할 우선순위 기능 아이디어

### Takeaway
우선순위의 기준은 "참여가 아니라 사용자 결과와 안전"이다. 증거가 강하고 구현 비용이 낮은 순서로 보면 ① 구속력 있는 한도와 느린 실전 전환, ② 알림 다이어트, ③ 정직한 백테스트·기록 표시, ④ 화면에서 자극 요소를 덜어내기가 최우선이고, 일지·온보딩·모바일 개선은 근거가 약하므로 가설로 두고 가볍게 구현하는 것이 맞다.

### Cited Findings (아이디어 ↔ 근거 대응표)

**P0 — 근거 강함, 안전에 직접 기여**

| # | 아이디어 | 구체 동작 | 근거 | 강도 |
|---|---|---|---|---|
| P0-1 | 엔진이 강제하는 일일 한도 | 일일 손실 한도(원), 하루 최대 거래 수, 연속 손실 N회 후 당일 중단. 기본 켜짐. 홈에 "오늘 한도 사용률"만 표시 | 자동 손절은 처분효과를 줄이고 상기 알림은 무효 — [Fischbacher 등](https://econpapers.repec.org/RePEc:oup:rfinst:v:30:y:2017:i:6:p:2110-2129.); 한도 권유만으로는 순손실 불변 — [Ivanova 등](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.00639/full) | 강(인접 영역) |
| P0-2 | 비대칭 변경 규칙 | 한도 하향·일시정지는 즉시, 한도 상향·손절 확대는 다음 거래일부터 + 재확인. 장중·손실 중에는 상향 불가 | 손실 누적 시 가장 흔한 반응은 손실 한도 확대 — [NBER 발표 논문](https://conference.nber.org/conf_papers/f134975/f134975.pdf); [Chicago Booth Review](https://www.chicagobooth.edu/review/two-big-strategic-mistakes-investors-make) | 중 |
| P0-3 | 실전 전환 냉각과 동등 버튼 | (실전 단계 도입 시) 신청 후 24시간 뒤 활성화, "연습 유지"와 "실전 시작" 동일 크기, 단계 건너뛰기 없음, 통과 조건을 숫자로 표시 | FCA 24시간 냉각·동등 눈에 띔 — [FCA](https://www.fca.org.uk/publications/multi-firm-reviews/financial-promotions-high-risk-investments); 한국 해외 파생 모의거래 3시간 의무 — [데일리안](https://www.dailian.co.kr/news/view/1502047/); 67.2%가 모의 생략 — [Alpaca](https://alpaca.markets/learn/paper-trading-vs-live-trading-a-data-backed-guide-on-when-to-start-trading-real-money) | 중 |
| P0-4 | 알림 기본값 재설계 | 기본은 장 마감 요약 1회 + '조치 필요' 예외 알림만. 건당 체결 알림은 선택(기본 끔). 가격 변동 알림은 만들지 않음. 문구에 감탄·이모지 없음 | 푸시 → 거래 +11%, 위험 거래 +8% — [FCA](https://www.fca.org.uk/publications/research-notes/research-note-digital-engagement-practices-trading-apps-experiment); 15분 내 +25% — [Moss](https://austinsmoss.github.io/austinmoss.me/Moss_JMP_How-Do-DEPs-Affect-Retail-Investor-Information-Processing-and-Trading.pdf); 레버리지 +19%p — [Arnold 등](https://www.jbs.cam.ac.uk/wp-content/uploads/2020/08/2020-06-conference-paper-arnold-pelster-subrahmanyam.pdf); 하루 3회 묶음의 이점 — [Fitz 등](https://scholars.duke.edu/publication/1402953) | 강 |
| P0-5 | 정직한 "과거로 테스트" | 단일 수익률 대신 거래 수, 이긴/진 횟수("100번 중 N번"), 최악 구간, 비용 후 범위, 표본 외 기간 결과. **설정을 바꿔 시험한 횟수**를 누적 표시하고 많을수록 판정 엄격화. 표본 적으면 '보류'가 기본 | 적은 조합 시험으로도 높은 성과가 우연히 나오고 표본 외 기대수익은 음수 가능 — [Bailey 등](https://scholarworks.wmich.edu/math_pubs/40/); 최고 성과만 보고하면 부풀려짐 — [Deflated Sharpe Ratio](https://papers.ssrn.com/abstract=2460551); 관례 경고의 한계 — [Palmiter & Taha](https://digitalcommons.law.uga.edu/glr/vol46/iss2/3) | 강(통계) / 형식 효과는 추론 |
| P0-6 | '넣지 않을 것' 목록 명문화 | 축하 연출, 포인트·배지·연속 기록, 급등락·인기 순위, 깜빡이는 가격, 수익률 순 정렬 기본값을 기획서에 금지 항목으로 기록 | 포인트 +39%, 인기 목록 +14% — [OSC](https://www.osc.ca/sites/default/files/2022-11/sn_20221117_11-796_gamification-report.pdf); 쏠림 종목 −4.7% — [Barber 등](https://econpapers.repec.org/RePEc:bla:jfinan:v:77:y:2022:i:6:p:3141-3190); 축하 연출 +5.17% — [Chapkovski 등](https://pubsonline.informs.org/doi/epdf/10.1287/mnsc.2022.02650); Robinhood 합의 — [WealthManagement](https://www.wealthmanagement.com/regulation-compliance/robinhood-pays-75m-settle-massachusetts-gamification-charge) | 강 |
| P0-7 | 시스템 신선도 표시와 안전 정지 | 홈 한 문장에 "마지막 시세 수신 N초 전", API 오류 시 신규 진입 자동 중단 + '조치 필요' 알림, 사람이 읽을 수 있는 실패 사유 | 토스증권 장애·주문 거부 보도 — [데일리안](https://www.dailian.co.kr/news/view/1633904/); [더팩트](https://news.tf.co.kr/read/economy/2358451.htm); 10대 증권사 MTS 사고 57건 — [머니투데이](https://www.mt.co.kr/article/2026090714281792837) | 중(사례) |

**P1 — 근거 중간, 결과 개선 가능성 높음**

| # | 아이디어 | 구체 동작 | 근거 | 강도 |
|---|---|---|---|---|
| P1-1 | 평가 단위를 길게 | 홈 대표 숫자는 이번 주/이번 달 비용 후 누적 원화 손익. 장중 평가손익과 '실시간' 패널은 기본 접힘 | 단기 수익률 표시 금지 → 거래량 약 −30% — [Shaton](https://www.federalreserve.gov/econres/feds/the-display-of-information-and-household-investment-behavior.htm); 피드백 빈도와 위험 선택 — [Gneezy & Potters](https://econpapers.repec.org/RePEc:oup:qjecon:v:112:y:1997:i:2:p:631-645.); [Larson 등](https://www.nber.org/papers/w22605) | 강(방향 해석은 추론) |
| P1-2 | 매입가 덜 눈에 띄게 | 보유 줄에는 "규칙상 매도 조건까지 거리"와 "최대 손실(원)"을 먼저, 매입가·수익률은 펼치면 표시 | 매입가 미표시 시 처분효과 25% 감소 — [Frydman & Rangel](https://ideas.repec.org/a/eee/jeborg/v107y2014ipbp541-552.html) | 강(실험실) |
| P1-3 | 설명 카드에 기록과 불확실성 | 신호 상세에 "같은 유형 지난 N번 중 이익 a번/손실 b번", 표본 부족 표시, "이 규칙이 잘 틀리는 상황" 한 줄 | 설명은 틀린 추천 의존도 높임 — [Bansal 등](https://aiweb.cs.washington.edu/ai/pubs/bansal-chi21.pdf); 불확실성 병기 — [Papantonis & Belle](https://ar5iv.labs.arxiv.org/html/2304.14130); 빈도·아이콘 표현 — [Galesic 등](https://pure.mpg.de/pubman/item/item_2099767_5/component/file_2562291/MG_Using_2009.pdf) | 중 |
| P1-4 | 안전한 방향의 조정 손잡이 | 일시정지, 1회 투자금 상한 낮추기, 종목 제외만 즉시 허용 | 약간의 수정 권한이 알고리즘 사용과 만족을 높임 — [Dietvorst 등](https://ideas.repec.org/a/inm/ormnsc/v64y2018i3p1155-1170.html) | 강(예측 과제) |
| P1-5 | 고위험 결정의 인지 강제 | 실전 전환·한도 상향 직전에만 "지난 연습 거래 중 손실 횟수는?"을 먼저 묻고 실제 값 공개 | 인지 강제가 과의존 감소 — [Buçinca, Malaya & Gajos](https://ar5iv.labs.arxiv.org/html/2102.09692) | 중 |
| P1-6 | 기저율 + 내 기록 나란히 | 실전 관문에 데이트레이딩 기저율 한 문장과 본인 연습 기록을 같은 형식으로 | 97% 손실 — [Chague 등](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101); 1% 미만 — [Barber 등](https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html); 표준 손실 비율 고지 — [ESMA](https://www.esma.europa.eu/node/84933) | 중(고지 효과는 추론) |
| P1-7 | 비용 누적 줄 | "지금까지 수수료·세금으로 나간 돈"을 손익과 별도 표시, 거래 1건당 평균 비용 | 거래이익 13조 대 비용 13.7조 — [뉴데일리](https://biz.newdaily.co.kr/site/data/html/2021/02/26/2021022600078.html); 최다 거래 가구 11.4% 대 시장 17.9% — [Barber & Odean](https://econpapers.repec.org/RePEc:bla:jfinan:v:55:y:2000:i:2:p:773-806) | 중(표시 효과는 추론) |
| P1-8 | 보수적 모의 체결과 격차 지표 | 연습 체결에 슬리피지 가산, "연습은 실제보다 좋게 나옵니다" 고정 표시, 실전 소액 단계에서 연습가 대 실제가 차이 표시 | 모의→실전 격차 최대 6.38%p, 원인은 체결가·주문 금액 차이 — [arXiv 2609.34510](https://arxiv.org/pdf/2609.34510) | 약~중(프리프린트 1건) |

**P2 — 근거 약함, 저비용으로 시도하고 가설로 관리**

| # | 아이디어 | 구체 동작 | 근거 | 강도 |
|---|---|---|---|---|
| P2-1 | 자동 복기(주간) | 규칙 준수율, 사람이 개입한 거래의 결과를 규칙만 따랐을 때와 비교. 글쓰기 강요 없음 | 일지 효과의 통제 연구 없음, 업체 관찰 자료뿐 — [CMC Markets](https://www.cmcmarkets.com/en-au/cfd/learn/trading-guides/how-to-use-a-trading-journal) | 약 |
| P2-2 | 데모 모드와 빈 화면 안내 | 키 없이 녹화 데이터로 전 화면 재생("예시 데이터" 고정 표시), 빈 화면에 "아무 일도 없는 것이 정상" 설명 | 업체 자료의 상반된 주장 — [Produktly](https://produktly.com/guides/how-to-use-empty-states-for-onboarding) | 약 |
| P2-3 | 모바일은 보기와 멈추기만 | 모바일에서는 상태·순손익·한도 사용률·일시정지만. 위험 확대 조작은 PC 전용 또는 지연 적용 | 스마트폰 거래의 위험 감수↑ — [Kalda 등](https://www.nber.org/papers/w28363); 모바일 투자자 성과 저조 — [자본시장연구원](https://www.kcmi.re.kr/community/press_release_view?bno=344) | 중(적용은 추론) |
| P2-4 | 배지는 '조치 필요' 건수만 | 홈 화면 웹앱 배지를 읽지 않은 체결 수가 아니라 조치 필요 건수로 | iOS 16.4+ 홈 화면 웹앱 푸시·배지, 무음 푸시 불가 — [MobiLoud](https://www.mobiloud.com/blog/pwa-push-notifications); [WebKit](https://webkit.org/?p=16535) | 기술 사실 / 효과 근거 없음 |
| P2-5 | 색 이중 부호화 | 빨강(상승)/파랑(하락) 관례 유지 + 부호·화살표·글자 병기, 요약 숫자 채도 낮춤, 시스템 경고는 별도 색·아이콘 | 색 효과는 문화·색각에 따라 달라짐 — [Bazley 등](https://econpapers.repec.org/RePEc:inm:ormnsc:v:67:y:2021:i:9:p:5616-5641) | 중(한국 직접 증거 없음) |
| P2-6 | 용어 점검표 | 쉬운 말이 위험을 가리지 않는지 화면별 점검('연습/실전', '손실', '비용') | '외상구매' 시정 — [메트로신문](https://www.metroseoul.co.kr/article/20241119500746) | 사례 |

### Inferences
- **현재 UI에서 유지할 것**(근거와 일치): 한 문장 상태, 평문 설명, 원화 순손익, 통과/실패/보류 판정, 5단계 경로, 모의투자 전용.
- **현재 UI에서 재검토할 것**: (a) 연습 거래 개폐 시마다 보내는 푸시(P0-4), (b) 오른쪽 패널의 실시간·보유 종목 상시 노출(P1-1, P1-2), (c) 관심종목이 등락률 중심으로 보이는지 여부(P0-6), (d) "과거로 테스트"가 단일 수익률을 대표 숫자로 쓰는지 여부(P0-5).
- **성공 지표 제안**: 참여 지표(접속 횟수, 체류 시간)는 목표가 아니라 **경계 지표**로 둔다. 목표 지표는 규칙 준수율, 사람 개입 횟수(낮을수록 좋음), 한도 상향 시도 횟수(낮을수록 좋음), 비용 후 손익, 모의 대 실전 체결 격차. 근거: 참여를 높이는 장치가 성과를 낮춘다는 2절의 일관된 결과.
- 여러 권고가 서로 긴장 관계에 있다는 점을 기획서에 명시해야 한다: ① 투명성(다 보여주기) 대 편향 완화(덜 눈에 띄게 하기) — 해법은 "숨기지 않고 접어 두기". ② 통제감(Dietvorst) 대 사전 약속(Heimer) — 해법은 "안전한 방향만 즉시". ③ 설명(이해) 대 과신뢰(Bansal) — 해법은 "설명 + 기록 + 불확실성".
- 단일 사용자 로컬 도구라는 조건은 이점이다. 회사 제품과 달리 거래량에서 수익을 얻지 않으므로 이해상충이 없고, 위의 '느리게 만들기'를 사업적 손해 없이 적용할 수 있다.

### Gaps
- 위 아이디어 가운데 **이 조합 자체**(자동매매 + 비전문가 + 모의 우선)의 효과를 검증한 연구는 없다. 대부분 인접 영역(재량 매매, 도박, 의료 위험 전달, 일반 AI 보조 의사결정)의 결과를 옮긴 추론이므로, 도구 안에 간단한 자기 측정(개입 횟수, 한도 변경 시도, 알림 설정 변경 전후의 접속 빈도)을 넣어 스스로 검증하는 것이 필요하다.
- 열람 차단과 검색 한도 때문에 확인하지 못한 1차 자료 목록(후속 조사 권장): OSC 2024 "Gamification Revisited" 수치, FCA 연구 노트 본문의 리더보드·깜빡이는 가격 평균 효과, IOSCO 2025 DEP 최종 보고서의 좋은 관행 목록, Heimer 등 논문의 정확한 수치, Frydman & Rangel·Larson 등 본문 수치, NN/g 온보딩 지침, 경보 피로 문헌, 한국 색각 이상 통계와 KWCAG, Trade Republic·Public·3Commas·Pionex·Streak·핀트 외 로보어드바이저의 온보딩·가드레일 세부.
