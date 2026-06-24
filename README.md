# Toss Invest OpenAPI 문서 정리 도구

`split_openapi.py`는 Toss Invest OpenAPI 스펙(`openapi.json`)을 받아서
엔드포인트별 / 스키마별 JSON 파일로 분리하고, 요약 문서(`summary.md`)를 생성합니다.

## 사용법

### 1) 로컬 스펙 파일로 생성 (권장)

원격 실행 환경에서는 `openapi.tossinvest.com`이 네트워크 정책으로 차단될 수 있습니다.
이 경우 스펙 파일을 직접 받아 `--input`으로 전달하세요.

```bash
python3 split_openapi.py --input openapi.json --out toss_openapi_docs
```

### 2) URL로 직접 다운로드

네트워크에서 해당 호스트가 허용된 환경에서만 동작합니다.

```bash
python3 split_openapi.py \
  --url https://openapi.tossinvest.com/openapi-docs/latest/openapi.json \
  --out toss_openapi_docs
```

## 옵션

| 옵션 | 설명 | 기본값 |
| --- | --- | --- |
| `--input` | 로컬 `openapi.json` 경로 | 없음 |
| `--url` | OpenAPI JSON URL | 없음 |
| `--out` | 출력 폴더 | `toss_openapi_docs` |

`--input` 또는 `--url` 중 하나는 반드시 지정해야 합니다.

## 출력 구조

```
toss_openapi_docs/
├── openapi.json              # 원본 스펙 전체
├── summary.md                # 버전/엔드포인트/스키마 요약
├── endpoints/
│   └── <Tag>/
│       └── <method>__<operationId>.json
└── schemas/
    └── <SchemaName>.json
```

- `endpoints/<Tag>/...` : 태그(첫 번째 태그) 기준으로 분류된 개별 엔드포인트.
  각 파일에는 path, method, operationId, parameters, requestBody, responses,
  security와 원본(`raw`)이 포함됩니다.
- `schemas/<SchemaName>.json` : `components.schemas`의 각 스키마.
- `summary.md` : OpenAPI 버전, 타이틀, 엔드포인트/스키마 개수 및 전체 엔드포인트 목록.

## 참고

원격 환경에서 다운로드가 `403 Forbidden`(egress 정책 거부)으로 실패하는 경우,
환경의 네트워크 정책에서 `openapi.tossinvest.com`을 허용 목록에 추가하거나,
스펙 파일을 로컬로 받아 `--input`으로 실행하세요.
