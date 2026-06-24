import argparse
import json
import re
from pathlib import Path
from urllib.request import urlopen

DEFAULT_URL = "https://openapi.tossinvest.com/openapi-docs/latest/openapi.json"

def safe_name(text: str) -> str:
    text = text.strip("/").replace("/", "__")
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"[^a-zA-Z0-9._-]+", "_", text)
    return text or "root"

def load_spec(input_path: str | None, url: str | None) -> dict:
    if input_path:
        return json.loads(Path(input_path).read_text(encoding="utf-8"))

    if url:
        with urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))

    raise ValueError("input_path 또는 url 중 하나가 필요합니다.")

def split_openapi(spec: dict, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "endpoints").mkdir(exist_ok=True)
    (out_dir / "schemas").mkdir(exist_ok=True)

    (out_dir / "openapi.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    paths = spec.get("paths", {})
    schemas = spec.get("components", {}).get("schemas", {})

    for path, methods in paths.items():
        for method, detail in methods.items():
            operation_id = detail.get("operationId")
            tags = detail.get("tags") or ["uncategorized"]
            tag = safe_name(tags[0])

            tag_dir = out_dir / "endpoints" / tag
            tag_dir.mkdir(parents=True, exist_ok=True)

            file_name = f"{method.lower()}__{safe_name(operation_id or path)}.json"
            file_path = tag_dir / file_name

            payload = {
                "path": path,
                "method": method.upper(),
                "operationId": operation_id,
                "tags": tags,
                "summary": detail.get("summary"),
                "description": detail.get("description"),
                "parameters": detail.get("parameters", []),
                "requestBody": detail.get("requestBody"),
                "responses": detail.get("responses", {}),
                "security": detail.get("security"),
                "raw": detail,
            }

            file_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    for schema_name, schema in schemas.items():
        file_path = out_dir / "schemas" / f"{safe_name(schema_name)}.json"
        file_path.write_text(
            json.dumps(schema, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    summary_lines = [
        "# Toss Invest OpenAPI Docs Snapshot",
        "",
        f"- OpenAPI version: {spec.get('openapi')}",
        f"- Title: {spec.get('info', {}).get('title')}",
        f"- Version: {spec.get('info', {}).get('version')}",
        f"- Endpoint count: {len(paths)}",
        f"- Schema count: {len(schemas)}",
        "",
        "## Endpoint list",
        "",
    ]

    for path, methods in paths.items():
        for method, detail in methods.items():
            summary_lines.append(
                f"- `{method.upper()} {path}` — {detail.get('summary') or detail.get('operationId') or ''}"
            )

    (out_dir / "summary.md").write_text(
        "\n".join(summary_lines),
        encoding="utf-8"
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="로컬 openapi.json 경로")
    parser.add_argument("--url", help="OpenAPI JSON URL")
    parser.add_argument("--out", default="toss_openapi_docs", help="출력 폴더")
    args = parser.parse_args()

    spec = load_spec(args.input, args.url)
    split_openapi(spec, Path(args.out))

    print(f"[DONE] Saved to {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()
