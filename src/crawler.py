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

import re
import time
from typing import Iterator
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.bookdelivery.com/"
REQUEST_DELAY_SEC = 3
MAX_PAGES_PER_CATEGORY = 5
USER_AGENT = "Mozilla/5.0 (compatible; HUJI-67978-HW1-crawler/1.0)"

_SESSION = requests.Session()
_SESSION.headers.update(
    {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get(url: str) -> str:
    """Fetch `url` and return the response body as text.

    Sends a real User-Agent header, retries on transient failures (5xx /
    connection errors) with up to 2 retries, and sleeps REQUEST_DELAY_SEC
    before each request (politeness).  Raises on permanent failure.
    """
    max_retries = 2
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        time.sleep(REQUEST_DELAY_SEC)
        try:
            response = _SESSION.get(url, timeout=20)
            if response.status_code < 500:
                response.raise_for_status()
                return response.text
            # 5xx — treat as transient and retry
            last_exc = requests.HTTPError(
                f"Server error {response.status_code} for {url}", response=response
            )
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc

        if attempt < max_retries:
            backoff = 2 ** (attempt + 1)
            print(f"[crawler] Transient error on {url!r}, retrying in {backoff}s …")
            time.sleep(backoff)

    raise RuntimeError(f"[crawler] Permanent failure fetching {url!r}") from last_exc


def get_category_links(homepage_html: str) -> list[tuple[str, str]]:
    """Parse the homepage HTML and return every top-level category link.

    Returns:
        A list of (category_name, category_absolute_url) tuples.
        Example: [("Art", "https://www.bookdelivery.com/…/books/art"), ...]

    Strategy:
      1. Look for the main navigation / category menu (common containers).
      2. Collect all <a> tags whose href matches the category-URL pattern.
      3. Exclude links that look like book pages, author pages, or publisher pages.
    """
    soup = BeautifulSoup(homepage_html, "lxml")

    # Try progressively broader containers until we find category links.
    nav_candidates = (
        soup.select("nav")
        or soup.select("[class*='categor']")
        or soup.select("[class*='menu']")
        or soup.select("[class*='nav']")
        or [soup]  # last resort: whole document
    )

    seen_hrefs: set[str] = set()
    results: list[tuple[str, str]] = []

    for container in nav_candidates:
        for tag in container.find_all("a", href=True):
            href: str = tag["href"].strip()
            absolute = urljoin(BASE_URL, href)

            if absolute in seen_hrefs:
                continue

            # Must stay on the same host
            if urlparse(absolute).netloc != urlparse(BASE_URL).netloc:
                continue

            if not _is_category_url(absolute):
                continue

            name = _clean_text(tag.get_text())
            if not name:
                continue

            seen_hrefs.add(absolute)
            results.append((name, absolute))

        if results:
            break

    if not results:
        raise RuntimeError(
            "[crawler] No category links found on the homepage. "
            "Inspect the homepage HTML and update _is_category_url() / the nav selector."
        )

    return results


def get_book_links_from_category(category_url: str) -> list[str]:
    """Walk up to MAX_PAGES_PER_CATEGORY pagination pages of `category_url`
    and return every individual book-page URL found across those pages.

    Uses get() for every fetch so the politeness delay is respected.
    """
    book_urls: list[str] = []
    current_url: str | None = category_url

    for page_num in range(1, MAX_PAGES_PER_CATEGORY + 1):
        if current_url is None:
            break

        print(f"[crawler] Fetching page {page_num}: {current_url}")
        html = get(current_url)
        soup = BeautifulSoup(html, "lxml")

        # Save the first category page for local-first development
        if page_num == 1:
            _save_local(html, "local_category_page.html")

        page_books = _extract_book_links(soup, current_url)
        book_urls.extend(page_books)
        print(f"[crawler]   Found {len(page_books)} book links on page {page_num}")

        current_url = _next_page_url(soup, current_url)

    return list(dict.fromkeys(book_urls))  # preserve order, deduplicate


def iter_book_links() -> Iterator[dict]:
    """Generator: yield one dict per discovered book.

    Yields:
        {"book_url": str, "source_category": str}
    """
    print("[crawler] Fetching homepage …")
    homepage_html = get(BASE_URL)
    _save_local(homepage_html, "local_homepage.html")

    categories = get_category_links(homepage_html)
    print(
        f"[crawler] Discovered {len(categories)} top-level categories: "
        f"{[name for name, _ in categories]}"
    )

    for category_name, category_url in categories:
        print(f"[crawler] === Category: {category_name!r} — {category_url}")
        book_urls = get_book_links_from_category(category_url)
        print(f"[crawler] {len(book_urls)} book URLs in {category_name!r}")

        for book_url in book_urls:
            yield {"book_url": book_url, "source_category": category_name}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _is_category_url(url: str) -> bool:
    """Return True if `url` looks like a category/genre listing page.

    Bookdelivery.com URL patterns observed:
      Book pages  : …/book-{slug}/{isbn}/p/{id}
      Author pages: …/books/author/{slug}
      Publisher   : …/books/publisher/{slug}
      Categories  : …/books/{category-slug}  OR  …/categoria/{slug}
                    OR  …/books/subject/{slug}

    We accept paths with a category-like segment and reject known non-category paths.
    """
    path = urlparse(url).path.lower()

    exclude_patterns = [
        r"/book-",            # individual book page
        r"/books/author",     # author listing
        r"/books/publisher",  # publisher listing
        r"/p/\d+",            # product page by ID
        r"/cart",
        r"/checkout",
        r"/login",
        r"/register",
        r"/search",
        r"/account",
        r"\.(pdf|jpg|png|gif)$",
    ]
    if any(re.search(pat, path) for pat in exclude_patterns):
        return False

    include_patterns = [
        r"/books/",
        r"/categoria",
        r"/subject/",
        r"/genre/",
        r"/category/",
    ]
    return any(re.search(pat, path) for pat in include_patterns)


def _extract_book_links(soup: BeautifulSoup, page_url: str) -> list[str]:
    """Return all book-page URLs found in `soup`.

    A link is considered a book page when its path contains '/book-' AND '/p/'
    followed by a numeric ID — the pattern observed in bookdelivery.com URLs.
    """
    book_urls: list[str] = []
    for tag in soup.find_all("a", href=True):
        href: str = tag["href"].strip()
        absolute = urljoin(page_url, href)
        path = urlparse(absolute).path
        if re.search(r"/book-", path) and re.search(r"/p/\d+", path):
            book_urls.append(absolute)
    return book_urls


def _next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    """Return the URL of the next pagination page, or None on the last page.

    Tries several common pagination patterns in order:
      1. <a rel="next">
      2. <a> whose visible text is "Next" / "›" / "»" / "Siguiente" etc.
      3. <li class="next"> or <span class="next"> containing an <a>
      4. Increment the numeric /page/N segment in the current URL path
    """
    # 1. rel="next" — most reliable
    rel_next = soup.find("a", rel=lambda v: v and "next" in v)
    if rel_next and rel_next.get("href"):
        return urljoin(current_url, rel_next["href"])

    # 2. Text-based next link
    next_texts = {"next", "›", "»", ">", "siguiente", "next page"}
    for tag in soup.find_all("a", href=True):
        if _clean_text(tag.get_text()).lower() in next_texts:
            return urljoin(current_url, tag["href"])

    # 3. Container element with "next" in its class
    next_wrapper = soup.find(
        lambda t: t.name in {"li", "span", "div"}
        and "next" in " ".join(t.get("class", [])).lower()
    )
    if next_wrapper:
        inner_a = next_wrapper.find("a", href=True)
        if inner_a:
            return urljoin(current_url, inner_a["href"])

    # 4. Increment /page/N in path
    parsed = urlparse(current_url)
    path_match = re.search(r"(/page/)(\d+)", parsed.path)
    if path_match:
        next_n = int(path_match.group(2)) + 1
        new_path = (
            parsed.path[: path_match.start(2)]
            + str(next_n)
            + parsed.path[path_match.end(2):]
        )
        return parsed._replace(path=new_path).geturl()

    return None


def _clean_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _save_local(html: str, filename: str) -> None:
    """Persist HTML to disk for local-first development / debugging."""
    import pathlib

    out = pathlib.Path("local_samples") / filename
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[crawler] Saved {out}")
