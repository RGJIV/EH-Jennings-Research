#!/usr/bin/env python3
"""
fetch_chronicling_america.py  (improved loc.gov JSON API version)
Walks a Chronicling America newspaper via the official loc.gov JSON API
and searches OCR full text for keywords. Designed for the EH-Jennings-Research
project.

Key improvements over the original draft:
- Progress file so long runs can be resumed cleanly
- Optional list of OCR variants (Jenninga, Jennlngs, etc.)
- Slightly more defensive JSON parsing
- Clearer logging and summary
- Default delay raised to 4.0 s for safer unattended runs

USAGE EXAMPLE (Sistersville Daily Oil Review era of interest):

    python scripts/fetch_chronicling_america.py \
        --lccn sn86092356 \
        --start 1903-01-01 \
        --end 1906-06-30 \
        --keywords "Jennings" "Kanawha" "Buckeye" "Sugar Grove" "Culp" \
        --ocr-variants "Jenninga" "Jennlngs" "Kanawlia" \
        --output sistersville_jennings_1903-1906.csv \
        --delay 4.0

RATE LIMITS (loc.gov JSON/YAML API):
- Documented ceiling ~20 requests/minute.
- Script defaults to 4.0 s (~15/min). Do not go below 3.1 s.
- On 429 the script backs off exponentially.
- On non-JSON (CAPTCHA) response it stops entirely.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE = "https://www.loc.gov/resource/{lccn}/{date}/ed-1/"
USER_AGENT = (
    "EH-Jennings-Research/1.1 "
    "(personal genealogy research; github.com/RGJIV/EH-Jennings-Research)"
)
PROGRESS_FILE = ".chronicling_progress"

def fetch_issue(lccn, date_str, delay, max_retries=4):
    """Fetch one day's issue JSON. Returns dict or None."""
    url = BASE.format(lccn=lccn, date=date_str) + "?fo=json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
                time.sleep(delay)
                return json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                time.sleep(delay)
                return None
            if e.code == 429:
                wait = 90 * (attempt + 1)
                print(f"  [429] Rate limited. Waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  [HTTP {e.code}] {url}", file=sys.stderr)
            time.sleep(delay)
            return None
        except urllib.error.URLError as e:
            print(f"  [URLError] {e.reason} on {url}", file=sys.stderr)
            time.sleep(delay)
            return None
        except json.JSONDecodeError:
            print(f"  [Non-JSON / CAPTCHA] {url}", file=sys.stderr)
            print(
                "Stopping. Wait at least 1 hour before resuming and "
                "consider increasing --delay.",
                file=sys.stderr,
            )
            sys.exit(1)
    print(f"  [FAILED after {max_retries} retries] {url}", file=sys.stderr)
    return None

def extract_segments(issue_json):
    """Extract page-level OCR + metadata."""
    segments = issue_json.get("segments") or []
    out = []
    for seg in segments:
        text_parts = seg.get("description") or []
        if isinstance(text_parts, list):
            text = " ".join(str(p) for p in text_parts)
        else:
            text = str(text_parts)
        page_number = ""
        np = seg.get("number_page")
        if isinstance(np, list) and np:
            page_number = str(np[0])
        elif np:
            page_number = str(np)
        out.append({
            "page_url": seg.get("url", ""),
            "page_number": page_number,
            "text": text,
        })
    return out

def search_keywords(text, keywords):
    hits = []
    lower_text = text.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in lower_text:
            for m in re.finditer(re.escape(kw_lower), lower_text):
                start = max(0, m.start() - 160)
                end = min(len(text), m.end() + 160)
                context = text[start:end].replace("\n", " ").strip()
                hits.append((kw, context))
    return hits

def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return f.read().strip()
    return None

def save_progress(date_str):
    with open(PROGRESS_FILE, "w") as f:
        f.write(date_str)

def main():
    ap = argparse.ArgumentParser(
        description="Walk Chronicling America via loc.gov JSON API and search OCR."
    )
    ap.add_argument("--lccn", required=True, help="LCCN, e.g. sn86092356")
    ap.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    ap.add_argument("--keywords", nargs="+", required=True,
                    help="Keywords/phrases (case-insensitive)")
    ap.add_argument("--ocr-variants", nargs="*", default=[],
                    help="Additional OCR-error spellings to search")
    ap.add_argument("--output", default="matches.csv")
    ap.add_argument("--delay", type=float, default=4.0,
                    help="Seconds between requests (default 4.0)")
    ap.add_argument("--resume", action="store_true",
                    help="Resume from last successful date in progress file")
    args = ap.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()

    if args.resume:
        last = load_progress()
        if last:
            resume_date = datetime.strptime(last, "%Y-%m-%d").date() + timedelta(days=1)
            if resume_date > start:
                print(f"Resuming from {resume_date}", file=sys.stderr)
                start = resume_date

    if args.delay < 3.1:
        print("Warning: delay < 3.1 s exceeds documented 20/min limit.", file=sys.stderr)

    all_keywords = list(args.keywords) + list(args.ocr_variants)
    results = []
    checked = 0
    found_issues = 0

    for d in daterange(start, end):
        date_str = d.strftime("%Y-%m-%d")
        print(f"Checking {date_str}...", file=sys.stderr)
        issue = fetch_issue(args.lccn, date_str, args.delay)
        checked += 1
        save_progress(date_str)

        if issue is None:
            continue

        found_issues += 1
        segments = extract_segments(issue)
        for seg in segments:
            hits = search_keywords(seg["text"], all_keywords)
            for kw, context in hits:
                results.append({
                    "date": date_str,
                    "keyword": kw,
                    "page_url": seg["page_url"],
                    "page_number": seg["page_number"],
                    "context": context,
                })
                print(f"  MATCH ({kw}) {date_str} p{seg['page_number']}", file=sys.stderr)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["date", "keyword", "page_url", "page_number", "context"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(
        f"\nDone. Checked {checked} days, found {found_issues} issues, "
        f"{len(results)} hits → {args.output}",
        file=sys.stderr,
    )

if __name__ == "__main__":
    main()
