"""
crawler.py  —  Owner: Member A

Responsible for everything network-facing:
  * polite HTTP fetching (real User-Agent, retries, several-second delay)
  * discovering all top-level category links from the homepage
  * walking up to 5 pagination pages per category
  * extracting individual book-page URLs from each pagination page

The orchestrator (books_crawler.py) only ever calls:
  * get(url)               -> str  (HTML)
  * iter_book_links()      -> Iterator[{"book_url": str, "source_category": str}]

Spec rules to enforce here:
  * NO hand-coded category or book URLs. Everything must be discovered programmatically.
  * Significant delay between requests (REQUEST_DELAY_SEC).
  * Methodology: download one homepage / one category page / one book page locally
    first, then develop selectors against the local copies before turning on the loop.
"""

from __future__ import annotations

from typing import Iterator

BASE_URL = "https://www.bookdelivery.com/"
REQUEST_DELAY_SEC = 3
MAX_PAGES_PER_CATEGORY = 5
USER_AGENT = "Mozilla/5.0 (compatible; HUJI-67978-HW1-crawler/1.0)"


def get(url: str) -> str:
    """Fetch `url` and return the response body as text.

    Must:
      * send a real User-Agent header (USER_AGENT)
      * retry on transient failures (e.g. 5xx, connection errors) — at least 2 retries
      * sleep REQUEST_DELAY_SEC between requests (politeness)
      * raise on permanent failure so the caller can decide what to do
    """
    raise NotImplementedError("Member A: implement polite HTTP fetcher.")


def get_category_links(homepage_html: str) -> list[tuple[str, str]]:
    """Parse the homepage HTML and return every top-level category link.

    Returns:
        A list of (category_name, category_absolute_url) tuples.
        Example: [("Art", "https://www.bookdelivery.com/category/art"), ...]

    Must be programmatic — no hard-coded category names or URLs.
    """
    raise NotImplementedError("Member A: implement homepage -> category list.")


def get_book_links_from_category(category_url: str) -> list[str]:
    """Walk up to MAX_PAGES_PER_CATEGORY pagination pages of `category_url`
    and return every individual book-page URL found across those pages.

    If the category has fewer than 5 pagination pages, traverse all of them.
    Use get() for every fetch so the politeness delay is respected.
    """
    raise NotImplementedError("Member A: implement pagination + book-link extraction.")


def iter_book_links() -> Iterator[dict]:
    """Generator: yield one dict per discovered book.

    Yields:
        {"book_url": str, "source_category": str}

    The orchestrator will then fetch each book_url itself and pass the HTML to
    parser.parse_book(). Keep this function lazy (yield, don't return a list) so
    crawling and parsing can interleave.
    """
    raise NotImplementedError("Member A: implement top-level iterator over all categories.")
