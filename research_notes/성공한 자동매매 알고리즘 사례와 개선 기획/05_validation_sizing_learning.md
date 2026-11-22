# 05. 전략 검증(과최적화 방지) · 포지션 사이징 · 소표본 학습 설계 — 리서치 노트 (2026-11 기준)

> **읽는 법 / 검증 수준 표기**
> - 【검색확인】 = 이번 세션의 웹 검색 결과(초록·2차 요약 포함)로 내용을 다시 확인한 항목.
> - 【원전·미재확인】 = 원 논문/서적의 DOI·SSRN 링크를 제시했지만, 이번 세션에서 본문을 다시 열어 보지 못한 항목(세션 네트워크 정책상 en.wikipedia.org, arxiv.org, people.duke.edu, www.ams.org, hudsonthames.org 직접 열람이 차단되었고, 마지막 검색 배치는 검색 예산 소진으로 실행되지 못함). 공식·수치는 널리 인용되는 표준형이지만 보고서에 숫자를 그대로 싣기 전 원문 대조 권장.
> - 【자체 계산】 = 인용 공식에 본 프로젝트 가정(TP +0.9% / SL −0.5% / 왕복비용 0.25%)을 넣어 직접 계산한 값. 가정: 거래 결과는 TP 또는 SL 두 가지뿐(시간청산 무시), 거래 간 독립. 실제로는 시간청산·군집 때문에 필요한 표본이 더 늘어난다.
> - 기준 숫자(자체 계산): 순이익 W = 0.9 − 0.25 = **+0.65%**, 순손실 L = 0.5 + 0.25 = **−0.75%**, 손익분기 승률 p_BE = L/(W+L) = 0.75/1.40 = **53.57%** (비용 0이면 35.7%).

---

## 1. 백테스트 과최적화: MinBTL · PBO(CSCV) · PSR/DSR · t>3.0 · Haircut Sharpe · Reality Check/SPA/Romano-Wolf

### Takeaway
"그리드에서 고른 최고 파라미터의 성과"는 시도 횟수 N만큼 부풀려지므로, (a) 시도 횟수를 기록하고 (b) 그 N으로 기준선을 올려 잡는 검정(DSR·Bonferroni형 haircut·Reality Check 계열)을 통과시키는 것이 표준이다. 수백 건 이하 표본에서는 이 보정들을 통과하려면 승률이 손익분기보다 8~12%p 이상 높아야 하므로, 실무 해법은 "시도 횟수를 줄이고(사전 등록한 소수 조합), 보정 후 기준은 그대로 두고, 판정을 순차적으로 미루는 것"이다.

### Cited Findings

**(1) Minimum Backtest Length (MinBTL)** — Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism", Notices of the AMS 61(5).
- N개의 독립 시도 중 최댓값의 기대치 근사: `E[max_N] ≈ (1−γ)·Z⁻¹[1 − 1/N] + γ·Z⁻¹[1 − 1/(N·e)]` (γ ≈ 0.5772 Euler–Mascheroni, Z⁻¹ = 표준정규 역CDF). 진짜 Sharpe가 0이어도 연율 Sharpe `E[max_N]/√y` 가 y년 표본에서 나오므로, 목표 IS Sharpe를 우연으로 얻지 않기 위한 최소 길이는 `MinBTL ≈ ( E[max_N] / SR_target )² < 2·ln(N) / SR_target²` (년 단위). 【검색확인: 상한식과 "연 단위·1/√y 스케일" 서술】 — [SSRN 2308659](https://papers.ssrn.com/abstract=2308659); [R 재현(TimelyPortfolio)](https://timelyportfolio.github.io/research_lopezdePrado)
- 대표 예: "5년 표본에서 45개가 넘는 독립 구성을 시험하면, IS 연율 Sharpe 1 · OOS 기대 Sharpe 0인 구성을 거의 확실히 찾게 된다." 【검색확인】 — [CXO Advisory 요약](https://www.cxoadvisory.com/big-ideas/insidiousness-of-overfitting-investment-strategies-via-iterative-backtests); [R 재현: N=45 → MinBTL ≈ 4.998년](https://timelyportfolio.github.io/research_lopezdePrado)
- 논문의 가정은 정규·"순한" 분포이며 분포가 거칠면 해석이 깨진다는 한계가 요약에 명시됨. 【검색확인】 — [CXO Advisory](https://www.cxoadvisory.com/?p=23736)

**(2) PBO와 CSCV** — Bailey, Borwein, López de Prado & Zhu (2017), "The Probability of Backtest Overfitting", Journal of Computational Finance.
- PBO = "IS에서 최적으로 뽑힌 구성이 OOS에서 중앙값보다 못할 확률". CSCV(combinatorially symmetric cross-validation)는 모델-프리·비모수 구현이며, 저자들은 단순 hold-out이 투자 백테스트 맥락에서 신뢰하기 어렵다고 본다. 【검색확인】 — [Journal of Computational Finance (DOI 10.21314/JCF.2016.322)](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting); [SSRN 2326253](https://papers.ssrn.com/abstract=2326253); [eScholarship PDF](https://escholarship.org/uc/item/4w1110bb)
- 절차(표준 서술, 【원전·미재확인】): T×N 성과행렬(행=시간, 열=시도)을 S개 동일 크기 블록으로 자르고, S/2개 블록 조합을 IS·나머지를 OOS로 하는 C(S, S/2)개 분할마다 ① IS 최고 시도 n* 선택 ② n*의 OOS 상대순위 ω̄∈(0,1) ③ logit λ = ln(ω̄/(1−ω̄)) 계산. `PBO = (λ ≤ 0 인 분할의 비율)`. — [eScholarship PDF](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf)

**(3) PSR · MinTRL** — Bailey & López de Prado (2012), "The Sharpe Ratio Efficient Frontier", Journal of Risk. 【원전·미재확인(공식)】
- `PSR(SR*) = Φ[ (SR̂ − SR*)·√(n−1) / √(1 − γ̂₃·SR̂ + ((γ̂₄−1)/4)·SR̂²) ]` (n = 관측 수, γ̂₃ 왜도, γ̂₄ 첨도; SR은 관측 주기 단위 = 여기서는 "거래당" 또는 "일당").
- `MinTRL = 1 + [1 − γ̂₃·SR̂ + ((γ̂₄−1)/4)·SR̂²]·( Z_α / (SR̂ − SR*) )²`. — [SSRN 1821643](https://papers.ssrn.com/abstract=1821643)
- IID 가정의 Sharpe 표준오차 `SE(SR̂) ≈ √((1 + SR̂²/2)/T)`, 자기상관이 있으면 연율화 √q 규칙이 틀어진다(Lo 2002). 【원전·미재확인】 — [Lo, "The Statistics of Sharpe Ratios", FAJ 58(4)](https://doi.org/10.2469/faj.v58.n4.2453)

**(4) Deflated Sharpe Ratio (DSR)** — Bailey & López de Prado (2014), JPM 40(5).
- DSR은 선택 편향(다중 시도)과 비정규성 두 가지 부풀림을 보정하며, "0이 아니라 선택을 반영한 기준 SR₀에 대해 평가한 PSR", 즉 `DSR = PSR(SR₀)` 이다. SR₀는 "기량 없는 N개 독립 시도 중 최고가 기대상 도달하는 Sharpe"이고 시도들 Sharpe의 분산 V가 들어간다. 【검색확인】 — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551); [quantstrat `deflatedSharpe` 문서](https://www.rdocumentation.org/packages/quantstrat/versions/0.16.7/topics/deflatedSharpe)
- 표준형(【원전·미재확인】): `SR₀ = √V[{SR̂_n}] · ( (1−γ)·Z⁻¹[1 − 1/N] + γ·Z⁻¹[1 − 1/(N·e)] )`. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- 시도들은 서로 상관되어 있으므로 "유효 시도 수"를 추정해야 하고, López de Prado(2018)는 유사 전략을 군집화하는 방법을 제안한다. 【검색확인】 — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551); 군집 기반 추정 원전: [López de Prado & Lewis, "Detection of False Investment Strategies Using Unsupervised Learning Methods", SSRN 3167017](https://papers.ssrn.com/abstract=3167017) 【원전·미재확인】
- 2025~2026 갱신: López de Prado, Lipton & Zoonekynd, "How to Use the Sharpe Ratio"(SSRN, 2025-09 작성·2026-03 개정)는 "대부분의 Sharpe 분석이 통계적으로 결함이 있다"고 보고 PSR·MinTRL·DSR을 비정규성·소표본 편향·선택 효과 보정의 표준 도구로 재정리하며 재현 코드를 공개한다. 같은 저자들의 JPM 2026 논문 "Sharpe Ratio Inference: A New Standard for Decision Making and Reporting"이 출판본으로 보이나 동일 논문인지는 검색 결과로 확정되지 않음. 【검색확인】 — [SSRN 5520741](https://papers.ssrn.com/abstract=5520741); [ADIA Lab](https://www.adialab.ae/research-series/how-to-use-the-sharpe-ratio)
- 2026년에는 LLM이 전략을 탐색하는 설정에도 "누수 방지 + 탐색 횟수 인지(search-aware)" 평가를 적용하는 연구가 나오고 있다(제목·스니펫만 확인). 【검색확인(제목 수준)】 — [arXiv 2608.27734](https://arxiv.org/pdf/2608.27734)

**(5) t > 3.0** — Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns", RFS 29(1).
- 광범위한 데이터 마이닝을 감안하면 새 팩터에 t>2.0 기준은 경제적·통계적으로 무의미하며, 새로 발견된 팩터는 t-통계량 3.0 초과가 필요하다. 316개 팩터를 목록화. 【검색확인】 — [NBER w20592](https://nber.org/papers/w20592); [SSRN 2513152](https://papers.ssrn.com/abstract=2513152)
- 2차 자료의 표에는 316개 팩터 기준 Holm 3.64, Bonferroni 3.78이 실려 있으나 원문 대조는 못 함. 【검색확인(2차)】 — [강의노트 "The Factor Zoo and the Replication Crisis"](https://digital-ai-finance.github.io/Applied-Machine-Learning-in-Empirical-Finance/factor-zoo.html)
- 2026-02 NBER 워킹페이퍼(Harvey, Sancetta & Zhao)는 팩터 연구의 최소 t가 대략 3.0임을 다시 주장하고 p값의 보완으로 local false discovery rate를 권한다. 【검색확인】 — [NBER w34898](https://www.nber.org/system/files/working_papers/w34898/w34898.pdf)
- 반론: Jensen, Kelly & Pedersen (2023, JF) "Is There a Replication Crisis in Finance?"는 베이지안 틀로 다중검정을 다르게 다루며 다수 팩터가 재현된다고 본다. 【검색확인(2차 요약 수준)】 — [강의노트](https://digital-ai-finance.github.io/Applied-Machine-Learning-in-Empirical-Finance/factor-zoo.html); 원전 [DOI 10.1111/jofi.13249](https://doi.org/10.1111/jofi.13249) 【원전·미재확인】

**(6) Haircut Sharpe** — Harvey & Liu (2015), "Backtesting", JPM.
- 방법: Sharpe → t-비율(`t = SR_annual × √(년수)`) → 시험 횟수를 반영한 다중검정 보정 p값(Bonferroni/Holm/BHY) → 다시 Sharpe로 환산. "haircut Sharpe"는 단일 검정이었다면 나왔을 Sharpe다. 【검색확인】 — [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF); [SSRN 2345489](https://papers.ssrn.com/abstract=2345489)
- 업계 관행인 일률 50% 할인은 심각한 오류다: haircut은 비선형이라 매우 높은 Sharpe는 덜 깎고, 경계선 Sharpe는 훨씬 크게 깎아야 한다. 【검색확인】 — [Man Group/Oxford-Man 요약](https://www.man.com/insights/backtesting); [CFA Institute Digest](https://rpc.cfainstitute.org/research/cfa-digest/2016/03/backtesting-digest-summary)

**(7) Reality Check / SPA / Romano-Wolf** 【원전·미재확인】
- White (2000) Reality Check: K개 규칙 중 최고 규칙의 벤치마크 대비 초과성과에 대해 H₀: max_k E[f_k] ≤ 0 을 stationary bootstrap으로 검정(통계량 `V = max_k √n·f̄_k`). — [Econometrica 68(5)](https://doi.org/10.1111/1468-0262.00152)
- 기술적 규칙 적용 원형: Sullivan, Timmermann & White (1999). — [Journal of Finance 54(5)](https://doi.org/10.1111/0022-1082.00163)
- Hansen (2005) SPA: 통계량을 studentize하고, 형편없는 규칙이 검정력을 깎지 않도록 귀무분포를 재중심화. — [JBES 23(4)](https://doi.org/10.1198/073500105000000063)
- Romano & Wolf (2005) StepM: FWER을 통제하면서 "어느 규칙들이" 유의한지 단계적으로 식별. — [Econometrica 73(4)](https://doi.org/10.1111/j.1468-0262.2005.00615.x)
- 구현 참고: Python `arch` 패키지가 SPA·StepM·MCS를 제공. — [arch 문서](https://arch.readthedocs.io/en/latest/multiple-comparison/multiple-comparisons.html)

**(8) 실증: 백테스트 지표는 OOS를 잘 예측하지 못한다**
- Quantopian 888개 알고리즘(2010–2015 백테스트, 6~12개월 OOS): IS Sharpe 등 개별 지표는 OOS 성과의 1~2%만 설명(R² 0.01~0.02), 변동성·낙폭 지표가 상대적으로 더 예측력 있음; 백테스트 특징들에 ML을 쓰면 hold-out R² = 0.17. 【검색확인】 — [SSRN 2745220](https://papers.ssrn.com/abstract=2745220); [CXO Advisory 요약](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies); [Quantpedia](https://quantpedia.com/quantopians-academic-paper-about-in-vs-out-of-sample-performance-of-trading-alg/)
- 학술 이상현상: 72개 발표 전략에서 Sharpe가 발표 후 약 절반으로 감쇠, 감쇠 예측 변수는 차익 자본 유입과 다중검정에 따른 IS 과최적화. 【검색확인】 — [Falck, Rej & Thesmar, arXiv 2105.01380](https://arxiv.org/pdf/2105.01380)

### Inferences
- 【자체 계산】 `E[max_N]`(표준정규 단위): N=5 → 1.19, 10 → 1.57, 20 → 1.90, 45 → 2.24, 100 → 2.53, 200 → 2.77, 1000 → 3.26. 즉 연율 Sharpe 1을 목표로 할 때 MinBTL ≈ 1.4년(N=5), 2.5년(N=10), 3.6년(N=20), 5.0년(N=45), 6.4년(N=100). **분봉 몇 달치 데이터로 수십~수백 조합 그리드를 돌리면 "IS 최고"는 통계적으로 거의 정보가 없다.**
- 【자체 계산】 거래 단위 DSR(귀무하 시도 간 Sharpe 분산 V ≈ 1/n, 정규 근사). DSR ≥ 0.95에 필요한 거래당 Sharpe와 그에 해당하는 승률(TP/SL/비용 가정):

  | 거래 수 n | 시도 1개(PSR) | 유효 시도 20개 | 유효 시도 100개 |
  |---|---|---|---|
  | 100 | SR 0.167 → 승률 61.7% | SR 0.361 → 70.1% | SR 0.426 → 72.6% |
  | 200 | 0.117 → 59.3% | 0.253 → 65.6% | 0.298 → 67.5% |
  | 300 | 0.095 → 58.3% | 0.206 → 63.5% | 0.243 → 65.1% |
  | 500 | 0.074 → 57.2% | 0.159 → 61.3% | 0.187 → 62.6% |
  | 1000 | 0.052 → 56.2% | 0.112 → 59.1% | 0.132 → 60.1% |

  → 그리드 탐색 결과를 그대로 승격 게이트에 쓰려면 손익분기(53.6%) 대비 +8~12%p가 필요. 현실적 엣지(+3~5%p)는 이 게이트를 수백 건으로는 통과할 수 없다.
- 【자체 계산】 Bonferroni haircut 예시(양측 p, `t = SR√T`): 연율 SR 1.0·3년·50회 시험 → t=1.73, 보정 p=1 → haircut 100%(유의성 없음). SR 2.0·3년·200회 → 보정 p≈0.106 → haircut SR ≈ 0.93(−53%). SR 1.0·10년·200회 → haircut SR ≈ 0.32(−68%). Harvey–Liu의 "비선형" 메시지와 일치하는 방향.
- 적용안(소표본·단일 전략): ① 백테스터가 **평가한 모든 파라미터 조합 수 N과 각 조합의 거래별 손익 행렬을 저장**(DSR·PBO·SPA의 입력). ② 그리드는 "사전 등록한 ≤10~20개 조합"으로 제한하고 인접 조합이 함께 양(+)인 **고원(plateau)** 인지 확인. ③ 승격 게이트: 기존의 "OOS 기대값>0 & CI 하한>0"에 `DSR ≥ 0.95`(N은 유효 시도 수, 보수적으로는 전체 조합 수) 와 `PBO ≤ 0.2~0.3`(임계값은 논문이 정한 것이 아니라 본 노트의 제안; PBO≈0.5 이상이면 선택 절차가 무작위와 다를 바 없다는 뜻)을 추가. ④ CSCV는 S=8(70분할)~10(252분할) 정도가 소표본에 맞음(블록당 거래가 너무 적어지지 않게). ⑤ SPA/StepM은 "벤치마크=거래 안 함(0) 또는 무조건 진입" 대비 그리드 전체의 데이터 스누핑 p값을 한 번에 주므로 DSR의 교차검증용으로 적합(`arch` 사용).
- 분봉은 관측 수를 늘리지만 **평균(기대수익) 추정의 정밀도는 관측 빈도가 아니라 기간·독립 거래 수가 결정**한다(Merton 1980의 고전적 결과; [DOI 10.1016/0304-405X(80)90007-0](https://doi.org/10.1016/0304-405X(80)90007-0) 【원전·미재확인】). 따라서 MinBTL/DSR의 n에는 분봉 수가 아니라 "거래 수(또는 거래일 수)"를 넣어야 한다.

### Gaps
- Harvey & Liu 논문 본문의 수치 예(특정 Sharpe·시험 횟수에서의 Bonferroni/Holm/BHY haircut 표)는 Duke PDF 접근 차단으로 인용하지 못함. 위 haircut 숫자는 자체 Bonferroni 계산이다.
- Chordia, Goyal & Saretto (2020)의 임계 t(통상 3.4~3.8로 인용)는 이번 검색에서 확인되지 않음.
- "How to Use the Sharpe Ratio"(2025)가 PSR 분산식·FDR 처리에서 기존 공식을 어떻게 수정했는지 세부는 본문 미열람으로 확인 못 함 — 구현 전 저자 GitHub 코드 대조 필요.
- PBO 허용 임계값에 대한 학술적 합의는 찾지 못함(0.2~0.3은 본 노트의 제안).

---

## 2. 시계열 교차검증: walk-forward(anchored/rolling) · purged k-fold + embargo · CPCV

### Takeaway
통제된 비교 연구(2024)는 CPCV가 PBO·DSR 기준으로 walk-forward·k-fold보다 낫다고 보고하지만, 실거래와 같은 시간 순서를 지키는 walk-forward가 여전히 업계 표준이다. 몇 달치 분봉·수백 거래에서는 "규칙 파라미터 선택 = anchored walk-forward(+CSCV로 PBO 산출)", "ML 스코어러 평가 = 거래일 단위 purged/embargo k-fold 또는 소규모 CPCV(N=6,k=2)"가 실용적이다.

### Cited Findings
- Arian, Norouzi Mobarekeh & Seco (2024), "Backtest overfitting in the machine learning era: A comparison of out-of-sample testing methods in a synthetic controlled environment", Knowledge-Based Systems: CPCV가 더 낮은 PBO와 더 나은 DSR 검정통계량을 보였고, walk-forward는 거짓 발견 방지에 약하며 시간적 변동성이 크고 정상성이 약했다. Purged K-Fold와 일반 K-Fold는 성능이 비슷해 선택에 주의가 필요. 합성 환경과 S&P 500 과거 데이터로 검증. 【검색확인(초록·2차 인용)】 — [DOI 10.1016/j.knosys.2024.112477](https://doi.org/10.1016/j.knosys.2024.112477); [SSRN 사본(Scribd)](https://www.scribd.com/document/725401650/SSRN-id4778909)
- 2025-12 arXiv 논문은 위 연구가 CPCV 우위를 보였음을 인용하면서도 "현실적 트레이딩에는 walk-forward가 업계 표준으로 남아 있다"고 적는다. 【검색확인】 — [arXiv 2512.12924](https://arxiv.org/pdf/2512.12924)
- Purged CV 개요: CPCV는 여러 train-test 분할을 체계적으로 만들고, 겹치는 표본을 purge하고 embargo 기간을 둔다. 【검색확인】 — [Wikipedia: Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation)
- 원전(【원전·미재확인】): López de Prado (2018) *Advances in Financial Machine Learning* 7장(purging: 테스트 라벨 구간과 시간상 겹치는 학습 표본 제거; embargo: 테스트 직후 학습 표본을 h ≈ 0.01·T 만큼 추가 제거), 12장(CPCV: T를 N개 그룹으로 나눠 k개를 테스트로 쓰는 C(N,k)개 분할 → 백테스트 경로 수 `φ[N,k] = (k/N)·C(N,k)`). — [Wiley](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086); 구현 문서 [skfolio CombinatorialPurgedCV](https://skfolio.org/generated/skfolio.model_selection.CombinatorialPurgedCV.html)
- Walk-forward 원전(【원전·미재확인】): Pardo (2008) *The Evaluation and Optimization of Trading Strategies* 2판 — rolling/anchored walk-forward와 Walk-Forward Efficiency(연율 OOS 수익 ÷ 연율 IS 수익; 통상 50% 이상을 견고함의 신호로 사용). — [Wiley](https://www.wiley.com/en-us/The+Evaluation+and+Optimization+of+Trading+Strategies%2C+2nd+Edition-p-9780470128015)
- DRL 암호화폐 연구(Gort et al. 2022)는 walk-forward·k-fold 대신 CPCV 기반으로 과최적화 확률을 추정해 과최적화 에이전트를 기각하는 절차를 제안. 【검색확인】 — [arXiv 2209.05559](https://arxiv.org/pdf/2209.05559)

### Inferences
- 【자체 계산】 CPCV 경로 수: (N=6,k=2) → 15분할·5경로, (8,2) → 28분할·7경로, (10,2) → 45분할·9경로. CSCV 분할 수: S=8 → 70, S=10 → 252, S=16 → 12,870.
- 방법별 한계와 본 시스템 적용:
  - **Rolling WF**: 레짐 변화에 적응하지만 창마다 표본이 작아 파라미터가 흔들림. 몇 달 데이터에서는 창이 2~4개뿐이라 경로가 1개 → 분산 큰 단일 추정.
  - **Anchored(expanding) WF**: 소표본에서 학습 표본을 최대화. 정상성 가정이 더 강함. **초기 단계 권장 기본값.**
  - **Purged k-fold + embargo**: 표본 효율이 좋지만 "미래로 학습해 과거를 테스트"하므로 실거래 시뮬레이션은 아님. 본 전략은 보유시간이 분~시간이고 장 마감 전 청산이므로 **거래일을 분할 단위로 하고 embargo 1거래일**이면 라벨 겹침이 사실상 제거된다.
  - **CPCV**: 경로 분포(Sharpe 분포, PBO)를 주지만 그룹당 거래 수가 적으면(예: 200거래/6그룹 ≈ 33건) 경로별 추정이 매우 시끄럽다. 300거래 이상부터 (6,2) 정도만 권장.
- 규칙 기반 "puddle" 탐지기의 TP/SL/시간 파라미터 선택에는 CV보다 **CSCV(PBO) + DSR**이 직접적이다(학습이 아니라 선택 문제이므로). ML 스코어러(메타 모델)에는 purged CV가 필요하다(특징에 롤링 통계가 들어가 누수 경로가 생김).
- 누수 체크리스트(분봉 특유): 신호 시각 이후 봉의 고가/저가로 만든 특징, 당일 종가 기반 정규화, 전체 표본으로 맞춘 스케일러, 같은 날 같은 종목의 연속 신호가 train/test에 갈라지는 것.

### Gaps
- Arian et al. 본문(합성 환경 설정, 수치)은 미열람 — 결론은 초록·2차 인용 수준.
- 분봉 데이 트레이딩 규칙에 대해 WF vs CPCV를 직접 비교한 실증 연구는 찾지 못함.
- mlfinlab 공식 문서 URL은 이번 세션에서 확인하지 못해 skfolio 문서로 대체.

---

## 3. 몇 건의 거래가 필요한가: 검정력 분석 · 순차 검정(SPRT / Beta 갱신 / confidence sequence) · 부트스트랩 · 같은 날 군집 처리

### Takeaway
TP 0.9 / SL 0.5 / 비용 0.25에서 손익분기 승률은 53.57%이고, +3%p 엣지를 단측 5%·검정력 80%로 검출하려면 약 **1,700건**, +5%p는 약 **610건**, +10%p는 약 **150건**이 필요하다. 따라서 수십~수백 건 단계에서는 "통과/탈락/계속 수집" 3분기 순차 규칙(SPRT 또는 anytime-valid 방식)과 거래일 단위 군집 부트스트랩을 써야 하며, 같은 날 거래를 독립으로 세면 유의성이 과장된다.

### Cited Findings
- Wald의 SPRT: 누적 로그우도비 `Λ_n = Σ ln[f₁(x_i)/f₀(x_i)]` 가 `A = ln((1−β)/α)` 이상이면 H₁ 채택, `B = ln(β/(1−α))` 이하이면 H₀ 채택, 그 사이면 계속 표본 수집. 【원전·미재확인】 — [Wald (1945), Annals of Mathematical Statistics 16(2)](https://doi.org/10.1214/aoms/1177731118)
- Confidence sequence(CS): "제한 없는 시간 지평에 걸쳐 균일하게 유효한 신뢰구간의 열". Howard, Ramdas, McAuliffe & Sekhon (2021)은 폭이 0으로 수렴하고 비모수 조건에서 비점근적 포함확률을 보장하는 CS를 개발했고, Cramér–Chernoff 방법·반복로그 법칙·SPRT를 연결한다. 【검색확인】 — [Annals of Statistics 49(2)](https://projecteuclid.org/journals/annals-of-statistics/volume-49/issue-2/Time-uniform-nonparametric-nonasymptotic-confidence-sequences/10.1214/20-AOS1991.full)
- Waudby-Smith & Ramdas, "Estimating means of bounded random variables by betting"(JRSS-B): 유계 확률변수의 평균에 대한 신뢰구간·시간균일 CS를 "베팅(마팅게일)" 방식으로 구성. 【검색확인】 — [arXiv 2010.09686](https://arxiv.org/pdf/2010.09686)
- 베팅 기반 구간은 분산 적응적이어서 Hoeffding형보다 좁다(시뮬레이션에서 우월). 【검색확인】 — [Shekhar & Ramdas, arXiv 2310.01547](https://arxiv.org/pdf/2310.01547v2.pdf)
- 연속 모니터링(A/B 테스트의 "엿보기") 문제와 always-valid p값: Johari, Koomen, Pekelis & Walsh. 【원전·미재확인】 — [arXiv 1512.04922](https://arxiv.org/abs/1512.04922); 개관: Ramdas, Grünwald, Vovk & Shafer (2023), "Game-theoretic statistics and safe anytime-valid inference" — [arXiv 2210.01948](https://arxiv.org/abs/2210.01948)
- Stationary bootstrap: 기하분포(평균 1/p) 길이의 블록을 이어 붙여 약의존 정상 시계열을 재표집. 【원전·미재확인】 — [Politis & Romano (1994), JASA 89(428)](https://doi.org/10.1080/01621459.1994.10476870); 블록 길이 자동 선택 — [Politis & White (2004), Econometric Reviews 23(1)](https://doi.org/10.1081/ETC-120028836); 구현 — [arch.bootstrap 문서](https://arch.readthedocs.io/en/latest/bootstrap/bootstrap.html)
- 군집 표본의 추론: 군집 수가 적을 때는 군집 단위 부트스트랩(특히 wild cluster bootstrap)이 표준오차 과소추정을 완화. 【원전·미재확인】 — [Cameron, Gelbach & Miller (2008), REStat 90(3)](https://doi.org/10.1162/rest.90.3.414)
- 군집 내 상관 ρ, 군집 크기 m일 때 유효 표본 `n_eff = n / (1 + (m−1)ρ)` (design effect). 【원전·미재확인】 — [Wikipedia: Design effect](https://en.wikipedia.org/wiki/Design_effect)
- 데이 트레이딩의 사전확률(기저율)은 낮다: 대만 전수 자료(1992–2006)에서 데이 트레이더 집계 성과는 수수료 차감 후 15년 모두 음(−)이었고 소수만 지속적 능력을 보임; 브라질 미니 지수선물에서는 지속 데이 트레이더 1,551명 중 47명(3.0%)만 수수료 차감 후 이익, 학습 효과 증거 없음; KOSPI200 선물에서도 국내 개인 데이 트레이더는 상당한 손실, 거래가 잦을수록 손실 가능성 증가. 【검색확인】 — [Barber, Lee, Liu & Odean (Haas PDF)](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf); [Chague, De-Losso & Giovannetti, SSRN 3423101](https://papers.ssrn.com/abstract=3423101); [SKKU, KOSPI200 선물 데이 트레이딩 연구](https://pure.skku.edu/en/publications/the-profitability-of-day-trading-an-empirical-study-using-high-qu/)

### Inferences
- 【자체 계산】 **손익분기 승률과 비용 민감도** (W = 0.9 − c, L = 0.5 + c, p_BE = L/1.4):

  | 왕복비용 c | 0% | 0.05% | 0.10% | 0.15% | 0.20% | 0.25% | 0.30% | 0.35% |
  |---|---|---|---|---|---|---|---|---|
  | p_BE | 35.7% | 39.3% | 42.9% | 46.4% | 50.0% | **53.6%** | 57.1% | 60.7% |

  → 비용 0.05%p가 손익분기 승률 약 3.6%p에 해당. **비용 모델의 오차가 엣지 추정 오차보다 크다.** 거래세가 없는 ETF(8절)는 손익분기가 구조적으로 낮다.
- 【자체 계산】 **검정력**(H₀: p = 53.57%, 정규근사, `n = [(z_α·√(p₀q₀) + z_β·√(p₁q₁)) / (p₁−p₀)]²`):

  | 엣지(승률 −p_BE) | 순 기대값/거래 | 거래당 Sharpe | n (단측 5%, 검정력 80%) | 검정력 90% | 검정력 50% |
  |---|---|---|---|---|---|
  | +2%p | +0.028% | 0.040 | 3,835 | 5,308 | 1,682 |
  | **+3%p** | +0.042% | 0.061 | **1,702** | 2,354 | 748 |
  | +5%p | +0.070% | 0.102 | 610 | 843 | 269 |
  | +7%p | +0.098% | 0.143 | 310 | 427 | 137 |
  | +10%p | +0.140% | 0.208 | 150 | 207 | 67 |

  평균수익 t-검정도 같은 결론: `n ≈ ((z_α+z_β)/SR_trade)²`. t>3.0(HLZ 기준)을 "기대상" 달성하려면 `n = (3/SR_trade)²` → SR 0.06이면 2,500건, 0.10이면 900건, 0.20이면 225건.
- 【자체 계산】 고정 n에서 "승률 95% 단측 하한 > p_BE"가 되려면 관측 승률이 n=30 → 68.6%, 50 → 65.2%, 100 → 61.8%, 200 → 59.4%, 300 → 58.3%, 500 → 57.2%, 1,000 → 56.2%, 2,000 → 55.4% 이상이어야 한다. 100~300건에서는 **+5~8%p 이상의 큰 엣지만** 통과한다 — 이것이 정상이며 게이트를 낮출 이유가 아니다.
- 【자체 계산】 **SPRT 설계 예**(α=0.05, β=0.20 → A = +2.773, B = −1.558). H₀: p = 53.57% vs H₁: p = 58.57%(+5%p)면 승 1건당 +0.0892, 패 1건당 −0.1139를 누적. 기대 표본 수(Wald 근사): H₁ 참일 때 ≈ 377건, H₀ 참일 때 ≈ 263건(고정표본 610건 대비 약 40~55% 절감). H₁을 +3%p로 잡으면 ≈ 1,050건 / 736건. → **"탈락"은 통과보다 빨리 결정된다**는 점이 소표본 시스템에 유리.
- 【자체 계산】 **Beta 사후확률 규칙**(승률 p ~ Beta(a₀+승, b₀+패); P(p > p_BE | data)). 회의적 사전분포 = 손익분기 중심의 가상 20거래 Beta(10.7, 9.3):

  | 관측 | 승률 | P(p>p_BE) 평탄 사전 | 회의적 사전 |
  |---|---|---|---|
  | 30/50 | 60% | 0.814 | 0.783 |
  | 60/100 | 60% | 0.899 | 0.883 |
  | 116/200 | 58% | 0.894 | 0.886 |
  | 120/200 | 60% | 0.966 | 0.960 |
  | 174/300 | 58% | 0.938 | 0.933 |
  | 290/500 | 58% | 0.976 | 0.975 |
  | 285/500 | 57% | 0.938 | 0.935 |

  주의: 사후확률 임계값을 매 거래마다 들여다보며 멈추는 규칙은 빈도주의 1종 오류를 보장하지 않는다. 보장이 필요하면 아래 anytime-valid 형식을 쓴다.
- **Anytime-valid 간편 구현(제안)**: 사전분포를 (p_BE, 1] 위로 제한한 Beta 혼합 우도비 `M_n = ∫ Π (p/p_BE)^{x_i} ((1−p)/(1−p_BE))^{1−x_i} dπ(p)` 는 p ≤ p_BE 하에서 비음 초마팅게일이므로 Ville 부등식에 의해 "`M_n ≥ 1/α`가 되는 첫 순간 통과"는 언제 멈추든 1종 오류 ≤ α(위 Ramdas et al. 2023의 일반 원리 적용; 본 노트의 구성). 시간청산 때문에 결과가 2값이 아니므로 실제로는 **순수익을 [−(SL+c+슬리피지 상한), TP−c] 로 유계화**한 뒤 Waudby-Smith–Ramdas 베팅 CS로 "평균 순수익의 하한 > 0"을 모니터링하는 편이 일반적이다.
- **3분기 게이트 초안**: (통과) 최소 100거래·최소 20~30거래일 충족 후, anytime-valid 하한 > 0 **그리고** 거래일 군집 부트스트랩 95% 하한 > 0 / (탈락) 반대 방향 SPRT 경계 도달, 또는 P(p>p_BE) < 0.10, 또는 사전 정한 최대 표본(예: 500거래)까지 통과 못 함(무익성 중단) / (계속) 그 외.
- **같은 날 군집 처리**: 장중 시장 방향이 그날의 모든 dip-rebound 거래를 함께 좌우하므로 ① 통계의 기본 단위를 "거래일 손익"으로 병행 보고, ② 부트스트랩은 **거래일을 통째로 재표집**(날짜 간 자기상관이 의심되면 날짜열에 stationary bootstrap), ③ n 대신 n_eff를 게이트에 사용(예: 하루 평균 4거래·일중 상관 0.2면 n_eff = n/1.6), ④ 동일 종목·동일 시간대 중복 신호는 1건으로 병합하거나 쿨다운을 둔다.

### Gaps
- 시간청산(TP·SL 외 결과)이 섞인 실제 손익분포에서의 정확한 필요 표본 수는 백테스트 손익분포로 시뮬레이션해야 함(위 표는 2값 근사).
- 일중 거래 간 상관 ρ의 한국 주식 실측값은 문헌에서 찾지 못함 — 자체 로그로 추정해야 한다.
- Barber et al.의 "예측 가능하게 이익을 내는 데이 트레이더 비율(통상 1% 미만으로 인용)" 수치는 이번 검색에서 원문 확인 실패.

---

## 4. 라벨링과 메타 라벨링: triple-barrier · meta-labeling(López de Prado 2018; Joubert 2022; Hudson & Thames)

### Takeaway
본 시스템의 TP/SL/시간청산은 그 자체가 triple-barrier 라벨이고, "AI는 신호 점수만 매긴다"는 설계는 메타 라벨링과 정확히 같은 구조다. 다만 메타 라벨링의 효과 증거는 주로 합성 데이터·시뮬레이션이며 동료심사된 실거래 증거나 반박 연구는 드물다 — 과신하지 말고 "거르기 전/후"를 shadow로 비교해 검증해야 한다.

### Cited Findings
- 원전(【원전·미재확인】): López de Prado (2018) AFML 3장 — triple-barrier(상단=익절, 하단=손절, 수직=시간 만료 중 먼저 닿는 장벽으로 라벨), meta-labeling(1차 모델이 방향을 정하고, 2차 이진 분류기가 "이 신호를 취할지"와 확률 기반 베팅 크기를 결정; 1차 모델의 높은 recall을 유지하면서 precision을 올려 F1 개선). — [Wiley](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086)
- Joubert (2022), "Meta-Labeling: Theory and Framework", Journal of Financial Data Science 4(3): 31–44 — 여러 문헌을 실무자용 프레임워크로 통합. 후속으로 Meyer·Barziy·Joubert (2023)의 보정(calibration)·포지션 사이징 논문, Thumm·Barucca·Joubert의 앙상블 메타 라벨링(여러 레짐·비선형 데이터에서 앙상블이 가장 도움) 등이 있다. 【검색확인】 — [Wikipedia: Meta-Labeling](https://en.wikipedia.org/wiki/Meta-Labeling); [Hudson & Thames meta-labeling 저장소](https://github.com/hudson-and-thames/meta-labeling)
- 증거의 한계: 뒷받침하는 실증 연구는 주로 합성 데이터와 모의 트레이딩에 의존해 실시장 일반화에 한계가 있다. 【검색확인】 — [Wikipedia(초안) 미러](https://wikiless.lunar.icu/wiki/Draft:Meta-Labeling?lang=en)
- Hudson & Thames의 S&P500 E-mini 선물 실험("Does Meta Labeling Add to Signal Efficacy?")과 토이 예제는 메타 라벨링이 false positive를 걸러 F1을 높인다고 보고(추세추종·평균회귀 1차 모델). 【검색확인(스니펫 수준)】 — [Hudson & Thames 글](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/embed/); [Toy example](https://hudsonthames.org/meta-labeling-a-toy-example/)
- 비판(비공식): "메타 모델이 1차 모델보다 더 많은 정보를 뽑아낼 이유가 있는가", 1차 모델이 단순(항상 롱)하면 성과 부담이 전부 메타 모델로 넘어간다, 평균 Sharpe가 오히려 낮아졌다는 사용자 보고. 【검색확인】 — [QuantConnect 포럼 "why meta labeling is not a silver bullet"](https://www.quantconnect.com/forum/discussion/14706/why-meta-labeling-is-not-a-silver-bullet/)
- 실무 함정: 메타 라벨 분포가 불균형이면 분류기가 정확해 보이면서도 가치를 더하지 못할 수 있다. 【검색확인】 — [quant-lessons: meta-labeling](https://5x5x5x5.github.io/quant-lessons/ml/meta-labeling/)

### Inferences
- 본 시스템 매핑: 1차 모델 = puddle 탐지 규칙(방향은 항상 롱), 라벨 = 거래 결과(TP=1, SL=0, 시간청산은 순수익 부호 또는 별도 클래스), 2차 모델 = P(성공 | 신호 시점 특징). **주문은 내지 않고 점수만** → 점수 하위 x%를 거르거나 크기를 줄이는 정책은 별도 규칙 계층이 수행.
- 라벨 설계 권고: ① 이진 라벨은 "비용 차감 순수익 > 0". ② 회귀 타깃으로 R-multiple(순수익/위험)도 함께 저장. ③ **거른 신호도 가상으로 끝까지 추적해 라벨을 남긴다**(선택 편향 방지: 취한 거래만 학습하면 메타 모델이 자기 결정으로 만든 표본만 보게 됨). 페이퍼 단계에서는 모든 신호를 다 "거래"한 것으로 기록 가능하다는 점이 큰 장점.
- 평가는 분류 지표(F1)보다 **경제적 지표**로: 점수 상위 버킷의 순 기대값, "필터 적용 후 총 기대이익 = 남은 거래 수 × 거래당 기대값"이 무필터보다 큰가(거래 수가 줄어 총이익이 감소하는 경우가 흔함), 보정 곡선(Brier/log loss).
- 필터 임계값 자체도 "시도"다 → 임계값 후보 수를 1절의 N에 포함.
- 소표본에서는 손익분기 승률이 53.6%로 높아 클래스가 대략 균형이므로 불균형 문제는 작지만, 반대로 기저 승률이 p_BE 근처면 메타 모델이 올릴 수 있는 여지(precision 상승폭)가 엣지의 전부가 된다.

### Gaps
- Hudson & Thames 글의 정량 결과(precision/recall/Sharpe 수치)는 사이트 접근 차단으로 확인 못 함.
- Joubert(2022) 본문·DOI 직접 확인 못 함(2차 자료가 DOI 비활성 상태를 언급).
- 메타 라벨링의 실거래(라이브) 성과에 대한 동료심사 실증은 찾지 못함.

---

## 5. 장중 반등(reversal) 스코어링용 특징과 과최적화에 강한 특징 중요도

### Takeaway
문헌상 근거가 가장 분명한 축은 (1) 변동성 상태 — 단기 반전 수익은 VIX가 높을 때 크다(동시에 위험도 크다), (2) 호가 불균형(OFI) — 단기 가격변화의 대부분을 선형적으로 설명, (3) "뉴스 없는·종목 고유의" 하락이 더 잘 되돌려진다는 유동성 공급 해석이다. 특징 중요도는 MDI 대신 purged CV 기반 MDA를 군집 단위로 계산하고, SHAP는 설명 도구로만 쓴다.

### Cited Findings
- **변동성 상태**: Nagel (2012), "Evaporating Liquidity"(RFS 25(7)) — 단기 반전 전략 수익은 유동성 공급 수익의 대리변수이며, VIX가 이후 반전 수익을 예측한다(동시적 상관이 아니라 예측적). 금융 불안기(2007–09)에 기대수익과 조건부 Sharpe가 급등, 평소 수익이 낮은 산업 포트폴리오 반전도 VIX가 높을 때는 높은 수익. 해석: 제약된 중개자의 유동성 공급 철수. 【검색확인】 — [NBER w17653](https://www.nber.org/papers/W17653); [RFS 서지](https://econpapers.repec.org/RePEc:oup:rfinst:v:25:y:2012:i:7:p:2005-2039)
- **호가 불균형**: Cont, Kukanov & Stoikov (2014), "The Price Impact of Order Book Events" — 짧은 구간의 가격변화는 최우선 호가의 order flow imbalance(OFI)가 대부분 설명하고, 관계는 선형이며 기울기는 시장 깊이에 반비례. 일중 계절성 조정 후에도, 시간 척도·종목에 걸쳐 견고(NYSE 50종목, Level I). 거래량과의 관계(제곱근 법칙)는 더 시끄럽고 덜 견고. 【검색확인】 — [arXiv 1011.6402](https://arxiv.org/abs/1011.6402); [J. Financial Econometrics 12(1)](https://econpapers.repec.org/RePEc:oup:jfinec:v:12:y:2013:i:1:p:47-88)
- **지정가 체결과 역선택**: 메이커 주문의 체결 확률과 체결 후 수익은 음의 관계 — 잘 체결되는 주문일수록 역선택된 주문. 【검색확인】 — [arXiv 2502.18625](https://arxiv.org/pdf/2502.18625v2); ["The Negative Drift of a Limit Order Fill", arXiv 2407.16527](https://arxiv.org/pdf/2407.16527)
- **한국 개인 성과의 타이밍 요인**: KOSPI에서 개인투자자의 낮은 성과는 종목 선택보다 거래 타이밍 선택과 관련. 【검색확인】 — [KoreaScience 논문(2024)](https://koreascience.kr/article/JAKO202431663254538.pdf)
- 아래는 표준 문헌이나 이번 세션에서 재확인하지 못한 근거(【원전·미재확인】):
  - **뉴스 유무**: Tetlock (2010) — 공개 뉴스가 있는 날의 수익률은 뉴스 없는 날보다 덜 되돌려진다(뉴스성 하락은 정보, 무뉴스 하락은 유동성 충격). — [RFS 23(9)](https://doi.org/10.1093/rfs/hhq052)
  - **종목 고유 vs 산업/시장 공통**: Da, Liu & Schaumburg (2014) — 산업 내 잔차 수익 기준 단기 반전이 원수익 기준보다 강하고, 유동성 충격 성분이 반전을 주도. — [Management Science 60(3)](https://doi.org/10.1287/mnsc.2013.1766)
  - **유동성·회전율**: Avramov, Chordia & Goyal (2006) — 단기 반전은 비유동적·고회전 종목에 집중. — [Journal of Finance 61(5)](https://doi.org/10.1111/j.1540-6261.2006.01060.x)
  - **시간대**: Heston, Korajczyk & Sadka (2010) — 30분 단위 수익률이 하루 간격의 같은 시간대에서 지속되는 일중 주기성. — [Journal of Finance 65(4)](https://doi.org/10.1111/j.1540-6261.2010.01573.x); Gao, Han, Li & Zhou (2018) — 첫 30분 수익이 마지막 30분 수익을 예측("market intraday momentum"). — [JFE 129(2)](https://doi.org/10.1016/j.jfineco.2018.05.009)
- **특징 중요도**
  - MDI(불순도 기반)는 편향되고, 대체 효과(상관된 특징) 하에서 중복 특징의 중요도를 낮게 보고한다; MDA(순열)는 중복 특징을 "완전히 지워" 버릴 수 있다. López de Prado *Machine Learning for Asset Managers* §6.5.2의 해법: 특징을 의존성으로 군집화하고 군집 단위로 점수화(clustered MDI = 군집 내 불순도 합, clustered MDA = 군집의 모든 열을 함께 순열). 한계: 다른 특징과 결합해야만 유용한 특징은 무용한 것으로 나온다. 【검색확인(2차 요약)】 — [MQL5 정리 글](https://www.mql5.com/en/articles/23564); 원전 [MLAM, Cambridge Elements](https://doi.org/10.1017/9781108883658)
  - MDA·LIME·SHAP 모두 특징 중요도 순위의 변동성이 클 수 있고, 원인으로 대체 효과가 지목됨; 군집 기반 선택(cMDA)이 안정적이라는 보고는 Ernest Chan의 블로그(자사 제품 PredictNow.ai 연관) 출처이므로 벤더 인접 자료로 취급. 【검색확인】 — [Chan 블로그(2021)](https://epchan.blogspot.com/2021/01/the-amazing-efficacy-of-cluster-based.html?m=1)
  - 순열 중요도/SHAP의 구조적 문제(【원전·미재확인】): 상관 특징에서 순열은 모형을 외삽 영역으로 밀어 넣는다 — [Hooker, Mentch & Zhou, arXiv 1905.03151](https://arxiv.org/abs/1905.03151); Shapley 기반 설명의 수학적·인과적 한계 — [Kumar et al., arXiv 2002.11097](https://arxiv.org/abs/2002.11097); 랜덤포레스트 불순도 중요도의 편향 — [Strobl et al. (2007), BMC Bioinformatics](https://doi.org/10.1186/1471-2105-8-25)

### Inferences
- **사전 등록 특징 목록 제안**(신호 시각 t까지의 정보만, 종목별 롤링 z-score 또는 백분위로 정규화; 기대 부호는 가설이며 데이터로 확인할 것):

  | 특징 | 정의 예 | 기대 방향(가설) | 근거 |
  |---|---|---|---|
  | 변동성 상태 | 당일 실현변동성 ÷ 20일 평균, VKOSPI 수준 | 반등폭↑ 그러나 SL 도달 확률도↑ (비단조 가능) | Nagel 2012 |
  | 상대 거래량 | 하락 구간 거래량 ÷ 동시간대 20일 평균 | 투매성(climactic) 거래량은 반등에 유리하다는 실무 가설; 뉴스성 급증은 불리 | Avramov et al. 2006; Tetlock 2010 |
  | 호가 불균형 | (매수잔량−매도잔량)/(합), 최근 1~3분 OFI | 매수 우위 전환 시 유리 | Cont et al. 2014 |
  | 시장/섹터 동조 | 종목 수익 − β×(KOSPI200/섹터 ETF 수익), 같은 창 | 종목 고유 하락(잔차 큼)·시장 안정 → 유리; 시장 동반 급락 → 불리 | Da et al. 2014 |
  | 시간대 | 장 시작 후 경과 분, 구간 더미(개장 30분·점심·마감 30분) | 구간별 상이(개장 직후 스프레드·변동성 큼) | Heston et al. 2010; Gao et al. 2018 |
  | VWAP 괴리 | (가격−당일 VWAP)/ATR | 과도한 음(−) 괴리는 반등 여지, 추세일에는 계속 하락 | 직접 학술 근거 약함(아래 Gaps) |
  | 전일 범위·갭 | 전일 (고−저)/종가, 시가 갭 | 큰 갭다운 후 dip은 뉴스성일 가능성 | Tetlock 2010(간접) |
  | 스프레드 | 호가 스프레드/가격, 틱/가격 | 넓을수록 비용↑·불리 | 8절 |

- 표본이 수백 건이면 **특징 5~8개가 상한**(6절의 EPV 규칙). 특징 추가 자체가 다중검정이므로 "특징 후보 목록"을 사전 고정하고 버전 관리.
- 중요도 절차 제안: ① 특징 상관행렬로 군집(계층적 군집) → ② purged(거래일 단위) CV에서 OOS log-loss 기준 **clustered MDA** → ③ 무작위 잡음 특징 2~3개를 넣어 그보다 중요도가 낮은 군집은 제거 → ④ SHAP는 방향성(부호가 가설과 맞는지) 점검용으로만.
- 변동성 특징은 "수익↑·위험↑"가 동시에 일어나므로 승률이 아니라 **순 기대값과 SL 도달률**을 따로 봐야 한다. Nagel의 결과는 일간·횡단면 반전 포트폴리오에 관한 것이어서 단일 종목 분 단위 dip에 그대로 옮겨지지 않는다.

### Gaps
- VWAP 괴리, 상대 거래량의 "장중 반등 예측력"에 대한 직접적 학술 근거는 이번 조사에서 확보하지 못함(실무 통념 수준).
- 한국 시장(KOSPI/KOSDAQ) 분 단위 반전·과잉반응에 대한 직접 실증은 검색에서 나오지 않음.
- Tetlock, Da et al., Avramov et al., Heston et al., Gao et al.은 표준 인용이지만 이번 세션에서 초록을 재확인하지 못함(마지막 검색 배치 미실행).
- Toss Securities Open API가 호가 잔량(10단계)·체결 틱을 어느 수준까지 제공하는지는 본 노트 범위 밖 — OFI 특징 가능 여부는 API 조사 결과에 따름.

---

## 6. 소규모 테이블 데이터용 모델과 보정, 그리고 ML이 단순 규칙보다 못한 경우

### Takeaway
수백 건 표본에서는 강한 사전 구조를 가진 단순 모델(L2 로지스틱, 종목 간 부분 풀링)이 기본이고, GBDT는 얕게·단조 제약을 걸어 1,000건 이후에 도전자로 둔다. 금융 예측은 신호 대 잡음비가 극히 낮아 ML의 긍정적 결과(Gu–Kelly–Xiu)도 "월간·수만 종목·수십 년" 규모에서 나온 것이며, 최근에는 복잡성의 효용 자체가 반박되고 있다.

### Cited Findings
- 긍정 사례: Gu, Kelly & Xiu (2020), "Empirical Asset Pricing via Machine Learning"(RFS 33(5)) — 미국 주식 월간 수익 예측에서 트리·신경망이 선형 대비 우수(대규모 패널: 약 3만 종목, 1957–2016). 【원전·미재확인】 — [DOI 10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009)
- 경고: Israel, Kelly & Moskowitz (2020), "Can Machines 'Learn' Finance?" — 금융은 (i) 데이터가 작고 (ii) 신호 대 잡음비가 낮고 (iii) 시장이 적응·진화하며 (iv) 해석 가능성이 요구되어, ML의 성과 기대치를 낮춰야 한다. 【원전·미재확인】 — [SSRN 3624052](https://papers.ssrn.com/abstract=3624052)
- Avramov, Cheng & Metzker (2023) — ML 신호의 수익성은 마이크로캡·부실 종목 등 차익거래가 어려운 영역에 집중되고 거래비용·경제적 제약을 넣으면 크게 줄어든다. 【원전·미재확인】 — [Management Science 69(5)](https://doi.org/10.1287/mnsc.2022.4449)
- "복잡성의 미덕" 논쟁: Kelly, Malamud & Zhou (2024, JF 79(1))는 관측 수보다 파라미터가 많은 모형이 단순 모형보다 예측력을 덜 과소평가한다고 주장. 【검색확인】 — [SFI](https://www.sfi.ch/en/publications/the-virtue-of-complexity-in-return-prediction); [JF 서지](https://econpapers.repec.org/RePEc:bla:jfinan:v:79:y:2024:i:1:p:459-503)
- 반박: Nagel (2025), "Seemingly Virtuous Complexity in Return Prediction" — 특징 수가 관측 수를 크게 넘는 ridgeless 회귀는 사실상 학습 창의 최근 수익을 평균하는 것이며, 결과 전략은 기계적으로 생기는 변동성 타이밍 모멘텀이다. 강한 반전을 가진 인공 데이터를 넣어도 같은 전략이 나오므로 실제 수익 과정을 학습한 것이 아니다. 【검색확인】 — [BFI WP 2025-104](https://bfi.uchicago.edu/wp-content/uploads/2025/08/BFI_WP_2025-104.pdf); [NBER 컨퍼런스 버전](https://conference.nber.org/conf_papers/f221481/f221481.pdf)
- 소표본 테이블 모델: TabPFN(Hollmann et al., Nature 637, 2025-01) — 수백만 합성 데이터셋으로 사전학습한 테이블 파운데이션 모델이 **표본 10,000개 이하** 데이터셋에서 기존 방법(4시간 튜닝한 GBDT 포함)을 큰 폭으로 앞섬. 후속 TabPFN-2.5 기술보고서(2025-11)는 ≤10,000행·500특징 분류에서 기본 XGBoost 대비 승률 100%를 주장하나 벤더(Prior Labs) 사전공개본. 【검색확인】 — [Nature / PubMed](https://pubmed.ncbi.nlm.nih.gov/39780007/); [PMC 전문](https://pmc.ncbi.nlm.nih.gov/articles/PMC11711098/); [arXiv 2511.08667](https://arxiv.org/pdf/2511.08667v2)
- 테이블 데이터에서 트리 모델이 딥러닝보다 강한 이유(비정보 특징에 강건 등). 【원전·미재확인】 — [Grinsztajn, Oyallon & Varoquaux (2022), arXiv 2207.08815](https://arxiv.org/abs/2207.08815)
- 보정(【원전·미재확인】): Platt scaling(시그모이드)은 보정 표본이 작을 때(대략 1,000 미만) 유리, isotonic 회귀는 더 유연하지만 소표본에서 과적합. — [Niculescu-Mizil & Caruana (2005), ICML](https://doi.org/10.1145/1102351.1102430); [scikit-learn calibration 문서](https://scikit-learn.org/stable/modules/calibration.html)
- 단조 제약 GBDT 구현 참고. — [XGBoost monotonic constraints 튜토리얼](https://xgboost.readthedocs.io/en/stable/tutorials/monotonic.html)
- 로지스틱 회귀의 표본 규칙(【원전·미재확인】): 변수당 사건 수(EPV) 10 미만이면 계수 편향·분산 급증. — [Peduzzi et al. (1996), J. Clinical Epidemiology 49(12)](https://doi.org/10.1016/S0895-4356(96)00236-3)
- 메타 라벨링 문헌도 확률 보정을 포지션 사이징의 전제로 다룸(Meyer, Barziy & Joubert 2023). 【검색확인】 — [Wikipedia: Meta-Labeling](https://en.wikipedia.org/wiki/Meta-Labeling)

### Inferences
- **표본 단계별 학습 설계(제안)**

  | 누적 거래(라벨) | 허용 모델 | 역할 |
  |---|---|---|
  | < 100 | 모델 없음. 로깅·특징 품질 점검, 버킷별 승률을 Beta 사후분포로 표시 | 관찰만 |
  | 100~300 | 종목 간 부분 풀링 Beta-binomial/계층적 로지스틱(절편만 종목별), 특징 ≤ 3~5 | shadow 점수(결정에 미사용) |
  | 300~1,000 | L2(또는 elastic-net) 로지스틱, 특징 5~8, 사전 부호 가설, Platt 보정 | 하위 분위 신호 "크기 축소" 정도의 약한 개입 |
  | 1,000~3,000 | 얕은 GBDT(depth 2~3, 큰 min_child, 강한 수축·서브샘플, 단조 제약) 또는 TabPFN을 **도전자**로 | 챔피언(로지스틱) 대비 shadow 비교 |
  | > 3,000 | 앙상블·레짐별 모델 검토 | 정식 메타 라벨링 |

- EPV 10 기준: 200거래 중 소수 클래스가 약 90건이면 특징 9개가 이론적 상한 — 다중검정까지 감안하면 5개 이하가 안전.
- 계층적(부분 풀링) 모델이 소표본에 맞는 이유: 종목별 20~50건으로는 종목별 승률 추정이 무의미(95% 구간 ±14~18%p, 3절 표). 전체 평균으로 수축시키되 종목 효과가 데이터로 드러날 때만 벌어지게 한다. 간단 구현: 종목 i의 승률 사후평균 = (승_i + κ·p̄)/(n_i + κ), κ는 20~50 정도의 가상 표본 수(본 노트의 제안값).
- TabPFN은 "소표본 테이블"이라는 조건에는 맞지만, 벤치마크는 일반 테이블 과제이지 신호 대 잡음비가 극단적으로 낮은 금융 라벨이 아니다. 금융 라벨에 대한 검증 증거는 찾지 못했으므로 도전자 슬롯에서만 시험.
- ML이 단순 규칙보다 못한 전형 조건: (a) n < 수백, (b) 특징이 결과와 동시적(누수), (c) 레짐 변화로 학습·적용 분포 불일치, (d) 필터가 거래 수를 줄여 총이익·검정력 모두 감소, (e) 임계값·특징·모델 선택이 모두 추가 "시도"가 됨. → 기준선은 항상 "점수 없이 모든 신호 수용".
- 모델 평가지표: OOS log-loss/Brier가 "기저 승률만 예측하는 상수 모델"보다 유의하게 낮은지(거래일 군집 부트스트랩) 먼저 확인하고, 그다음에 경제적 지표.

### Gaps
- Gu–Kelly–Xiu의 세부 수치(OOS R² 등)와 Israel–Kelly–Moskowitz 인용문은 본문 미열람.
- 분 단위 개별 종목 신호에 대해 "정규화 로지스틱 vs GBDT vs TabPFN"을 수백~수천 표본에서 비교한 공개 실증은 찾지 못함.
- KMZ 측의 Nagel 반박에 대한 재반박은 검색에서 확인되지 않음.

---

## 7. 온라인 학습과 적응: 드리프트 탐지 · 밴딧/Thompson sampling · champion–challenger · 안전한 갱신 · RL의 실전 증거

### Takeaway
소표본·저빈도(하루 몇 건) 라벨에서는 "매 거래마다 가중치를 갱신하는 온라인 학습"보다 **주기적 재학습 + shadow 평가 + 사전 정의된 승격·롤백 규칙**이 안전하다. 드리프트는 거래 손익에 대한 CUSUM/Page-Hinkley로 감시하고, RL은 서베이들이 공통으로 비용·OOS 검증 부실을 지적하므로 현 단계에서 채택 근거가 약하다.

### Cited Findings
- 드리프트 탐지기: Page-Hinkley 검정은 CUSUM 계열로, 누적 통계량의 running max가 임계 λ>0을 (최소 변화 허용치 δ를 뺀 뒤) 넘으면 경보; River 구현은 기본 양측. ADWIN의 δ는 신뢰 파라미터(기본 0.002로 문서화된 구현 다수, 통상 범위 0.0001~0.1), River는 기본 32스텝마다 검사. 【검색확인】 — [arXiv 2610.05853](https://arxiv.org/pdf/2610.05853); [datadriftR 문서](https://cran.nics.utk.edu/cran/web/packages/datadriftR/refman/datadriftR.html)
- 원전(【원전·미재확인】): Page (1954) CUSUM — [Biometrika 41(1/2)](https://doi.org/10.1093/biomet/41.1-2.100); ADWIN — [Bifet & Gavaldà (2007), SIAM SDM](https://doi.org/10.1137/1.9781611972771.42); 개념 드리프트 서베이 — [Gama et al. (2014), ACM Computing Surveys 46(4)](https://doi.org/10.1145/2523813)
- CUSUM 설계 표준값(【원전·미재확인】): 표준화 관측에 대해 `S_t = max(0, S_{t−1} + (μ₀ − x_t) − k)`, `S_t > h` 면 경보. k = 0.5σ일 때 h = 4σ → 무변화 평균 경보 간격(ARL₀) ≈ 168, h = 5σ → ARL₀ ≈ 465; 1σ 이동 탐지까지 평균 ≈ 8.4 / 10.4 관측. — [NIST/SEMATECH e-Handbook: CUSUM Control Charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm)
- Thompson sampling: Russo, Van Roy, Kazerouni, Osband & Wen, "A Tutorial on Thompson Sampling"(FnT ML 11(1), 2018). Beta-Bernoulli 밴딧: 각 행동의 성공확률에 Beta 사전분포, 관측 보상 r과 1−r을 (α, β)에 더해 갱신, 매 시점 사후분포에서 표본을 뽑아 최댓값 행동 선택. 【검색확인】 — [arXiv 1707.02038](https://arxiv.org/abs/1707.02038); [Now Publishers](https://nowpublishers.com/article/Details/MAL-070)
- Shadow/champion–challenger: shadow 배포에서는 새 모델이 운영 트래픽을 병렬로 받지만 예측은 사용자에게 제공되지 않는다; 승격 게이트는 실트래픽 전에 정의하고, 도전자는 테스트셋이 아닌 실트래픽에서 이긴 뒤에만 승격; 롤백은 레지스트리 alias를 이전 버전으로 되돌리는 한 줄 변경 패턴; 승격 방식 선택지로 canary·A/B·shadow·bandit 할당. 【검색확인(실무 문서)】 — [DataRobot](https://www.datarobot.com/blog/introducing-mlops-champion-challenger-models/); [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/mlops-checklist/continuous-deployment.html); [Dataiku](https://blog.dataiku.com/mlops-champion-challenger-model-evaluation)
- RL 실전 증거:
  - 다수의 RL 접근은 현실적 거래비용을 넣으면 수익성 검정을 통과하지 못하며, 마찰 없는 환경에서만 존재하는 패턴을 착취했을 가능성을 시사; RL 모형은 거래비용을 고정으로 단순화하고 체결을 확실하다고 가정하는 경우가 많다. 【검색확인】 — [arXiv 2512.12924](https://arxiv.org/pdf/2512.12924); [Pippas et al., "The Evolution of Reinforcement Learning in Quantitative Finance: A Survey"(167편 검토), arXiv 2408.10932](https://arxiv.org/pdf/2408.10932)
  - 기존 DRL 연구는 백테스트 수익을 낙관적으로 보고했으나 과최적화에 따른 false positive 문제가 있을 수 있음 — 과최적화 확률을 추정하는 가설검정 제안. 【검색확인】 — [Gort et al., arXiv 2209.05559](https://arxiv.org/pdf/2209.05559)
  - "Deep Reinforcement Learning for Trading — A Critical Survey"(Data, 2021)는 커뮤니티 내 평가 일관성 부족을 지적. 【검색확인】 — [MDPI Data 6(11):119](https://mdpi.com/2306-5729/6/11/119)
  - RL 결과는 데이터 선택·특징·거래비용 가정·학습 절차·보상 설계·검증 프로토콜에 크게 좌우되어 누수 없는 재현 가능한 보고 표준이 필요. 【검색확인】 — [Brunel 리뷰](https://bura.brunel.ac.uk/bitstream/2438/34200/2/FullText.pdf)
- AFML의 대칭 CUSUM 필터(이벤트 샘플링)와 구조 변화 검정(17장)도 같은 계열 도구. 【원전·미재확인】 — [Wiley](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086)

### Inferences
- **드리프트 감시 설계(제안)**: 관측 x_t = 거래 순수익을 백테스트 기대값 μ₀·표준편차 σ로 표준화. 하방 CUSUM(k = 0.5, h = 4~5)을 **거래 단위와 거래일 단위** 둘 다로 운영. ARL₀ 168~465는 "엣지가 그대로여도 대략 그 정도 거래마다 한 번은 오경보"를 의미하므로, 경보 = 즉시 폐기가 아니라 **"크기 축소 + 재검증 진입"**으로 연결. ADWIN은 수백 개 이상의 관측이 쌓여야 의미 있는 창 비교가 되므로 거래 손익보다는 **특징 분포 드리프트**(분봉 단위 스프레드·변동성·상대 거래량)에 쓰는 편이 맞다.
- **페이퍼/shadow에서는 밴딧이 필요 없다**: 소액·페이퍼에서는 시장충격이 없다고 볼 수 있어 모든 파라미터 세트·모든 모델의 가상 결과를 같은 신호 위에서 동시에 관측할 수 있다(완전정보 설정). 탐색–활용 딜레마는 **실자금 배분**(한 번에 한 세트만 실제 체결을 관측)에서만 생긴다. 따라서 Thompson sampling의 적절한 용도는 ① 실거래 전환 후 챔피언/도전자 간 **자금 비중** 배분(Beta 사후에서 표본 추출 → 승률이 p_BE를 넘을 사후확률에 비례), ② 페이퍼→실거래 노출 비중의 점진적 확대. 비정상성 대응으로 사후분포에 망각계수(예: 매 거래 α,β ← γα, γβ, γ≈0.99)나 슬라이딩 윈도를 둔다(본 노트의 제안).
- **안전한 갱신 정책 초안**: ① 재학습은 고정 주기(예: 신규 라벨 50~100건 또는 월 1회) — 매 거래 온라인 갱신 금지. ② 새 모델은 최소 N거래(예: 100)·M거래일(예: 20) shadow. ③ 승격 조건: 도전자−챔피언의 **짝지은(paired) 거래별 차이**에 대한 거래일 군집 부트스트랩 하한 > 0, 그리고 보정 지표 악화 없음. ④ 승격 후 감시 창에서 CUSUM 경보 또는 사전 정의 낙폭 초과 시 자동 롤백(이전 버전 아티팩트·특징 스키마 보존). ⑤ 한 번에 한 가지만 변경(파라미터 세트 또는 스코어러). ⑥ 승격 시도 횟수도 누적 기록해 DSR의 N에 반영.
- AI 계층이 "점수만 매기고 주문은 내지 않는다"는 제약은 유지하고, 점수→행동 매핑(임계값, 크기 배수)은 사람이 승인하는 설정값으로 분리하면 롤백이 설정 되돌리기로 끝난다.
- RL은 (a) 상태–행동–보상 표본이 수백 건이면 학습 불가능에 가깝고 (b) 시뮬레이터(체결·비용)의 오차를 정책이 착취하며 (c) 서베이들이 OOS·비용 검증 부실을 공통 지적 → 로드맵에서 제외하거나 "연구 메모" 수준으로만 둔다.

### Gaps
- River 공식 문서의 Page-Hinkley 기본값(threshold, delta)은 확인하지 못함.
- 밴딧(Thompson sampling)을 전략 파라미터 선택·자금 배분에 적용한 실거래 성과의 신뢰할 만한 실증은 찾지 못함.
- "승격에 필요한 최소 shadow 표본"에 대한 문헌상 합의 수치는 없음(위 수치는 3절 검정력 계산에 근거한 제안).

---

## 8. 포지션 사이징과 리스크: Kelly/fractional Kelly · 추정오차 · 변동성 타기팅 · 고정 비율 위험 · 파산 위험 · 일손실 한도 · 낙폭 기반 축소

### Takeaway
엣지 추정이 불확실할수록 Kelly 비율은 줄여야 하며(Baker–McHale: 불확실성이 클수록 수축이 커짐), 본 시스템처럼 거래당 엣지가 0.05% 안팎이고 표본이 수백 건이면 "엣지의 신뢰 하한"은 0 이하이므로 Kelly는 **상한 계산용**으로만 쓰고 실제 크기는 거래당 계좌의 0.25~0.5% 고정 위험이 합리적이다. 변동성 타기팅은 in-sample 근거는 강하지만 실시간·비용 차감 후 성과는 논쟁 중이다.

### Cited Findings
- Kelly 기준(【원전·미재확인】): 승률 p, 배당비 b(이익/손실)일 때 `f* = (b·p − q)/b = p − q/b`; 연속 근사 `f* ≈ μ/σ²`. — [Kelly (1956), Bell System Technical Journal 35(4)](https://doi.org/10.1002/j.1538-7305.1956.tb03809.x); [Thorp (2006), "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market"](https://doi.org/10.1016/B978-044453248-0.50015-0)
- Fractional Kelly의 장단점(【원전·미재확인】): Kelly는 장기 성장률을 최대화하지만 단기 낙폭이 매우 크고, 분수 Kelly(예: half)는 성장률을 조금 포기하고 분산·낙폭을 크게 줄인다(half Kelly ≈ 성장률의 3/4, 변동성 1/2). — [MacLean, Thorp & Ziemba (2010), Quantitative Finance 10(7)](https://doi.org/10.1080/14697688.2010.506108)
- 추정오차 하의 Kelly: Baker & McHale (2013), "Optimal Betting Under Parameter Uncertainty: Improving the Kelly Criterion"(Decision Analysis 10(3)) — 승률이 불확실하면 베팅 크기를 수축해야 하며, 시뮬레이션과 테니스 베팅 데이터에서 수축 Kelly가 OOS에서 원 Kelly를 앞섬; 손으로 적용 가능한 근사 수축 추정량 제시. 【검색확인】 — [INFORMS](https://pubsonline.informs.org/doi/fpi/10.1287/deca.2013.0271); [EconPapers](https://econpapers.repec.org/RePEc:inm:ordeca:v:10:y:2013:i:3:p:189-199)
- Fractional Kelly는 이 문제의 통상적 처방이며 Baker–McHale은 2결과 설정에서 최적 Kelly 분수를 주는 수축 계수를 유도. 【검색확인】 — [Metel, "Kelly betting on horse races with uncertainty", arXiv 1701.02814](https://ar5iv.arxiv.org/html/1701.02814)
- 2차 설명: 그 모형에서는 불확실성의 분포를 특정하지 않아도 수축이 항상 최적이고, 불확실성이 클수록 최적 분수가 작아진다(원문 대조는 못 함). 【검색확인(2차)】 — [S. Morse 노트](https://stmorse.github.io/journal/odds4.html); 분포 강건 Kelly — [arXiv 1812.10371](https://arxiv.org/pdf/1812.10371)
- 변동성 타기팅:
  - Moreira & Muir (2017), "Volatility-Managed Portfolios"(JF 72(4)): 전월 실현분산의 역수로 노출을 조절 `f^σ_{t+1} = (c/σ̂²_t)·f_{t+1}` → 여러 팩터에서 양의 알파. 【원전·미재확인(공식)】 — [DOI 10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513)
  - Cederburg, O'Doherty, Wang & Yan (2020, JFE 138(1)): Moreira–Muir 표본에서 스패닝 회귀 알파는 유의하게 양(+)이지만, 직접 비교에서는 변동성 관리 포트폴리오가 체계적으로 우월하지 않다(103개 주식 포트폴리오 중 관리형 우위 53 vs 원형 우위 50). 회귀가 함의하는 전략은 실시간 구현 불가이고 합리적 OOS 버전은 대체로 더 낮은 확실성등가수익·Sharpe. 【검색확인】 — [논문 PDF](https://www.lehigh.edu/~xuy219/research/COWY.pdf); [JFE 서지](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117)
  - DeMiguel, Martín-Utrera & Uppal (2024, JF): Cederburg et al.은 OOS 실패를, Barroso & Detzel은 거래비용 후 소멸을 보였다고 정리하고, 조건부 다요인 포트폴리오는 OOS·비용 후에도 우월하다고 보고. 【검색확인】 — [LBS 저장소](https://lbsresearch.london.edu/id/eprint/3716/1/The%20Journal%20of%20Finance%20-%202024%20-%20DeMIGUEL%20-%20A%20Multifactor%20Perspective%20on%20Volatility%E2%80%90Managed%20Portfolios.pdf)
  - Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert (2018), "The Impact of Volatility Targeting": 주식·크레딧 같은 위험자산에서는 Sharpe 개선, 전 자산군에서 꼬리 위험(극단 수익·최대 낙폭) 축소. 【원전·미재확인】 — [SSRN 3175538](https://papers.ssrn.com/abstract=3175538)
- 낙폭 관련(【원전·미재확인】): 낙폭 한도 하의 최적 전략은 "쿠션(자산 − 허용 바닥)에 비례한 노출" — [Grossman & Zhou (1993), Mathematical Finance 3(3)](https://doi.org/10.1111/j.1467-9965.1993.tb00044.x); 낙폭 형성보다 회복이 약 3배 오래 걸린다는 "triple penance rule"과 자기상관 하 스톱아웃 — [Bailey & López de Prado, SSRN 2201302](https://papers.ssrn.com/abstract=2201302)
- 파산 확률 기본식(【원전·미재확인】): 동일 금액 승패(±1 단위), 승률 p, 초기 자본 U 단위일 때 `P(ruin) = (q/p)^U` (p > q). — [Wikipedia: Gambler's ruin](https://en.wikipedia.org/wiki/Gambler%27s_ruin)
- 실무서(【원전·미재확인】): Carver (2015) *Systematic Trading* — 백테스트 Sharpe를 할인해 쓰고 half-Kelly 이하의 변동성 목표를 권고. — [Harriman House](https://harriman-house.com/systematictrading)

### Inferences
- 【자체 계산】 **Kelly를 본 전략에 넣어 보면**(b = 0.65/0.75 = 0.867; f = 손절 시 잃는 계좌 비율로 해석):

  | 참 승률 | 순 기대값/거래 | full Kelly f(위험 비율) | 필요한 포지션(계좌 대비) |
  |---|---|---|---|
  | 55% | +0.020% | 3.1% | 4.1배 |
  | 57% | +0.048% | 7.4% | 9.9배 |
  | 60% | +0.090% | 13.8% | 18.5배 |

  → 거래당 손익 폭이 ±0.7%로 작아서 **full Kelly는 레버리지 4~18배**를 요구한다. 현금·롱온리 계좌의 실제 제약은 "포지션 ≤ 계좌 100%"이고, 이 제약 하의 위험은 거래당 ≤ 0.75% 다. 즉 Kelly는 "과소 베팅 여부"가 아니라 **엣지가 없을 때의 손실 속도**를 통제하는 관점에서만 의미가 있다.
- 【자체 계산】 Baker–McHale형 근사 수축(내가 기억하는 근사식 `k* ≈ s*² / (s*² + ((b+1)/b)²·σ_p²)`, s* = Kelly 분수, σ_p² = 승률 추정 분산; **원문 대조 필요**)을 p̂ = 58%에 적용: n=50 → k ≈ 0.29, n=100 → 0.45, n=200 → 0.62, n=500 → 0.80. 즉 표본 100건 이하에서는 "quarter~half Kelly"가 오히려 자연스러운 결과.
- **더 보수적인 규칙(권장)**: 크기 산정에 쓰는 승률은 점추정이 아니라 **단측 95% 하한 또는 사후분포 5~25% 분위수**. 3절 표대로 n=200에서 p̂ < 59.4%면 하한이 p_BE 이하 → Kelly 하한 = 0 → "최소 단위(관찰용) 크기". 이것이 "엣지 추정이 불확실할 때 합리적인 것"에 대한 직접적인 답이다.
- 【자체 계산】 **고정 비율 위험과 낙폭**(독립 거래 가정 몬테카를로 4,000회, 500거래 내 고점 대비 −20% 낙폭 발생 확률):

  | 거래당 위험(계좌 %) | 참 승률 53.6%(엣지 없음) | 57% | 60% |
  |---|---|---|---|
  | 0.25% | ≈0% | ≈0% | ≈0% |
  | 0.5% | 6.4% | 0.15% | ≈0% |
  | 1.0% | 55.6% | 15.3% | 2.8% |
  | 2.0% | 97.7% | 83.6% | 55.7% |

  → 엣지가 사실은 없을 가능성을 진지하게 본다면 **거래당 0.25~0.5%** 가 합리적 범위. 같은 날 군집(상관)까지 고려하면 실제 낙폭 확률은 더 높다. 위험 0.5%·SL+비용 0.75%면 포지션 ≈ 계좌의 67%, 0.25%면 ≈ 33%.
- 일손실 한도(제안, 실무 관행에 근거하며 학술적 최적값은 아님): 일 −2R~−3R(R = 거래당 위험) 도달 시 당일 신규 진입 중단; 동시 보유 종목 수 상한(상관된 dip은 사실상 한 포지션); 주간 한도; 연속 손실 k회(무엣지 가정 하 확률 0.464^k: 5연패 ≈ 2.2%, 7연패 ≈ 0.46%) 후 쿨다운.
- 낙폭 기반 축소(제안): Grossman–Zhou 방식의 단순화 — 고점 대비 낙폭이 허용 한도 D의 50%에 도달하면 크기 1/2, 100%면 중단·재검증. triple penance 관점에서 "회복 기간은 낙폭 형성 기간보다 훨씬 길 수 있다"는 점을 재개 조건에 반영.
- 변동성 타기팅은 본 전략에서는 "포지션 = 목표 위험 ÷ (종목의 최근 분 단위 변동성 기반 예상 손절폭)" 형태의 **종목 간 위험 균등화** 용도로 충분하다. 손절폭이 고정 −0.5%면 종목 변동성이 클수록 잡음으로 손절될 확률이 올라가므로, 손절폭을 ATR 배수로 두고 수량을 조절하는 대안을 백테스트 후보로 둘 수 있다(이 또한 시도 횟수에 포함).

### Gaps
- Baker & McHale의 수축 계수 정확한 식은 본문 미열람(위 식은 기억 기반 근사, 검증 필요).
- MacLean–Thorp–Ziemba의 구체적 시뮬레이션 수치, Carver의 구체적 권고 수치(변동성 목표 %)는 원문 대조 못 함.
- 일손실 한도·연속손실 쿨다운의 최적 수준에 대한 학술 근거는 찾지 못함(관행적 수치).
- 시간청산·부분 체결이 섞인 실제 손익분포에서의 파산/낙폭 확률은 자체 거래 로그의 블록 부트스트랩으로 다시 계산해야 함.

---

## 9. 거래비용·체결 모델링(분봉): 스프레드/틱 · 주문 유형별 체결 · 슬리피지 · implementation shortfall · 비용 모델 보정

### Takeaway
이 전략의 손익은 비용 가정에 극도로 민감하다(비용 0.05%p ≈ 손익분기 승률 3.6%p). 2026년 한국 주식 매도 시 거래세는 KOSPI·KOSDAQ 모두 실질 0.20%이고 국내 상장 ETF는 거래세가 면제되므로, 같은 TP/SL이라도 ETF의 손익분기 승률이 훨씬 낮다. 분봉 백테스트의 지정가 "닿으면 체결" 가정은 낙관적이며, 페이퍼/실거래 체결 로그로 implementation shortfall을 재서 비용 모델을 주기적으로 재보정해야 한다.

### Cited Findings
- **한국 거래세(2026)**: KOSPI는 증권거래세 0.05% + 농어촌특별세 0.15% = 실질 0.20%, KOSDAQ·K-OTC는 단일 0.20%(농특세 없음). 금투세 도입을 전제로 인하했던 세율이 금투세 폐지로 2023년 수준으로 환원. 매도 시에만 과세되며 수수료가 무료여도 면제되지 않음. 일부 자료는 2026년 세율을 0.15%로 적고 있어 상충하나 최신 보도 기준은 0.20%. 【검색확인】 — [세계일보 2026-01-05](https://www.segye.com/newsView/20260105516769); [studygov 정리](https://studygov.kr/blog/0337-2026-stock-transaction-tax/); [더팩트 "'단타족' 울린 증권거래세 부활"](https://news.tf.co.kr/read/economy/2278747.htm)
- **ETF**: 한국거래소 상장 ETF는 세법상 신탁형 펀드에 해당해 매도 시 증권거래세를 내지 않는다. 단, 국내주식형이 아닌 "기타 ETF"(해외지수·채권·원자재·레버리지·인버스·액티브 등)는 매매차익이 보유기간과세 방식으로 배당소득세 15.4% 과세. 【검색확인(증권사·운용사 2차 자료, 법령 조문 직접 확인은 아님)】 — [토스피드 "ETF 세금의 모든 것"](https://toss.im/tossfeed/article/etf-and-tax); [KB자산운용](https://kbam.co.kr/insights/guide/etf-tax-guide-domestic-vs-other-types); [KB Think](https://www.kbthink.com/main/guide/etf-tax.html)
- **체결 모델**:
  - 백테스트 체결 가정 3종 비교(모든 대기 주문 체결 / 지수분포 체결 시간 / Bernoulli 비율로 역선택 체결 추가): "대기 주문은 처음 도착하는 시장가 주문에 항상 체결된다"가 가장 낙관적 가정이며, 실거래 시뮬레이션을 기준선으로 보정. 【검색확인】 — [arXiv 2407.16527](https://arxiv.org/pdf/2407.16527)
  - 체결 확률과 역선택 체결은 성과에 유의한 영향을 주며 현실적 체결 확률이 전략 성과를 더 정확히 보여 준다. 【검색확인】 — [Lalor & Swishchuk, arXiv 2409.12721](https://arxiv.org/abs/2409.12721v2)
  - 체결 확률은 큐 내 위치, 해당 가격의 유동성 깊이, 들어오는 시장가 주문의 빈도·크기에 좌우; 체결 확률이 높은 메이커 주문일수록 체결 후 수익이 나쁘다. 【검색확인】 — [arXiv 2502.18625](https://arxiv.org/pdf/2502.18625v2)
  - 체결 불확실성과 역선택을 무시하면 결과가 실거래 대비 부풀려진다; 공격적 지정가의 실패 확률 모형과 시장가의 체결가 모형 제안. 【검색확인】 — [Oxford ORA 논문](https://ora.ox.ac.uk/objects/uuid:cdab1de2-7576-42e2-abae-ab12371eba76/files/rs4655j600)
  - 큐 위치 모델링과 "실거래 주문 제출·큐 추정·체결 시각을 로깅해 실거래 vs 백테스트 체결률 비교" 권고. 【검색확인】 — [hftbacktest 문서: queue position](https://www.mintlify.com/nkaz001/hftbacktest/concepts/queue-position)
- **Implementation shortfall**(【원전·미재확인】): "종이 포트폴리오(결정 시점 가격으로 즉시 전량 체결 가정) 수익 − 실제 포트폴리오 수익" = 실행 비용 + 미체결 기회비용. — [Perold (1988), JPM 14(3)](https://doi.org/10.3905/jpm.1988.409150)
- **Almgren–Chriss**(【원전·미재확인】): 큰 주문을 쪼갤 때 시장충격 비용과 타이밍 위험의 trade-off 최적화. — [Almgren & Chriss (2000), Journal of Risk](https://doi.org/10.21314/JOR.2001.041)
- **호가 없이 스프레드 추정**(【원전·미재확인】): Roll (1984) `spread = 2·√(−Cov(Δp_t, Δp_{t−1}))` — [Journal of Finance 39(4)](https://doi.org/10.1111/j.1540-6261.1984.tb03897.x); 고가·저가 기반 추정량 — [Corwin & Schultz (2012), Journal of Finance 67(2)](https://doi.org/10.1111/j.1540-6261.2012.01729.x)
- RL·백테스트 문헌 공통 지적: 비용을 고정값으로 단순화하고 체결을 확실하다고 가정하면 변동하는 스프레드 같은 현실을 놓친다. 【검색확인】 — [arXiv 2408.10932](https://arxiv.org/pdf/2408.10932)

### Inferences
- 【자체 계산】 **주식 vs ETF 손익분기**(TP 0.9 / SL 0.5 고정): 주식 왕복비용 = 거래세 0.20% + 수수료(무료~0.03%) + 스프레드·슬리피지(0.03~0.10%) ≈ 0.25~0.33% → p_BE 53.6~59%. 국내주식형 ETF 왕복비용 = 수수료 + 스프레드·슬리피지 ≈ 0.03~0.10% → p_BE 38~43%. **같은 탐지 규칙이라면 유동성 높은 ETF 쪽이 통계적으로 훨씬 유리한 출발점**(단 ETF는 변동성이 낮아 +0.9% TP 도달 빈도가 낮을 수 있고, 레버리지·인버스 ETF는 매매차익 과세가 별도 — 세후 기준으로 다시 계산해야 함).
- 소액 리테일 주문에서는 시장충격(Almgren–Chriss의 대상)은 무시 가능하고 **스프레드·틱·지연·세금**이 비용의 전부다. 주문 크기가 최우선 호가 잔량의 일정 비율(예: 10%)을 넘지 않도록 하는 것으로 충분.
- **주문 유형별 모델(제안)**
  - 시장가: 체결 확실, 비용 = 반 스프레드 + 지연 중 가격 이동. 반등 포착(가격이 유리하게 움직이기 시작한 순간 진입)에서는 지연 슬리피지가 구조적으로 불리한 방향.
  - Marketable limit(최우선 매도호가 또는 +1틱 지정가): 슬리피지 상한을 고정하는 대신 미체결 위험. **진입 기본값으로 권장**(미체결은 "기회 상실"로 로깅).
  - Passive limit(매수호가에 대기): 스프레드를 벌지만 "잘 체결되는 주문일수록 역선택" — dip 매수에서는 가격이 더 떨어지는 경우에만 체결되고 바로 반등하는 경우에는 놓친다. 백테스트에서는 **가격이 지정가를 1틱 이상 관통한 봉에서만 체결**로 처리하고, 체결된 거래의 사후 수익이 미체결 가정 거래보다 나쁜지(역선택)를 페이퍼 로그로 측정.
  - TP는 지정가(유리), SL은 시장가/스톱(불리한 슬리피지 +α)로 **비대칭 슬리피지**를 넣는다: 유효 W = 0.9 − 비용, 유효 L = 0.5 + 비용 + SL 슬리피지.
- **슬리피지 함수형(보정 대상 모델, 제안)**: `slip_i = a·(spread_i/2) + b·σ_1m,i·√(지연초/60) + c·(주문금액/최우선잔량금액) + ε`. 페이퍼/실거래 체결마다 (결정 시각 중간가, 주문 전송 시각, 체결가, 스프레드, 1분 변동성, 잔량)을 저장하고 주기적으로 a, b, c를 회귀로 갱신. 변동성이 큰 순간(바로 신호가 나오는 순간)에 스프레드와 슬리피지가 함께 커지므로 **평균 비용이 아니라 신호 시점 조건부 비용**을 써야 한다.
- **Implementation shortfall 로깅**: 거래별 IS = (실제 체결가 − 신호 시점 기준가)/기준가 를 진입·청산 각각 기록 + 미체결 신호의 가상 손익(기회비용). 백테스트 가정 비용 대비 실측 IS의 평균·분포가 게이트 항목(10절)이 된다.
- 페이퍼 트레이딩 체결이 "마지막 체결가로 즉시 전량 체결"이라면 실거래보다 낙관적이다. 페이퍼 단계에서도 매수는 매도호가(+지연 보정), 매도는 매수호가로 체결시키는 보수 모드를 기본으로 하고, 두 모드의 차이를 민감도로 보고.
- 분봉 OHLC만 있고 호가 이력이 없는 과거 구간은 Roll/Corwin–Schultz 추정치와 틱 크기 하한 중 큰 값을 스프레드로 사용.
- 비용 민감도(±0.05%p, ±0.10%p)에서 기대값 부호가 뒤집히면 승격 금지 — "비용 스트레스 테스트"를 게이트에 포함.

### Gaps
- KRX 호가가격단위(틱) 표는 이번 세션에서 검색 예산 소진으로 확인하지 못함. 내 기억으로는 2023년 개편 후 주식은 2,000원 미만 1원 / 2,000~5,000원 5원 / 5,000~20,000원 10원 / 20,000~50,000원 50원 / 50,000~200,000원 100원 / 200,000~500,000원 500원 / 500,000원 이상 1,000원, ETF는 5원(저가 ETF 1원)이나 **미검증**. 맞다면 틱/가격 비율이 구간 하단에서 0.2~0.25%(예: 50,000원 종목의 100원)까지 커져 TP 0.9%·SL 0.5% 대비 매우 크므로, 종목 선정에 "틱/가격 ≤ 0.1%" 같은 필터가 필요할 수 있음 — KRX 규정으로 확인 필요.
- 증권거래세법·소득세법 조문 직접 확인은 하지 않음(2차 자료 기준). Toss증권의 2026년 수수료·유관기관 수수료 체계는 본 노트 범위에서 확인하지 않음.
- 한국 주식 분 단위 실측 슬리피지(지연 대비) 공개 통계는 찾지 못함.
- 대체거래소(넥스트레이드) 병행 체결이 스프레드·체결에 주는 영향은 조사하지 않음.

---

## 10. 성과 측정과 감쇠 모니터링: 기대값·profit factor·Sharpe/Sortino(거래/일 단위)·MDD 분포·백테스트 대비 추적·폐기 규칙

### Takeaway
백테스트 Sharpe는 실전 성과를 거의 예측하지 못하고(R² 1~2%), 발표된 전략도 평균적으로 Sharpe가 절반가량 감쇠한다. 따라서 "기대 성과"는 할인해서 잡고, 실현 성과가 백테스트 부트스트랩 분포의 어느 분위에 있는지와 CUSUM 경보, 체결비용 추적오차를 사전에 정한 폐기 규칙으로 묶어 두어야 한다.

### Cited Findings
- Quantopian 연구: IS Sharpe 등은 OOS의 1~2%만 설명, 연수익은 OOS와 약한 음의 상관, 변동성·낙폭 지표가 더 예측적. 논문은 백테스트 과최적화를 틀로 삼으며 백테스트 지표가 OOS 예측에 거의 가치가 없다고 요약됨. 【검색확인】 — [SSRN 2745220](https://papers.ssrn.com/abstract=2745220); [CXO Advisory](https://www.cxoadvisory.com/big-ideas/in-sample-vs-out-of-sample-performance-of-888-trading-strategies)
- 발표 후 감쇠: McLean & Pontiff (2016, JF) — 97개 예측 변수; 초기 초안은 통계적 편향에 의한 OOS 감쇠 약 10%, 발표 효과 하한 약 32%로 보고(최종본 수치로 흔히 인용되는 "OOS −26%, 발표 후 −58%"는 이번 검색에서 재확인 실패). 【검색확인(부분)】 — [JF DOI 10.1111/jofi.12365](https://doi.org/10.1111/jofi.12365); [CFA Digest](https://rpc.cfainstitute.org/research/cfa-digest/2016/06/does-academic-research-destroy-stock-return-predictability-digest-summary)
- Falck, Rej & Thesmar: 72개 전략의 Sharpe가 발표 후 약 절반으로 감쇠. 【검색확인】 — [arXiv 2105.01380](https://arxiv.org/pdf/2105.01380)
- Sharpe의 통계적 취급(PSR/MinTRL/DSR; Lo 2002)은 1절 참조. — [SSRN 5520741](https://papers.ssrn.com/abstract=5520741); [Lo (2002)](https://doi.org/10.2469/faj.v58.n4.2453)
- 낙폭 회복의 비대칭(triple penance), 자기상관이 있으면 낙폭이 더 깊어짐. 【원전·미재확인】 — [SSRN 2201302](https://papers.ssrn.com/abstract=2201302)
- 대안 베타 215개 전략에서 백테스트→실거래 Sharpe 중앙값 감쇠가 매우 컸다는 실증(통상 −73%로 인용). 【원전·미재확인】 — [Suhonen, Lennkh & Perez (2017), JPM 43(2)](https://doi.org/10.3905/jpm.2017.43.2.090)
- 구현 참고: quantstats(성과 지표·티어시트), pypbo(PBO·DSR 계산). — [quantstats GitHub](https://github.com/ranaroussi/quantstats); [pypbo GitHub](https://github.com/esvhd/pypbo)

### Inferences
- **지표 정의와 본 전략 수치(자체 계산)**
  - 기대값(expectancy) `E = p·W − (1−p)·L`; R-multiple로는 E/L.
  - Profit factor `PF = p·W / ((1−p)·L)`: p=53.6% → 1.00, 57% → 1.15, 60% → 1.30, 65% → 1.61. PF는 소표본에서 분모가 작아 불안정하므로 부트스트랩 구간과 함께 보고.
  - 거래당 Sharpe `SR_trade = E/σ_trade`; 연율화는 독립 가정 시 `SR_trade·√(연간 거래 수)`. 예: 승률 57%(SR_trade ≈ 0.07), 연 1,000거래 → 연율 ≈ 2.2. 그러나 같은 날 군집 때문에 **일 단위 손익으로 계산한 Sharpe(×√252)** 가 더 정직하다 — 두 값을 병기하고 차이가 크면 일중 상관이 크다는 신호.
  - Sortino = 평균/하방편차: SL로 하방이 잘려 있는 전략에서는 Sharpe보다 좋게 보이므로 보조지표로만.
- **MDD 분포**: 과거 한 경로의 MDD는 표본 1개다. 거래일 블록 부트스트랩(stationary bootstrap)으로 1만 경로를 만들어 MDD의 중앙값·95%·99% 분위수를 보고하고, 실거래 낙폭 한도는 95% 분위수 근처에 둔다. 8절 표가 보여 주듯 크기 0.5% 위험에서도 "엣지 없음" 시나리오의 낙폭 꼬리가 의미 있게 존재.
- **실현 vs 기대 추적(제안 지표)**
  1. 체결 추적오차: 같은 신호에 대해 백테스트 체결가 vs 페이퍼/실체결가의 차이(bp)의 평균·표준편차·분위수 — 평균이 가정 슬리피지를 넘으면 비용 모델 재보정.
  2. 신호 일치율: 실시간 탐지 신호와 사후 백테스트 재생 신호의 일치 비율(데이터 지연·봉 확정 시점 차이 탐지). 95% 미만이면 코드/데이터 문제.
  3. 성과 분위수: 최근 N거래 누적 손익이 백테스트 부트스트랩 분포의 몇 분위수인지. 5% 미만 지속 시 경보.
  4. 하방 CUSUM(7절) + 승률의 Beta 사후확률 P(p > p_BE).
  5. 메타 모델 보정 드리프트: 예측 확률 버킷별 실현 승률.
- **기대치 할인**: 승격 문서에 "백테스트 기대값의 50%만 실현된다고 가정해도 비용 후 양(+)인가"를 명시(Falck et al.의 '절반 감쇠'와 Quantopian 결과를 근거로 한 보수적 기획 가정).
- **폐기/중단 규칙 초안**(사전 등록): (a) 페이퍼/실거래 누적 n ≥ 100에서 P(p > p_BE) < 10% → 폐기 후보, (b) 낙폭이 부트스트랩 MDD 99% 분위수 초과 → 즉시 중단, (c) CUSUM 경보 2회 연속(재검증 후에도) → 폐기, (d) 실측 왕복비용이 가정보다 0.05%p 이상 높고 재계산 기대값 ≤ 0 → 중단, (e) 최대 표본(예: 500거래)까지 통과 기준 미달 → 무익성 중단. 폐기된 변형도 시도 횟수 N에 영구 계상.
- 보고 주기: 거래 단위 지표는 매일, 통계적 판정(게이트)은 사전 정한 체크포인트(예: 50거래마다) 또는 anytime-valid 방식으로만 — 임의 시점 재검정은 3절의 "엿보기" 문제.

### Gaps
- McLean–Pontiff 최종본의 정확한 수치(−26%/−58%)와 Suhonen et al.의 −73%는 이번 세션에서 원문 재확인 실패.
- Quantopian 논문의 "백테스트를 많이 돌릴수록 IS–OOS 격차가 커진다"는 결과는 기억하고 있으나 이번 검색 스니펫으로는 직접 확인하지 못함.
- 리테일 분봉 전략의 실거래 감쇠율에 대한 체계적 공개 통계는 찾지 못함.
- quantstats·pypbo의 현재 유지보수 상태(2026)는 확인하지 않음.

---

## 11. 근거 있는 레짐 필터: 시장 추세/변동성 · 매크로·실적 이벤트 회피 · 시장 전체 급락 vs 종목 고유 하락

### Takeaway
"변동성이 높을 때 반전(유동성 공급) 수익이 크다"는 것은 실증되어 있지만 같은 시기에 위험과 비용도 커지므로, 고변동 레짐은 "진입 허용 + 크기 축소"가 합리적이다. "뉴스 없는 종목 고유 하락이 더 잘 반등한다"는 방향의 근거가 있고, 시장 전체 급락일·이벤트일 회피는 논리적으로 타당하나 장중 단일 종목 수준의 직접 증거는 부족해 자체 데이터로 검증할 가설로 취급해야 한다.

### Cited Findings
- 고변동성 레짐: VIX가 이후 단기 반전 전략 수익을 예측하고, 금융 불안기에 기대수익·조건부 Sharpe가 급등 — 유동성 공급자의 철수(유동성 증발)가 원인. 【검색확인】 — [Nagel (2012), NBER w17653](https://www.nber.org/papers/W17653)
- 변동성 타기팅은 위험자산의 꼬리 위험을 줄이나(Harvey et al. 2018), 변동성 관리의 실시간 우월성은 논쟁 중(Cederburg et al. 2020; DeMiguel et al. 2024). 【검색확인(후자)】 — [SSRN 3175538](https://papers.ssrn.com/abstract=3175538); [Cederburg et al. PDF](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
- 한국 개인의 데이 트레이딩: 회전율이 높을수록 손실이 큰 경향(NH투자증권 2022년 계좌 분석: 국내 주식 평균 −25.4% vs KOSPI −24.9%), 자본시장연구원 보고서(2020–2022, 102,380명)에서는 회전율이 가장 낮은 고액 투자자군만 양(+)의 수익(2차 기사 기준). 【검색확인(2차 기사)】 — [다음/코리아중앙데일리 2023-01-12](https://v.daum.net/v/20230112122100856); [아시아경제 2023-02-06](https://cm.asiae.co.kr/en/article/2023020616195058910)
- 뉴스성 하락 vs 무뉴스 하락, 종목 고유(산업 조정) 반전의 우위(【원전·미재확인】) — [Tetlock (2010)](https://doi.org/10.1093/rfs/hhq052); [Da, Liu & Schaumburg (2014)](https://doi.org/10.1287/mnsc.2013.1766)
- 예정된 매크로 발표일의 특수성(【원전·미재확인】): 발표일에 시장 위험프리미엄이 집중 — [Savor & Wilson (2013), JFQA 48(2)](https://doi.org/10.1017/S002210901300015X); FOMC 직전 24시간의 주가 상승 드리프트 — [Lucca & Moench (2015), Journal of Finance 70(1)](https://doi.org/10.1111/jofi.12196)
- 일중 시장 모멘텀(첫 30분 → 마지막 30분)은 "추세일"에 dip 매수가 불리할 수 있음을 시사(【원전·미재확인】) — [Gao, Han, Li & Zhou (2018)](https://doi.org/10.1016/j.jfineco.2018.05.009)

### Inferences
- **필터 후보와 처리 방식(제안)** — 필터는 on/off 스위치보다 **메타 모델의 특징 또는 크기 배수**로 넣는 편이 표본을 덜 버린다. 각 필터는 "시도" 1회로 계상.

  | 레짐/이벤트 | 조작적 정의 예 | 권장 처리 | 근거 수준 |
  |---|---|---|---|
  | 시장 전체 급락(동반 하락) | 신호 시각 KOSPI200(또는 KODEX 200) 당일 수익 ≤ −1% 또는 최근 15분 하락 속도 상위 5% | 진입 보류 또는 크기 1/2; 종목 잔차 하락이 클 때만 허용 | 간접(Da et al.; Nagel) |
  | 종목 고유 dip | 종목 수익 − β×시장 수익의 z-score ≤ −2, 시장은 ±0.3% 이내 | 기본 진입 대상 | 간접(잔차 반전) |
  | 고변동성 | VKOSPI 또는 20일 실현변동성 상위 분위 | 진입 허용, 크기 축소, 비용 가정 상향 | Nagel(수익↑), 9절(비용↑) |
  | 뉴스/공시 | 당일 해당 종목 공시·실적 발표·거래정지 해제 | 제외(정보성 하락) | Tetlock(간접) |
  | 매크로 이벤트일 | 금통위, 옵션·선물 동시만기일, 미국 CPI/FOMC 직후 개장일 | 개장 초 구간 제외 또는 크기 축소 | 미국 일간 증거의 유추 |
  | 추세일 | 개장 30분 수익과 현재까지 수익의 부호·크기가 강한 하락 추세 | dip 매수 보류 | Gao et al.(간접) |
  | 시간대 | 개장 직후 5~10분, 마감 동시호가 직전 | 제외(스프레드·변동성 과대, 시간청산 불가) | 실무 통념 |

- ETF(지수형) 자체를 거래할 때 "시장 급락 vs 종목 고유"의 구분이 사라지므로(ETF의 dip = 시장의 dip), ETF에는 잔차 기반 논리가 적용되지 않는다 — ETF용과 개별주용 규칙·통계를 **분리 집계**해야 한다(계층 모델에서 자산 유형을 그룹 변수로).
- 필터가 거래 수를 30% 줄이면 같은 기간에 모이는 표본도 30% 줄어 3절의 판정 시점이 늦어진다. "필터 적용 후 총 기대이익"과 "판정까지 걸리는 기간" 둘 다 보고.
- 레짐별 성과를 사후에 쪼개 보는 것은 가장 흔한 과최적화 경로다. 레짐 정의는 거래 로그를 보기 전에 고정하고, 사후 분할 분석은 "가설 생성"으로만 표기.

### Gaps
- 한국 시장에서 장중 dip 매수의 레짐별(시장 급락일·이벤트일) 성과를 다룬 직접 실증은 찾지 못함.
- VKOSPI와 한국 단기 반전 수익의 관계(Nagel 결과의 한국판)는 확인하지 못함.
- 이동평균 추세 필터(예: 지수 20일선 위에서만 매수)의 장중 평균회귀 전략에 대한 효과는 신뢰할 만한 근거를 찾지 못함(월간 자산배분 맥락의 근거만 존재).
- 자본시장연구원 원보고서는 직접 열람하지 못함(기사 인용).
- Savor–Wilson, Lucca–Moench, Tetlock, Da et al., Gao et al.은 이번 세션에서 초록 재확인 못 함.
