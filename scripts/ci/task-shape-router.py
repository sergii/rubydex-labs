#!/usr/bin/env python3
"""Lab 09 oracle task-shape router.

This intentionally routes from the benchmark's controlled scenario label rather
than asking an LLM to classify the prompt. It measures the upper bound of
correct task-shape routing; prompt classification is a separate experiment.
"""
from __future__ import annotations

import argparse
import json

ROUTES = {
    "declaration": "source",
    "descendants": "semantic",
    "references": "semantic",
    "neighborhood": "semantic",
    "impact": "semantic",
}


def route(scenario: str) -> str:
    try:
        return ROUTES[scenario]
    except KeyError as exc:
        raise ValueError(f"unknown scenario: {scenario}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=sorted(ROUTES))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    selected = route(args.scenario)
    if args.json:
        print(json.dumps({"scenario": args.scenario, "route": selected}))
    else:
        print(selected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
