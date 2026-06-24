# Puddle Trader CLI

토스증권 Open API 기반 **웅덩이 단타 보조 시스템**. 관심종목을 순회 감시하며 급락 후 저점이
잡히는 "웅덩이" 구간을 탐지하고, **가상매매 로그 · AI 점수화 · 마크다운 리포트**를 축적해
다음 매매 판단에 반영한다.

> ⚠️ 이 프로그램은 "AI가 알아서 매수/매도하는 자동 수익 봇"이 아니다. 기본 모드는 **무조건
> paper(가상매매)** 이며, 실주문은 충분한 검증 이후 반자동(manual)부터 단계적으로 확장한다.

전체 제품 정의는 [`docs/PRD.md`](docs/PRD.md), API 검증 결과는 [`docs/API_NOTES.md`](docs/API_NOTES.md) 참고.

## 설치

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .          # ML 기능까지: pip install -e ".[ml,dev]"
```

## 자격 증명 설정

API 키/시크릿은 코드·저장소에 절대 넣지 않는다. `.env` 로만 관리한다.

```bash
cp .env.example .env
# .env 를 열어 TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 입력
```

## 사용

```bash
tradebot init                       # 디렉토리 + SQLite DB 생성
tradebot auth test                  # 토큰 발급/계좌 조회 확인
tradebot favorites add KR:000660 --name "SK하이닉스"
tradebot favorites list
tradebot watch --mode paper --interval 10s   # (탐지/가상매매는 후속 구현)
```

## 구조

```
config/        favorites / strategy / risk / app  설정(YAML)
src/puddle_trader/
  api/         토스 API 클라이언트(토큰 캐싱·429 백오프) + 엔드포인트 래퍼
  candles.py   1분봉 → 3m/5m 합성 (API 가 1m/1d 만 주므로)
  db/          SQLite 스키마 + 연결
  cli.py       tradebot 명령
docs/          PRD, API 검증 노트
```

## 개발 로드맵 (PRD §17)
- **v0.1** CLI 가상매매: 인증 · 관심종목 · 시세 수집 · 웅덩이 탐지 · paper trade · 일일 리포트
- **v0.2** AI 점수화/학습  ·  **v0.3** 반자동 주문  ·  **v0.4** 자동 익절/손절  ·  **v0.5** 제한적 자동진입
