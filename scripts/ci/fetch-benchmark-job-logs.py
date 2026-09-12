#!/usr/bin/env python3
"""Download completed sample job logs for the current GitHub Actions run."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request


def request(url: str, token: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rubydex-labs-benchmark",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    jobs_url = (
        f"https://api.github.com/repos/{args.repository}/actions/runs/"
        f"{args.run_id}/jobs?filter=latest&per_page=100"
    )
    jobs = json.loads(request(jobs_url, token))["jobs"]
    sample_jobs = [job for job in jobs if job.get("name", "").startswith("sample-")]

    if not sample_jobs:
        raise SystemExit("No completed sample-* jobs found in this workflow run")

    failures: list[str] = []
    for job in sample_jobs:
        name = job["name"]
        job_id = job["id"]
        logs_url = f"https://api.github.com/repos/{args.repository}/actions/jobs/{job_id}/logs"
        data: bytes | None = None
        last_error: Exception | None = None

        # GitHub can need a few seconds after a job completes before its log
        # archive/text endpoint becomes available to a downstream job.
        for attempt in range(6):
            try:
                data = request(logs_url, token)
                break
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in (404, 409):
                    break
                time.sleep(2 + attempt)
            except Exception as exc:  # pragma: no cover - network fallback
                last_error = exc
                time.sleep(2 + attempt)

        if data is None:
            failures.append(f"{name}: {last_error}")
            continue

        (output / f"{name}.log").write_bytes(data)

    manifest = {
        "run_id": args.run_id,
        "repository": args.repository,
        "jobs": [
            {
                "name": job["name"],
                "id": job["id"],
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
            }
            for job in sample_jobs
        ],
        "failures": failures,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    if failures:
        print("Warning: some sample logs could not be downloaded:")
        for failure in failures:
            print(f"  {failure}")

    print(f"Downloaded {len(sample_jobs) - len(failures)}/{len(sample_jobs)} sample logs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
