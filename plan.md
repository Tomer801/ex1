# HW1 — Bookdelivery.com Crawler: 3-Person Work Split

## Context
University course **67978: A Needle in a Data Haystack**, HW1 (practical part), due **2026-05-07**. Three teammates need to split the work roughly evenly. Target site: `https://www.bookdelivery.com/`. Deliverable is a ZIP `ex1p_<ID>.zip` containing `code/books_crawler.py` (+ helpers), an `output/` folder with all CSV/JSON artifacts, and a consolidated PDF report with names/IDs, the required 10-row preview tables, and the summary stats table.

The work breaks into three natural layers — **fetching**, **per-book parsing**, and **DataFrame/outputs/report** — and that's how we split it. Each member owns one helper module; a thin `books_crawler.py` orchestrates them.

---

## Shared contract (agree on this BEFORE coding)
All three members depend on these. Lock them on day 1.

**Module layout** (under `code/`):
- `books_crawler.py` — entry point: `main()` wires fetch → parse → process.
- `crawler.py` — Member A.
- `parser.py` — Member B.
- `processing.py` — Member C.
- `requirements.txt` — shared.

**A → B interface:**
```python
# crawler.iter_book_links() yields:
{"book_url": str, "source_category": str}
```

**B → C interface:** `parser.parse_book(html, source_category) -> dict` returning a flat dict with these exact keys (omit a key if the field is missing on the page — required by spec for JSON):
```
Title, Category, Categories, Authors,
PriceNIS, PriceUSD, Year,
Synopsis, SynopsisLength,
StarRating, NumberOfReviews,
Language, Format,
Dimensions, DimensionsUnit, Weight, WeightUnit,
ISBN, ISBN13
```

**Shared utils** (put in `parser.py`, used by B and C):
- `ceil2(x)` → `math.ceil(x*100)/100` (the "2 decimals, rounded up" rule for Price NIS, Price USD, StarRating).
- `USD_RATE = 3.01`.

---

## Member A — Crawler / Fetching layer (`crawler.py`)
Scope:
1. Polite HTTP fetcher: a `get(url)` helper using `requests` with a real User-Agent, retries, and a **several-second delay** between requests (spec requires politeness).
2. From the homepage, programmatically extract **all top-level category links** (e.g., Art, Law). No hand-coded URLs.
3. For each category, walk the **first 5 pagination pages** (or all if fewer).
4. From each pagination page, extract links to individual book pages.
5. Expose `iter_book_links()` yielding `{"book_url", "source_category"}`.
6. Local-first methodology: save one homepage + one category page + one book page to disk and develop selectors against the local copy before looping.

Deliverable artifact for the report: nothing directly, but A produces the URL stream that everything else depends on.

---

## Member B — Per-book parsing (`parser.py`)
Scope: given a book page's HTML and its source category, return a clean dict with all 19 fields above. Owns every tricky field-level rule:
- **PriceNIS**: parse number, `ceil2`.
- **PriceUSD**: `ceil2(price_nis / 3.01)` (or × — confirm direction with team based on what site shows; spec says rate 3.01).
- **StarRating**: compute from the **star distribution histogram**, `ceil2`. Return the string `"None"` when `NumberOfReviews == 0`.
- **NumberOfReviews**: int, can be 0.
- **Authors**: comma-separated string.
- **Categories**: comma-separated list of categories shown on the book page (different from `Category`, which is the crawl source).
- **Synopsis** + **SynopsisLength** (char count).
- **Dimensions** (numerical, comma-separated) + **DimensionsUnit** (e.g., `inch`).
- **Weight** + **WeightUnit**.
- **ISBN / ISBN13**.
- **Year**, **Title**, **Language**, **Format**.
- **Missing-field rule**: if a field isn't on the page, omit the key from the returned dict (this propagates to the JSON output).

Also owns the shared `ceil2` util and the USD rate constant.

---

## Member C — DataFrame, outputs, stats, report, packaging (`processing.py` + report)
Scope:
1. Build `df_books` from B's dicts; cast numeric columns (`PriceNIS`, `PriceUSD`, `Year`, `StarRating` when not "None", `NumberOfReviews`, `Weight`, etc.) to proper dtypes.
2. **Step 2/3 outputs:**
   - Print & save first 10 rows → `output/books_before_sort.csv`.
   - Sort by `Title` ascending; save first 10 → `output/books_after_sort.csv`.
3. **Step 4 features:**
   - `IsExpensive` = 1 if `PriceNIS > median(PriceNIS)` else 0.
   - `NumberOfAuthors` = count of authors (split `Authors` on `,`).
4. **Step 4 saves:**
   - `output/books_processed.csv`.
   - `output/books_processed.json` — **nested format** `{"records": {"record": [ {...}, {...} ]}}`. Per-record missing-field omission (carry through from B).
   - `output/books_processed_preview.csv` (first 10 rows of processed).
5. **Step 5 summary stats** for `PriceUSD`, `Year`, `StarRating`, `NumberOfReviews`, `NumberOfAuthors`: mean, std, min, max, median. Include total row count. Save → `output/books_summary.csv`. Treat `StarRating == "None"` as NaN for stats.
6. **Consolidated PDF report** (e.g., `reportlab` or render Markdown → PDF): names/IDs of all 3 members, the three required 10-row preview tables (`books_before_sort`, `books_after_sort`, `books_processed_preview`), and the `books_summary` table.
7. **Packaging:** assemble `ex1p_<ID>.zip` with `code/` and `output/` folders per spec.

---

## Why this is roughly equal
- **A**: smaller surface but lots of edge cases (politeness, pagination boundaries, blocked requests, robust category discovery).
- **B**: heaviest per-field logic (19 fields, star-distribution math, missing-field handling) — but narrowly scoped to one page type.
- **C**: less scraping, but owns all output formatting, the JSON nested schema, stats with NaN handling, the PDF report, and the final ZIP.

## Critical files to be created
- `code/books_crawler.py` (orchestrator, ~30 lines).
- `code/crawler.py` (A).
- `code/parser.py` (B).
- `code/processing.py` (C).
- `code/requirements.txt`.
- `output/` artifacts: `books_before_sort.csv`, `books_after_sort.csv`, `books_processed.csv`, `books_processed.json`, `books_processed_preview.csv`, `books_summary.csv`, plus saved sample HTML/JPG examples.
- Report PDF (C).

## Verification (end-to-end)
1. `pip install -r code/requirements.txt`.
2. Run `python code/books_crawler.py` — expect it to crawl all top-level categories × up to 5 pages, then per-book pages, with several-second delays.
3. Confirm all 6 CSV/JSON artifacts exist under `output/` and row counts match.
4. Spot-check `books_processed.json` opens as valid JSON with the `records → record` nesting and that records missing a field omit that key.
5. Verify rounding: pick one book and confirm `PriceNIS`, `PriceUSD`, `StarRating` are `ceil`-rounded to 2 decimals.
6. Verify `StarRating == "None"` whenever `NumberOfReviews == 0`.
7. Open the report PDF and confirm names/IDs + 4 tables present.
8. Build the ZIP and confirm folder structure.

## Open items for the team to decide on day 1
- Who is A / B / C (and whose ID goes in the ZIP filename).
- Names and IDs to embed in the report.
- Confirm USD conversion direction (NIS / 3.01 vs NIS × 3.01) once you see real prices on the site.
