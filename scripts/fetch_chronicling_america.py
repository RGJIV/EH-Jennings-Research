#!/usr/bin/env python3
"""
fetch_chronicling_america.py

Replacement for the old legacy-Chronicling-America-API script.

Background: chroniclingamerica.loc.gov's dedicated API was retired when the
site migrated to the main loc.gov platform (Aug 4, 2025). Chronicling
America content is now served exclusively through the loc.gov JSON/YAML API.
Plain HTML page requests to www.loc.gov/item/... or .../resource/... are
frequently blocked by bot detection; appending `?fo=json` to an item or
resource URL requests the underlying JSON directly instead, which is the
documented, supported way to pull structured data and full OCR text.

IMPORTANT CAVEAT (learned the hard way): even the JSON endpoint gets
bot-blocked if you hit it too fast or too often in a short window. This
script defaults to a multi-second delay between requests and retries with
backoff. If you still get blocked, slow it down further (increase
--delay) rather than assuming the endpoint is dead -- it may just need
more time between calls. Don't assume a title/date is inaccessible after
one failure; the blocking observed during testing was inconsistent even
for identical URL patterns.

Usage:
    python fetch_chronicling_america.py --lccn sn88085947 --date 1910-01-22 --edition 1
    python fetch_chronicling_america.py --batch batch.csv --delay 6

batch.csv format (no header):
    sn88085947,1910-01-22,1
    sn83045462,1931-09-04,1

Output: one JSON file per issue in ./output/, containing the raw API
response, plus a companion .txt file with just the extracted OCR text
from each page (segment) -- this is what you actually want to read.
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_BASE = "https://www.loc.gov"
DEFAULT_DELAY = 6.0  # seconds between requests -- do not lower this casually
MAX_RETRIES = 3
USER_AGENT = (
    "EH-Jennings-Research/1.0 (personal genealogy research; "
    "contact via GitHub repo RGJIV/EH-Jennings-Research)"
)


def build_resource_url(lccn: str, date: str, edition: str = "1") -> str:
    """Build the loc.gov resource JSON endpoint for a specific newspaper issue.

    Pattern confirmed working against loc.gov's current API:
        https://www.loc.gov/resource/{lccn}/{date}/ed-{edition}/?fo=json
    """
    return f"{API_BASE}/resource/{lccn}/{date}/ed-{edition}/?fo=json"


def fetch_json(url: str, max_retries: int = MAX_RETRIES, delay: float = DEFAULT_DELAY) -> dict | None:
    """Fetch a loc.gov JSON API endpoint with retry/backoff.

    Returns the parsed JSON dict on success, or None if every attempt failed
    (bot-detection blocks, timeouts, etc.) -- callers should treat None as
    "could not retrieve this time," not "this content does not exist."
    """
    for attempt in range(1, max_retries + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urlopen(req, timeout=30) as resp:
                if resp.status != 200:
                    print(f"  [warn] HTTP {resp.status} on attempt {attempt} for {url}")
                else:
                    return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            print(f"  [warn] HTTPError {e.code} on attempt {attempt} for {url}: {e.reason}")
        except URLError as e:
            print(f"  [warn] URLError on attempt {attempt} for {url}: {e.reason}")
        except json.JSONDecodeError:
            print(f"  [warn] Response wasn't valid JSON on attempt {attempt} for {url} "
                  f"(likely got an HTML block page instead of the API response)")

        if attempt < max_retries:
            backoff = delay * attempt  # linear backoff: 6s, 12s, 18s...
            print(f"  retrying in {backoff:.0f}s...")
            time.sleep(backoff)

    return None


def extract_ocr_text(data: dict) -> list[str]:
    """Pull the OCR text out of each page/segment of a resource response.

    Full-page OCR text lives in segments[].description as a list of
    paragraphs/blocks. Returns one string per segment (page); most single-
    edition issues have one segment per page image.
    """
    texts = []
    for segment in data.get("segments", []):
        desc = segment.get("description", [])
        if desc:
            texts.append("\n\n".join(desc))
    return texts


def process_issue(lccn: str, date: str, edition: str, outdir: Path, delay: float) -> bool:
    url = build_resource_url(lccn, date, edition)
    safe_name = f"{lccn}_{date}_ed{edition}"
    print(f"Fetching {safe_name} -> {url}")

    data = fetch_json(url, delay=delay)
    if data is None:
        print(f"  [FAILED] Could not retrieve {safe_name} after retries. "
              f"Logging to output/{safe_name}.FAILED and moving on.")
        (outdir / f"{safe_name}.FAILED").write_text(
            f"Failed to fetch {url}\nTry again later with a longer --delay.\n"
        )
        return False

    (outdir / f"{safe_name}.json").write_text(json.dumps(data, indent=2))

    texts = extract_ocr_text(data)
    if texts:
        combined = "\n\n===== PAGE BREAK =====\n\n".join(texts)
        (outdir / f"{safe_name}.txt").write_text(combined)
        print(f"  [OK] Saved {safe_name}.json and {safe_name}.txt "
              f"({len(texts)} page(s) of OCR text)")
    else:
        print(f"  [OK] Saved {safe_name}.json but no OCR text found in segments "
              f"(item may not have hassegments=true, or may be image-only)")

    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lccn", help="Newspaper LCCN, e.g. sn88085947")
    parser.add_argument("--date", help="Issue date, YYYY-MM-DD")
    parser.add_argument("--edition", default="1", help="Edition number (default: 1)")
    parser.add_argument("--batch", help="CSV file of lccn,date,edition rows for bulk fetching")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                         help=f"Seconds to wait between requests (default: {DEFAULT_DELAY}). "
                              f"Increase this if you start getting blocked.")
    parser.add_argument("--outdir", default="output", help="Output directory (default: ./output)")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    jobs = []
    if args.batch:
        with open(args.batch, newline="") as f:
            for row in csv.reader(f):
                if not row or row[0].strip().startswith("#"):
                    continue
                lccn = row[0].strip()
                date = row[1].strip()
                edition = row[2].strip() if len(row) > 2 else "1"
                jobs.append((lccn, date, edition))
    elif args.lccn and args.date:
        jobs.append((args.lccn, args.date, args.edition))
    else:
        parser.error("Provide either --lccn/--date or --batch")

    print(f"Processing {len(jobs)} issue(s) with {args.delay}s delay between requests...\n")

    results = {"ok": 0, "failed": 0}
    for i, (lccn, date, edition) in enumerate(jobs):
        ok = process_issue(lccn, date, edition, outdir, args.delay)
        results["ok" if ok else "failed"] += 1
        if i < len(jobs) - 1:
            time.sleep(args.delay)

    print(f"\nDone. {results['ok']} succeeded, {results['failed']} failed.")
    if results["failed"]:
        print("Failed issues are logged as .FAILED files in the output directory. "
              "Re-run with a longer --delay before concluding a source is unreachable.")
        sys.exit(1)


if __name__ == "__main__":
    main()
