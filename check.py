"""
Progress checker for the rebuild. Run it as often as you like.

    python3 check.py

It tells you which targets you have hit and which you have not. It does NOT
tell you how to hit them — that is the part you are practising. A red line
means go back to that task; it does not mean start over.

Nothing here touches your files. It reads mamaearth.db if you have built one,
runs your analysis script if it exists, and greps the output for the figures
the brief specifies.
"""

import os
import re
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
GREEN, RED, GREY, DIM, OFF = "\033[32m", "\033[31m", "\033[90m", "\033[2m", "\033[0m"

total = {"pass": 0, "fail": 0, "skip": 0}


def line(ok, label, got=None, want=None):
    if ok is None:
        total["skip"] += 1
        print(f"  {GREY}·  {label}{OFF}{GREY}   not written yet{OFF}")
        return
    total["pass" if ok else "fail"] += 1
    mark = f"{GREEN}ok{OFF}" if ok else f"{RED}XX{OFF}"
    tail = ""
    if not ok and want is not None:
        tail = f"   {DIM}got {got}, want {want}{OFF}"
    print(f"  {mark} {label}{tail}")


def head(title):
    print(f"\n{title}\n" + "-" * 66)


# ── PART 1 ────────────────────────────────────────────────────────────────
head("PART 1 - SQL     (build mamaearth.db with your sql/ scripts first)")

db = os.path.join(ROOT, "mamaearth.db")
if not os.path.exists(db):
    line(None, "mamaearth.db exists")
else:
    con = sqlite3.connect(db)
    q = lambda s: con.execute(s).fetchone()

    def table_ok(name, want):
        try:
            return q(f"SELECT COUNT(*) FROM {name}")[0], True
        except sqlite3.Error:
            return None, False

    for name, want in [("customers", 45), ("products", 16), ("orders", 180)]:
        got, exists = table_ok(name, want)
        line(got == want if exists else None, f"{name} row count", got, want)

    try:
        kinds = {r[0] for r in con.execute("SELECT DISTINCT typeof(rating) FROM orders")}
        # The .import trap: blanks arriving as '' instead of NULL.
        line("null" in kinds and "text" not in kinds,
             "rating blanks are NULL, not empty strings", sorted(kinds), "['integer','null']")
        rated = q("SELECT COUNT(rating) FROM orders")[0]
        line(rated == 165, "COUNT(rating) excludes the blanks", rated, 165)
    except sqlite3.Error:
        line(None, "orders table readable")

    try:
        rev = q("SELECT ROUND(SUM(quantity*price*(1-COALESCE(discount_pct,0)/100.0)),2) "
                "FROM orders JOIN products USING(product_id)")[0]
        line(rev == 99860.2, "raw revenue (report a)", rev, 99860.2)
    except sqlite3.Error:
        line(None, "orders joins to products")

    try:
        tier = dict(con.execute("SELECT loyalty_tier, COUNT(*) FROM customers GROUP BY loyalty_tier"))
        line(tier.get("Gold") == 28 and tier.get("Silver") == 17,
             "loyalty_tier added and filled (report i)", tier, "{'Gold':28,'Silver':17}")
    except sqlite3.Error:
        line(None, "loyalty_tier column (report i)")
    con.close()

reports = os.path.join(ROOT, "sql", "reports.sql")
if os.path.exists(reports):
    text = open(reports, encoding="utf-8").read()
    pasted = len(re.findall(r"^\s*--", text, re.M))
    line(pasted >= 9, "reports.sql has output pasted as comments", f"{pasted} comment lines", ">= 9")
else:
    line(None, "sql/reports.sql written")


# ── PART 2 ────────────────────────────────────────────────────────────────
head("PART 2 - pandas  (runs analysis/clean_and_eda.py and reads its output)")

eda = os.path.join(ROOT, "analysis", "clean_and_eda.py")
out = ""
if not os.path.exists(eda):
    for label in ["shape (180, 9)", "7 raw payment values", "CARD 70 / UPI 55 / COD 55",
                  "5 duplicates dropped", "shape (175, 9)", "rating median 3.0",
                  "cleaned revenue 97358.30", "delta 2501.90", "IQR fences -0.5 / 3.5",
                  "outliers O0011 and O0098", "COD 44.4%", "COD+Tier-2 54.5%",
                  "corrected peak 20318.90"]:
        line(None, label)
else:
    r = subprocess.run([sys.executable, eda], capture_output=True, text=True, cwd=ROOT)
    out = r.stdout + r.stderr
    if r.returncode != 0:
        print(f"  {RED}XX{OFF} the script raised an error:")
        print(DIM + "\n".join("      " + l for l in out.strip().splitlines()[-6:]) + OFF)
        total["fail"] += 1
    else:
        flat = re.sub(r"[,\s]+", " ", out)
        def has(*bits):
            return all(b in flat for b in bits)
        line(has("(180 9)"),              "shape (180, 9) printed")
        line(has("7") and ("upi" in out and "UPI" in out), "raw payment variants shown")
        line(has("CARD 70") or has("CARD 70.0"), "CARD 70 after standardising")
        line(has("UPI 55"),               "UPI 55")
        line(has("COD 55"),               "COD 55")
        line(has("O0176") and has("O0180"), "the 5 duplicate ids named")
        line(has("(175 9)"),              "shape (175, 9) after dedupe")
        line(has("3.0"),                  "rating median 3.0 printed before imputing")
        line(has("97358.3"),              "cleaned revenue 97358.30")
        line(has("2501.9"),               "reconciliation delta 2501.90")
        line(has("-0.5") and has("3.5"),  "IQR fences -0.5 / 3.5")
        line(has("O0011") and has("O0098"), "outliers O0011 and O0098 flagged")
        line(has("44.4"),                 "COD return rate 44.4")
        line(has("54.5") and has("37.5"), "COD by tier: 54.5 vs 37.5")
        line(has("-0.09") or has("-0.09"), "discount vs returned correlation -0.09")
        line(has("29582.1") and has("11637.1"), "January before and after correction")
        line(has("20318.9"),              "corrected peak 20318.90")
        # The reconciliation must be explained, not just printed.
        line(bool(re.search(r"duplicat", out, re.I)) and "2501.9" in flat,
             "delta attributed to the duplicates in words")

findings = os.path.join(ROOT, "narrator", "findings.json")
line(os.path.exists(findings) if os.path.exists(eda) else None,
     "narrator/findings.json written by the script")

for png in ["return_rate_by_payment.png", "monthly_revenue_trend.png"]:
    p = os.path.join(ROOT, "visualizations", png)
    viz = os.path.join(ROOT, "analysis", "visualize.py")
    line(os.path.exists(p) if os.path.exists(viz) else None, f"visualizations/{png}")


# ── PART 3 ────────────────────────────────────────────────────────────────
head("PART 3 - narrator")

narr = os.path.join(ROOT, "narrator", "generate_narrative.py")
if not os.path.exists(narr):
    line(None, "narrator/generate_narrative.py written")
else:
    src = open(narr, encoding="utf-8").read()
    line("temperature=0.0" in src.replace(" ", ""), "temperature pinned to 0.0")
    line(bool(re.search(r"max_output_tokens\s*=\s*(\d+)", src)) and
         int(re.search(r"max_output_tokens\s*=\s*(\d+)", src).group(1)) >= 300,
         "max_output_tokens set explicitly, >= 300")
    line("timeout" in src.lower(), "a timeout is set")
    line("except" in src, "the API call is wrapped in try/except")
    line("offline" in src.lower(), "an offline fallback function exists")
    # The import must NOT be at module scope, or the offline path dies first.
    top = src.split("def ")[0]
    line("from google import genai" not in top,
         "google.genai imported inside the function, not at module scope")

    env = dict(os.environ); env.pop("GEMINI_API_KEY", None)
    r = subprocess.run([sys.executable, narr], capture_output=True, text=True,
                       cwd=ROOT, env=env)
    ran = r.returncode == 0
    line(ran, "runs with no API key set")
    sample = os.path.join(ROOT, "narrator", "sample_output.txt")
    if os.path.exists(sample):
        txt = open(sample, encoding="utf-8").read().replace(",", "")
        for fig, label in [("97358.3", "cleaned revenue"), ("44.4", "COD rate"),
                           ("54.5", "COD+Tier-2"), ("2501.9", "delta"),
                           ("20318.9", "March peak")]:
            line(fig in txt, f"narrative contains {label} ({fig})")
        line("March" in open(sample, encoding="utf-8").read(), "narrative names March")
    else:
        line(None, "narrator/sample_output.txt saved")


# ── PART 4 ────────────────────────────────────────────────────────────────
head("PART 4 - README")
readme = os.path.join(ROOT, "README.md")
if not os.path.exists(readme):
    line(None, "README.md written")
else:
    rd = open(readme, encoding="utf-8").read().lower()
    line("schema.sql" in rd and "seed_data.sql" in rd, "README covers the SQL layer")
    line("clean_and_eda" in rd, "README covers the analysis layer")
    line("findings.json" in rd, "README says the analysis writes findings.json")
    line("gemini_api_key" in rd, "README explains the key, and running without one")


# ── SUMMARY ───────────────────────────────────────────────────────────────
print("\n" + "=" * 66)
p, f, s = total["pass"], total["fail"], total["skip"]
colour = GREEN if f == 0 and s == 0 else (RED if f else GREY)
print(f"{colour}{p} passing · {f} failing · {s} not started yet{OFF}")
if f == 0 and s == 0:
    print(f"{GREEN}Everything the brief asks for is present and correct.{OFF}")
elif f:
    print(f"{DIM}Work the failing lines first — each one maps to a single task.{OFF}")
else:
    print(f"{DIM}Nothing broken. Keep going.{OFF}")
