#!/usr/bin/env python3
"""Pull all merchants and coupons from Feedico into a local SQLite warehouse."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://api.feedico.io/api/v1"
ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def api_post(token: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        data=data,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Expected JSON object from Feedico.")
    return payload


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("networks", "coupons", "items"):
            nested = payload.get(key)
            if isinstance(nested, list):
                return [row for row in nested if isinstance(row, dict)]
    return []


def paginate(token: str, path: str, page_size: int, provider: str | None) -> list[dict[str, Any]]:
    page = 1
    all_rows: list[dict[str, Any]] = []
    while True:
        body = {
            "page": page,
            "pageSize": page_size,
            "provider": provider,
            "firmName": "",
        }
        rows = extract_rows(api_post(token, path, body))
        if not rows:
            break
        all_rows.extend(rows)
        print(f"  page {page}: +{len(rows)} rows (total {len(all_rows)})")
        if len(rows) < page_size:
            break
        page += 1
        time.sleep(0.2)
    return all_rows


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))


def upsert_merchants(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        row_id = str(row.get("id") or row.get("merchantId") or "")
        if not row_id:
            continue
        conn.execute(
            """
            INSERT INTO merchants (id, firm_name, provider, website, raw_json, synced_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                firm_name = excluded.firm_name,
                provider = excluded.provider,
                website = excluded.website,
                raw_json = excluded.raw_json,
                synced_at = excluded.synced_at
            """,
            (
                row_id,
                row.get("firmName") or row.get("name"),
                row.get("provider"),
                row.get("website") or row.get("websiteUrl"),
                json.dumps(row, ensure_ascii=False),
            ),
        )


def upsert_coupons(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        row_id = str(row.get("id") or row.get("couponId") or "")
        if not row_id:
            continue
        conn.execute(
            """
            INSERT INTO coupons (
                id, merchant_id, title, coupon_code, provider, firm_name,
                starts_at, ends_at, raw_json, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                merchant_id = excluded.merchant_id,
                title = excluded.title,
                coupon_code = excluded.coupon_code,
                provider = excluded.provider,
                firm_name = excluded.firm_name,
                starts_at = excluded.starts_at,
                ends_at = excluded.ends_at,
                raw_json = excluded.raw_json,
                synced_at = excluded.synced_at
            """,
            (
                row_id,
                str(row.get("merchantId") or row.get("networkId") or ""),
                row.get("title") or row.get("description"),
                row.get("couponCode") or row.get("code"),
                row.get("provider"),
                row.get("firmName") or row.get("merchantName"),
                row.get("startsAt") or row.get("startDate"),
                row.get("endsAt") or row.get("endDate"),
                json.dumps(row, ensure_ascii=False),
            ),
        )


def main() -> int:
    load_dotenv(ROOT / ".env")
    token = os.environ.get("FEEDICO_API_TOKEN", "").strip()
    if not token:
        print("Set FEEDICO_API_TOKEN in .env", file=sys.stderr)
        return 1

    page_size = int(os.environ.get("FEEDICO_PAGE_SIZE", "100"))
    provider = os.environ.get("FEEDICO_PROVIDER") or None
    db_path = os.environ.get("FEEDICO_DATABASE", "feedico_warehouse.db")

    conn = sqlite3.connect(db_path)
    init_db(conn)

    print("Pulling merchants…")
    merchants = paginate(token, "/me/networks", page_size, provider)
    upsert_merchants(conn, merchants)

    print("Pulling coupons…")
    coupons = paginate(token, "/me/coupons", page_size, provider)
    upsert_coupons(conn, coupons)

    conn.commit()
    conn.close()
    print(f"Done. Database: {db_path} ({len(merchants)} merchants, {len(coupons)} coupons)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
