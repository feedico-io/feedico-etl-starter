-- Minimal SQLite schema for a Feedico coupon warehouse.
-- Adapt column names to your API payload fields.

CREATE TABLE IF NOT EXISTS merchants (
    id TEXT PRIMARY KEY,
    firm_name TEXT,
    provider TEXT,
    website TEXT,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS coupons (
    id TEXT PRIMARY KEY,
    merchant_id TEXT,
    title TEXT,
    coupon_code TEXT,
    provider TEXT,
    firm_name TEXT,
    starts_at TEXT,
    ends_at TEXT,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_coupons_merchant ON coupons(merchant_id);
CREATE INDEX IF NOT EXISTS idx_coupons_provider ON coupons(provider);
CREATE INDEX IF NOT EXISTS idx_merchants_provider ON merchants(provider);
