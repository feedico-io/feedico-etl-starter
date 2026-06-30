# Feedico ETL starter — coupon warehouse

> Pull your full **merchant** and **coupon** catalog from [Feedico](https://feedico.io) into a local **SQLite** database. A minimal ETL pipeline you can extend to Postgres, BigQuery, or your CMS.

**Website:** [feedico.io](https://feedico.io) · **Documentation:** [feedico.io/docs](https://feedico.io/docs)

`feedico` · `etl` · `coupon-warehouse` · `data-pipeline` · `sqlite` · `coupon-api` · `affiliate-api`

---

## Quick start

```bash
git clone https://github.com/feedico-io/feedico-etl-starter.git
cd feedico-etl-starter
cp .env.example .env
# Paste your fdco_… Bearer token

python3 pull_all.py
sqlite3 feedico_warehouse.db "SELECT COUNT(*) FROM coupons;"
```

**Requirements:** Python 3.10+ (stdlib only)

---

## What it does

1. Paginates `POST /me/networks` until all merchants are fetched
2. Paginates `POST /me/coupons` until all coupons are fetched
3. Upserts rows into SQLite using `schema.sql`
4. Stores full `raw_json` for forward-compatible field mapping

Guide context: [Build a coupon warehouse (ETL)](https://feedico.io/docs) in the Feedico documentation hub.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FEEDICO_API_TOKEN` | — | **Required.** Bearer token |
| `FEEDICO_PAGE_SIZE` | `100` | Rows per API page (max 500) |
| `FEEDICO_PROVIDER` | empty | Optional network slug filter |
| `FEEDICO_DATABASE` | `feedico_warehouse.db` | SQLite file path |

---

## Extend

- Swap SQLite for PostgreSQL — keep the same upsert pattern
- Schedule with cron, GitHub Actions, or Airflow
- Join `coupons.merchant_id` to your own storefront IDs

---

## Related projects

| Repo | Stack |
|------|--------|
| [feedico-api-php-example](https://github.com/feedico-io/feedico-api-php-example) | PHP |
| [feedico-api-python-example](https://github.com/feedico-io/feedico-api-python-example) | Python |
| [feedico-api-node-example](https://github.com/feedico-io/feedico-api-node-example) | Node.js |
| [feedico-api-csharp-example](https://github.com/feedico-io/feedico-api-csharp-example) | C# |
| [feedico-api-postman](https://github.com/feedico-io/feedico-api-postman) | Postman |
| [feedico-wp-plugin](https://github.com/feedico-io/feedico-wp-plugin) | WordPress |

---

## License

MIT — [feedico.io](https://feedico.io) · [Documentation hub](https://feedico.io/docs)
