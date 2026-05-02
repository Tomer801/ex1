"""
processing.py  —  Owner: Member C

Responsible for everything downstream of parsing:
  * building df_books
  * before-sort / after-sort 10-row CSV outputs
  * Step 4 features (IsExpensive, NumberOfAuthors)
  * saving books_processed.{csv,json} and books_processed_preview.csv
  * Step 5 summary statistics -> books_summary.csv
  * the consolidated PDF report (names/IDs + 4 tables)
  * final ZIP packaging (ex1p_<ID>.zip)

Public API (orchestrator only calls this):
    run_all(records: list[dict]) -> None

Spec rules to enforce here:
  * books_processed.json MUST be nested as {"records": {"record": [ {...}, ... ]}}.
  * Per-record missing-field omission must carry through to the JSON
    (a record's dict already omits absent keys — preserve that on write).
  * Stats columns: PriceUSD, Year, StarRating, NumberOfReviews, NumberOfAuthors.
    Treat StarRating == "None" as NaN for stats.
  * Summary table must include the total number of rows.
"""

from __future__ import annotations

import pandas as pd

# Fill these in before building the report. Members commit names/IDs together.
STUDENT_NAMES_AND_IDS: list[tuple[str, str]] = [
    # ("Full Name", "ID"),
]

# Whichever member's ID the team picks for the ZIP filename.
SUBMITTING_STUDENT_ID: str = ""


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    """Build df_books from the parsed records.

    Cast numeric columns to numeric dtypes (PriceNIS, PriceUSD, Year,
    NumberOfReviews, Weight, ...). Be careful with StarRating: it can be the
    string "None" -> keep that as-is; coerce only the rows that are numeric.
    """
    raise NotImplementedError("Member C")


def save_before_sort(df: pd.DataFrame) -> None:
    """Print and save df.head(10) -> output/books_before_sort.csv (Step 2)."""
    raise NotImplementedError("Member C")


def save_after_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Sort df by Title ascending. Save sorted df.head(10) ->
    output/books_after_sort.csv. Return the sorted DataFrame (Step 3).
    """
    raise NotImplementedError("Member C")


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Step 4 — add two derived columns:
      * IsExpensive       : 1 if PriceNIS > median(PriceNIS) else 0
      * NumberOfAuthors   : count of comma-separated authors in the Authors field
    Return the augmented DataFrame.
    """
    raise NotImplementedError("Member C")


def save_processed(df: pd.DataFrame) -> None:
    """Write the three Step-4 artifacts:
      * output/books_processed.csv
      * output/books_processed.json    -> {"records": {"record": [ {...}, ... ]}}
            Each record dict must omit keys whose value is missing (NaN / None).
      * output/books_processed_preview.csv  -> df.head(10)
    """
    raise NotImplementedError("Member C")


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Step 5 — compute mean/std/min/max/median for:
        PriceUSD, Year, StarRating, NumberOfReviews, NumberOfAuthors.
    Treat StarRating == "None" as NaN for the calculation.
    Append a row (or column) carrying the total number of rows in df.
    Save -> output/books_summary.csv. Return the summary DataFrame.
    """
    raise NotImplementedError("Member C")


def build_report_pdf(
    before_sort: pd.DataFrame,
    after_sort: pd.DataFrame,
    processed_preview: pd.DataFrame,
    summary: pd.DataFrame,
    out_path: str = "output/report.pdf",
) -> None:
    """Build the consolidated PDF report. Must contain:
      * student names + IDs of all 3 members (from STUDENT_NAMES_AND_IDS)
      * the three 10-row preview tables (before-sort, after-sort, processed-preview)
      * the summary statistics table
    Suggested library: reportlab (already in requirements.txt).
    """
    raise NotImplementedError("Member C")


def build_zip(student_id: str = "") -> None:
    """Assemble ex1p_<ID>.zip with this folder structure:

        ex1p_<ID>.zip
        ├── code/
        │   ├── books_crawler.py
        │   ├── crawler.py
        │   ├── parser.py
        │   ├── processing.py
        │   └── requirements.txt
        └── output/
            ├── books_before_sort.csv
            ├── books_after_sort.csv
            ├── books_processed.csv
            ├── books_processed.json
            ├── books_processed_preview.csv
            ├── books_summary.csv
            └── report.pdf
    """
    raise NotImplementedError("Member C")


def run_all(records: list[dict]) -> None:
    """Convenience entry point used by books_crawler.main().

    Calls every step in order:
        df = build_dataframe(records)
        save_before_sort(df)
        df_sorted = save_after_sort(df)
        df_proc = add_features(df_sorted)
        save_processed(df_proc)
        summary = compute_summary(df_proc)
        build_report_pdf(df.head(10), df_sorted.head(10), df_proc.head(10), summary)
        build_zip(SUBMITTING_STUDENT_ID)
    """
    raise NotImplementedError("Member C")
