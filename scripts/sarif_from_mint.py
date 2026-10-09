#!/usr/bin/env python3
"""Map Mint JSON diagnostics to SARIF 2.1.0. Not a compiler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def empty_log() -> dict[str, Any]:
    return {
        "$schema": SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "results": [],
                "tool": {
                    "driver": {
                        "informationUri": "https://github.com/opsdevcode/specmint-language",
                        "name": "mint",
                        "rules": [],
                    }
                },
            }
        ],
    }


def from_diagnostic(payload: dict[str, Any]) -> dict[str, Any]:
    log = empty_log()
    code = str(payload.get("code") or "MINT")
    message = str(payload.get("message") or "mint failed")
    unit = str(payload.get("unit") or "stdin")
    log["runs"][0]["tool"]["driver"]["rules"] = [
        {"id": code, "shortDescription": {"text": code}}
    ]
    location: dict[str, Any] = {
        "physicalLocation": {"artifactLocation": {"uri": Path(unit).name}}
    }
    span = payload.get("range")
    if isinstance(span, dict):
        start = span.get("start") or {}
        end = span.get("end") or {}
        region: dict[str, Any] = {}
        if start.get("line") is not None:
            region["startLine"] = start["line"]
        if start.get("column") is not None:
            region["startColumn"] = start["column"]
        if end.get("line") is not None:
            region["endLine"] = end["line"]
        if end.get("column") is not None:
            region["endColumn"] = end["column"]
        if region:
            location["physicalLocation"]["region"] = region
    log["runs"][0]["results"] = [
        {
            "level": "error",
            "locations": [location],
            "message": {"text": message},
            "ruleId": code,
        }
    ]
    return log


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exit-code", type=int, required=True)
    parser.add_argument("--stderr", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    text = args.stderr.read_text(encoding="utf-8") if args.stderr.is_file() else ""
    log = empty_log()
    if args.exit_code != 0 and text.strip().startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict) and payload.get("ok") is False:
            log = from_diagnostic(payload)
    args.output.write_text(json.dumps(log, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
