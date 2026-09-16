"""Terminal entry point for scripted demos and evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.assistant import SAPTicketAssistant


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Triagem de chamados SAP S/4HANA MM")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--case", help="ID de data/chamados.json, por exemplo CH-01")
    source.add_argument("--text", help="Texto livre do chamado")
    args = parser.parse_args()

    if args.case:
        cases = json.loads((ROOT / "data/chamados.json").read_text(encoding="utf-8"))
        case = next((item for item in cases if item["id"] == args.case.upper()), None)
        if case is None:
            parser.error(f"Caso {args.case} não encontrado")
        ticket = case["texto"]
    else:
        ticket = args.text

    assistant = SAPTicketAssistant.from_env(ROOT / "knowledge", ROOT / "logs/requests.jsonl")
    result = assistant.answer(ticket)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "error" else 2


if __name__ == "__main__":
    sys.exit(main())
