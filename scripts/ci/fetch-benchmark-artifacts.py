#!/usr/bin/env python3
"""Download sample artifacts from a completed benchmark workflow run."""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import urllib.request
import zipfile


def request(url: str, token: str, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rubydex-labs-benchmark",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
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

    url = (
        f"https://api.github.com/repos/{args.repository}/actions/runs/"
        f"{args.run_id}/artifacts?per_page=100"
    )
    artifacts = json.loads(request(url, token)).get("artifacts", [])
    samples = [a for a in artifacts if a.get("name", "").startswith("sample-")]
    if not samples:
        raise SystemExit("No sample-* artifacts found for source workflow run")

    manifest = []
    for artifact in samples:
        name = artifact["name"]
        download_url = artifact["archive_download_url"]
        data = request(download_url, token, "application/octet-stream")
        target = output / name
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            archive.extractall(target)
        manifest.append(
            {
                "name": name,
                "id": artifact["id"],
                "size_in_bytes": artifact.get("size_in_bytes"),
                "digest": artifact.get("digest"),
            }
        )

    (output / "manifest.json").write_text(
        json.dumps({"run_id": args.run_id, "artifacts": manifest}, indent=2) + "\n"
    )
    print(f"Downloaded {len(samples)} sample artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
