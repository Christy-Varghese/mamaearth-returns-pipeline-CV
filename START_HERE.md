# Start here

An empty workspace to rebuild the capstone from nothing. Your submitted repo in
`../Capstone/` is untouched — **don't open it.** If you get stuck, try for ten
minutes first, then look at `CLASS_SYNTAX.md`, then `../Capstone/REBUILD.md`,
and only then the finished code.

## What's here

```
data/            the three CSVs, unchanged. Never edit these.
sql/             empty — you write schema.sql, seed_data.sql, reports.sql
analysis/        empty x— you write clean_and_eda.py, visualize.py
narrator/        empty — you write generate_narrative.py
visualizations/  empty — your scripts fill it
check.py         run this any time; it tells you what passes
CLASS_SYNTAX.md  the patterns as they were taught, by session
```

## How to work

```bash
cd "/Users/cvarghese8/Documents/christy-documents/ObsidianVault/SecondBrain/DAAIG/mamaearth-returns-pipeline"
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install pandas matplotlib google-genai
python3 check.py          # 0 passing, 20 not started. That's the starting line.
```

Then: write a bit, run `check.py`, repeat. Grey means not started, green means
correct, red means go back to that one task. Nothing in `check.py` tells you
*how* — that's the part you're practising.

## The order

**1 · SQL** — `sql/schema.sql`, then `sql/seed_data.sql`, then `sql/reports.sql`.

```bash
sqlite3 mamaearth.db < sql/schema.sql
sqlite3 mamaearth.db < sql/seed_data.sql
sqlite3 -header -column mamaearth.db < sql/reports.sql
```

After seeding, before anything else, run this:

```sql
SELECT DISTINCT typeof(rating) FROM orders;
```

You want `integer` and `null`. If you see `text`, your blank cells loaded as
empty strings and report (b) will be wrong. `check.py` catches it.

**2 · pandas** — `analysis/clean_and_eda.py`. Casing → duplicates → impute →
merge → outliers → hypotheses → time series → write `findings.json`. That order
is the content, not a formality; `REBUILD.md` explains why each step depends on
the one before.

**3 · charts** — `analysis/visualize.py`.

**4 · narrator** — `narrator/generate_narrative.py`. **Write the offline path
first.** It needs no key, no network, and it's 5 marks banked before you touch
the API.

**5 · README**, then clone-and-rehearse.

## The numbers to hit

Keep these where you can see them. If yours differ, your code has a bug — every
one was re-computed from these exact CSVs.

| | |
|---|---|
| Raw revenue | **99,860.20** across 180 rows |
| Cleaned revenue | **97,358.30** across 175 rows |
| The gap | **2,501.90** — exactly the five duplicates |
| Payment counts | CARD 70 · UPI 55 · COD 55 |
| Duplicates | O0176 – O0180 |
| Rating median | **3.0** (12 discounts and 15 ratings filled) |
| IQR fences | Q1 1.0, Q3 2.0 → −0.5 and 3.5 |
| Outliers | O0011 (25 units) · O0098 (30 units) |
| Return rates | COD **44.4%** · UPI 18.9% · CARD 14.7% |
| Worst segment | COD + Tier-2 **54.5%** (Tier-1 is 37.5%) |
| January | 29,582.10 raw → **11,637.10** corrected |
| True peak | **March 2026, 20,318.90** |
| Zero-order customer | C045 Vihaan |
| Loyalty split | Gold 28 · Silver 17 |

## When check.py goes all green

46 passing, 0 failing, 0 not started. At that point you've built it twice, and
the second time you'll be able to say why every line is there — which is the
whole reason for doing this.
