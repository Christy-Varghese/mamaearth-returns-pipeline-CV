# The patterns, as they were taught

Every construct the capstone needs, traced to the session that taught it, in the
form the class used. **Patterns, not answers** — none of these is a finished
capstone query or a finished capstone function. You still have to decide which
one applies where, and wire it to the right columns.

Sessions you attended are marked. All of these come from modules where you were
present.

---

## SQL — Module 1

### Clause order, and why it's the one thing to memorise · S12

The engine does not run the clauses in the order you type them:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

This is why you can't filter an aggregate in `WHERE` — the aggregate doesn't
exist yet when `WHERE` runs. That's what `HAVING` is for, and it's exactly the
situation report (d) puts you in.

### CREATE TABLE · S11

```sql
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) UNIQUE
);
```

For the capstone: no AUTO_INCREMENT (your ids are strings), and you need
`FOREIGN KEY (col) REFERENCES other(col)` on the two keys in `orders`.

**Think before you type:** which two columns must *not* be NOT NULL, and why?

### JOIN and LEFT JOIN · S13

An inner `JOIN` keeps only matching rows. A `LEFT JOIN` keeps every row from the
left table and pads the right with NULLs where nothing matched — which is the
only way to find something that *isn't* there.

Report (c) asks for the same answer from a LEFT JOIN and from `NOT IN`. That's
deliberate: a LEFT JOIN that finds nothing and a LEFT JOIN written wrong look
identical, so the second query is the control.

### GROUP BY + HAVING · S13

```sql
SELECT col, COUNT(*) FROM t GROUP BY col HAVING COUNT(*) > n;
```

`GROUP BY` splits rows into buckets by distinct value; `HAVING` filters the
buckets after aggregation.

### ORDER BY, LIMIT, OFFSET · S12

`LIMIT n` takes the first n rows *after* ordering. `LIMIT n OFFSET m` skips m
first. Report (e) runs the same query twice this way.

**Think before you type:** what could go wrong with `OFFSET` if two rows tie and
there's no secondary sort key?

### UPDATE with CASE · S12

You used this in the S12 assignment:

```sql
UPDATE t SET col = CASE
    WHEN cond THEN 'A'
    ELSE 'B'
END;
```

Unmatched values fall through to `ELSE`. No `WHERE` means every row gets a value
— which is exactly what report (i) wants.

### ALTER TABLE · S11 / S12

```sql
ALTER TABLE employees ADD department_id INT;
```

Add the column first, then populate it. Two statements, in that order.

### NULL handling

`COUNT(*)` counts rows. `COUNT(column)` counts **non-NULL values in that column**
— that difference is the whole of report (b). And `COALESCE(x, 0)` substitutes a
value when `x` is NULL, which is how a missing discount becomes 0%.

---

## pandas — Module 3

### Loading and inspecting · S34, S39

```python
df = pd.read_csv("filename.csv")
df.head()      df.info()      df.describe()
df.shape       df.isnull()    df.dtypes
```

### Cleaning text columns · S35

String methods live under `.str`:

```python
df['col'].str.strip()      # trim whitespace
df['col'].str.upper()      # force case
df['col'].unique()         # what distinct values are actually in there
df['col'].value_counts()   # and how many of each
```

Chain them. Look at `.unique()` **before** you clean and again after — that
before/after is what task 2 asks you to print.

### Duplicates · S34, S35

```python
df.duplicated(subset=[...], keep='first')   # boolean mask
df.drop_duplicates(subset=[...])            # drops them
```

`subset` is the point. Without it, pandas compares every column — and if one
column is unique per row, nothing will ever match.

**Think before you type:** which column must you leave *out* of `subset`, and why?

### Missing values · S37

```python
df['col'].isna().sum()          # how many
df['col'].median()              # ignores NaN automatically
df['col'].fillna(value)         # replace, drop nothing
```

The class rule: **numerical → median, categorical → mode.** Median over mean
because the median isn't dragged by extremes.

### Merging · S39

```python
df.merge(other, on='key')                 # inner by default
df.merge(other, on='key', how='left')     # keep all left rows
```

### groupby · S39, S43

```python
df.groupby('col')['target'].mean()
df.groupby('col')['target'].agg(['count', 'mean'])
df.groupby(['col_a', 'col_b'])['target'].mean()    # two levels
```

Because `returned` is stored as 0/1, its **mean is the return rate**. No counting
needed — multiply by 100 for a percentage.

### Outliers, the 1.5×IQR rule · S35, S37, S41

```python
Q1  = df['col'].quantile(0.25)
Q3  = df['col'].quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
```

The middle 50% is the IQR; anything more than 1.5 IQRs beyond the quartiles is
fenced. `.between(lower, upper)` gives you the mask.

### Correlation and the strength bands · S35, S43, S44

```python
df[['a','b','c']].corr()
```

Bands taught in class:

| |r| | band |
|---|---|
| 0.00 – 0.19 | negligible |
| 0.20 – 0.39 | weak |
| 0.40 – 0.69 | moderate |
| 0.70 – 1.00 | strong |

Sign says direction, magnitude says strength. Correlation is not causation, and
a negligible band means the hypothesis is **busted** — say so plainly.

### Dates · S39

```python
pd.to_datetime(df['order_date'])
df['date'].dt.to_period('M')      # year-month buckets
```

### Segmentation — the S41 idea

> *An aggregate hides the driver. Segment on a second column, bucket a strong
> correlation with `pd.cut`, fence outliers with IQR, cross-tabulate two
> categoricals — then combine it into one recommendation.*

This is task 8 in one sentence. A blended 44.4% conceals that Tier-2 is 54.5%
and Tier-1 is 37.5%.

### Charts · S43, S44

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(x, y);  ax.plot(x, y, marker='o')
ax.set_xlabel(...); ax.set_ylabel(...); ax.set_title(...)
fig.tight_layout(); fig.savefig('path.png', dpi=150)
```

Class rule: **a title states the finding**, it doesn't describe the axes.

---

## Gemini — Module 2

### The call

```python
from google import genai
client = genai.Client(api_key=...)
response = client.models.generate_content(
    model=...,
    contents=user_prompt,
    config=types.GenerateContentConfig(
        system_instruction=...,      # role and rules — NOT folded into the prompt
        temperature=0.0,             # deterministic: factual report, not creative
        max_output_tokens=...,       # explicit, never the default
    ),
)
```

### Config, as taught

- **temperature** — 0 is deterministic, higher is more varied. A business report
  wants 0.
- **max_output_tokens** — a hard ceiling. Set it; don't inherit the default.
- **timeout** — minimum 10 seconds.
- **system_instruction** — separate from the user content. It fixes the role and
  the constraints; the user prompt carries the data.

### Error handling

Wrap the call in `try/except` and return a **structured dict on both paths**, so
the caller never receives a raw exception.

**Think before you type:** if you write `from google import genai` at the top of
the file, what happens on a machine where the package was never installed — and
does your offline fallback ever get a chance to run?

### SCR · S42

**Situation** — what is true. **Complication** — what is wrong. **Resolution** —
what to do. Three labelled sections, and every number traceable to the findings.

---

## If you get stuck

1. Re-read the relevant section above.
2. `python3 check.py` — the failing line names the task.
3. `../Capstone/REBUILD.md` for the reasoning behind the step.
4. Your own session notes in `_Resources/Module3_.../S**/Notes.md`.
5. Only then, the finished code.

Steps 1–4 are the ones that make it stick.
