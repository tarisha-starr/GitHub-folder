"""Connection check for GoPlus.

Answers two questions without needing their docs:

  1. Is GOPLUS_API_KEY actually reaching the workflow?
  2. Which authentication scheme does the API accept?

usegoplus.com blocks automated doc fetches (403), so the auth scheme is
unknown. Rather than guess in the client, this probes a handful of common
schemes once each and reports the HTTP status. The status tells us what we
need:

    200/2xx  this scheme works, build the client on it
    401/403  reached the API, wrong credentials or wrong scheme
    404      auth may be fine, the path is wrong
    000      host unreachable or the base URL is wrong

The key is never printed, logged, or included in output. Only its length and
a masked prefix appear, which is enough to catch a truncated paste without
exposing anything.

Usage:
    python3 goplus_check.py                    # probe with defaults
    python3 goplus_check.py --path /v1/contacts
    python3 goplus_check.py --presence-only    # just check the env vars
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

TIMEOUT = 15
DEFAULT_BASE = "https://api.usegoplus.com"

# Paths worth trying first. Most REST APIs answer at least one of these.
CANDIDATE_PATHS = ["/", "/v1", "/api/v1", "/me", "/v1/me", "/account"]


def mask(secret: str) -> str:
    """Show enough to spot a truncated paste, never enough to use."""
    if not secret:
        return "(empty)"
    if len(secret) <= 8:
        return f"{'*' * len(secret)} (len {len(secret)})"
    return f"{secret[:3]}{'*' * (len(secret) - 6)}{secret[-3:]} (len {len(secret)})"


def auth_schemes(key: str) -> list[tuple[str, dict]]:
    """Common ways APIs accept a key. One request each, no brute forcing."""
    return [
        ("Bearer token", {"Authorization": f"Bearer {key}"}),
        ("X-API-Key header", {"X-API-Key": key}),
        ("Api-Key header", {"Api-Key": key}),
        ("Authorization raw", {"Authorization": key}),
    ]


def probe(url: str, headers: dict) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "goplus-check/1.0",
        **headers,
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            body = resp.read(400).decode("utf-8", "replace")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read(400).decode("utf-8", "replace")
        except Exception:
            pass
        return exc.code, body
    except Exception as exc:
        return 0, f"{type(exc).__name__}: {exc}"


def main() -> int:
    ap = argparse.ArgumentParser(description="GoPlus connection check")
    ap.add_argument("--path", help="specific API path to probe")
    ap.add_argument("--presence-only", action="store_true",
                    help="only verify the env vars are set")
    args = ap.parse_args()

    key = os.environ.get("GOPLUS_API_KEY", "").strip()
    base = os.environ.get("GOPLUS_API_BASE", "").strip() or DEFAULT_BASE
    account = os.environ.get("GOPLUS_ACCOUNT_ID", "").strip()

    print("GoPlus connection check")
    print("=" * 46)
    print(f"  GOPLUS_API_KEY     {mask(key)}")
    print(f"  GOPLUS_API_BASE    {base}{'  (default)' if base == DEFAULT_BASE else ''}")
    print(f"  GOPLUS_ACCOUNT_ID  {account or '(not set)'}")
    print()

    if not key:
        print("FAIL: GOPLUS_API_KEY is not set.")
        print()
        print("If this ran in GitHub Actions, the secret exists but wasn't passed")
        print("to the step. Check the workflow's `env:` block. If it ran locally,")
        print("add it to automation/.env")
        return 1

    print(f"OK: key is present ({len(key)} chars).")

    if args.presence_only:
        return 0

    base = base.rstrip("/")
    paths = [args.path] if args.path else CANDIDATE_PATHS
    print(f"\nProbing {len(paths)} path(s) x {len(auth_schemes(key))} auth scheme(s)...\n")

    reached = False
    winners = []

    for path in paths:
        url = f"{base}{path}"
        for label, headers in auth_schemes(key):
            status, body = probe(url, headers)
            snippet = body.replace("\n", " ")[:90]
            if status == 0:
                print(f"  {path:<14} {label:<18} unreachable  {snippet}")
                continue
            reached = True
            verdict = ""
            if 200 <= status < 300:
                verdict = "  <-- WORKS"
                winners.append((path, label))
            print(f"  {path:<14} {label:<18} HTTP {status}{verdict}")
            if snippet and status >= 400:
                print(f"  {'':<14} {'':<18}      {snippet}")

    print()
    if winners:
        print("RESULT: connection works.")
        for path, label in winners:
            print(f"  Use {label} against {base}{path}")
        print("\nSend this output and I'll build the puller on it.")
        return 0

    if reached:
        print("RESULT: the host is reachable but nothing authenticated.")
        print("The key is valid-looking but the scheme or path is wrong.")
        print("Send the GoPlus API docs URL and I'll target the right endpoint.")
        return 1

    print("RESULT: could not reach the host at all.")
    print(f"'{base}' is probably not the right API base URL.")
    print("Check the GoPlus API docs for the correct one and set GOPLUS_API_BASE.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
