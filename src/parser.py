"""
parser.py  —  Owner: Member B

Responsible for turning a single book page's HTML into a flat dict.
Owns every per-field rule (rounding, missing-field omission, star-rating math).

Public API (only thing the orchestrator calls):
    parse_book(html: str, source_category: str) -> dict

Shared utilities (also used by processing.py — DO NOT duplicate elsewhere):
    USD_RATE
    ceil2(x)

Spec rules to enforce here:
  * "2 decimal digits, rounded UP" for PriceNIS, PriceUSD, StarRating  -> use ceil2().
  * USD conversion uses rate 3.01 (confirm direction with the team after you see
    a real price on the site; the spec just says "exchange rate 3.01").
  * If the book page does NOT contain a field, OMIT that key from the returned dict.
    (This is required so books_processed.json can drop missing fields per record.)
  * StarRating is computed from the star-distribution histogram. If NumberOfReviews == 0,
    StarRating must be the literal string "None".
"""

from __future__ import annotations

import math

USD_RATE = 3.01

# Canonical key order for the 19 extraction fields. Members B and C should both
# refer to this when in doubt.
EXPECTED_KEYS = [
    "Title",
    "Category",
    "Categories",
    "Authors",
    "PriceNIS",
    "PriceUSD",
    "Year",
    "Synopsis",
    "SynopsisLength",
    "StarRating",
    "NumberOfReviews",
    "Language",
    "Format",
    "Dimensions",
    "DimensionsUnit",
    "Weight",
    "WeightUnit",
    "ISBN",
    "ISBN13",
]


def ceil2(x: float) -> float:
    """Round x UP to 2 decimal places.

    Used for PriceNIS, PriceUSD, StarRating per the spec
    ("2 decimal digits, rounded up").
    """
    return math.ceil(x * 100) / 100


def parse_book(html: str, source_category: str) -> dict:
    """Parse a single book page and return a flat dict of book fields.

    Args:
        html: raw HTML of the book detail page.
        source_category: the category this book was crawled under (becomes the
            "Category" field — distinct from "Categories" which is whatever the
            book page itself lists).

    Returns:
        dict with any subset of the keys in EXPECTED_KEYS. Keys for fields that
        do not appear on the page MUST be omitted (not set to None / "" / NaN).

    Field rules:
        Title             : str
        Category          : str (== source_category)
        Categories        : str — comma-separated list from the page
        Authors           : str — comma-separated list
        PriceNIS          : float, ceil2()
        PriceUSD          : float, ceil2(price_nis converted via USD_RATE)
        Year              : int
        Synopsis          : str
        SynopsisLength    : int (len(Synopsis))
        StarRating        : float (ceil2) computed from the star-distribution
                            histogram, OR the string "None" when NumberOfReviews == 0
        NumberOfReviews   : int (can be 0)
        Language          : str
        Format            : str (e.g. "Hardcover", "Paperback")
        Dimensions        : str — numerical, comma-separated (e.g. "8.5,5.5,1.2")
        DimensionsUnit    : str (e.g. "inch")
        Weight            : float
        WeightUnit        : str (e.g. "pounds")
        ISBN              : str
        ISBN13            : str
    """
    raise NotImplementedError("Member B: implement full book-page parser.")


# ---------------------------------------------------------------------------
# Private helpers — fill these in to keep parse_book() readable.
# Each returns either the extracted value or None (None signals "field absent",
# and parse_book() should then OMIT the key from the final dict).
# ---------------------------------------------------------------------------

def _extract_title(soup) -> str | None:
    """Return the book title, or None if not present."""
    raise NotImplementedError("Member B")


def _extract_authors(soup) -> str | None:
    """Return a comma-separated string of authors, or None."""
    raise NotImplementedError("Member B")


def _extract_categories(soup) -> str | None:
    """Return a comma-separated string of categories shown on the page, or None.
    NOTE: this is different from the `Category` field, which is the crawl source.
    """
    raise NotImplementedError("Member B")


def _extract_price_nis(soup) -> float | None:
    """Return the book's price in NIS as float (already passed through ceil2)."""
    raise NotImplementedError("Member B")


def _compute_price_usd(price_nis: float) -> float:
    """Convert NIS price to USD using USD_RATE. Returns ceil2(result).

    Confirm direction (divide vs multiply) with the team after eyeballing the site.
    """
    raise NotImplementedError("Member B")


def _extract_year(soup) -> int | None:
    """Return publication year as int, or None."""
    raise NotImplementedError("Member B")


def _extract_synopsis(soup) -> str | None:
    """Return synopsis text, or None."""
    raise NotImplementedError("Member B")


def _extract_star_rating(soup) -> tuple:
    """Compute StarRating from the star-distribution histogram on the page.

    Returns:
        (rating, n_reviews) where:
          - n_reviews is int (can be 0)
          - rating is float ceil2'd to 2dp, OR the string "None" when n_reviews == 0
        Return (None, None) if the page has no rating widget at all.
    """
    raise NotImplementedError("Member B")


def _extract_language(soup) -> str | None:
    raise NotImplementedError("Member B")


def _extract_format(soup) -> str | None:
    raise NotImplementedError("Member B")


def _extract_dimensions(soup) -> tuple:
    """Return (dimensions_str, unit_str) e.g. ("8.5,5.5,1.2", "inch"),
    or (None, None) if not present.
    """
    raise NotImplementedError("Member B")


def _extract_weight(soup) -> tuple:
    """Return (weight_value: float, unit: str) or (None, None)."""
    raise NotImplementedError("Member B")


def _extract_isbns(soup) -> tuple:
    """Return (isbn, isbn13) where each is a string or None."""
    raise NotImplementedError("Member B")
