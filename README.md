# HW1 — Bookdelivery.com Crawler

Course 67978 (A Needle in a Data Haystack), Homework 1 (practical part).
Target site: <https://www.bookdelivery.com/>.

See [`plan.md`](plan.md) for the full work split between the three team members.

## Project layout
```
homework/
├── README.md              # this file
├── plan.md                # work split + shared interface contract
├── requirements.txt       # Python dependencies
├── HW1_67978_2026.pdf     # assignment
├── src/                   # source code
│   ├── books_crawler.py   # orchestrator (entry point)
│   ├── crawler.py         # Member A — fetching, pagination, book links
│   ├── parser.py          # Member B — per-book HTML → flat dict
│   └── processing.py      # Member C — DataFrame, outputs, stats, PDF, ZIP
└── output/                # generated CSV/JSON/PDF artifacts (created at run time)
```

## Module ownership
| Module | Owner |
| --- | --- |
| `crawler.py` | Member A — fetching, category discovery, pagination, book-link iterator |
| `parser.py` | Member B — per-book HTML → flat dict (19 fields), rounding rules, missing-field omission |
| `processing.py` | Member C — DataFrame, CSV/JSON outputs, stats, PDF report, ZIP packaging |
| `books_crawler.py` | Shared orchestrator — wires A → B → C |

Each module has function signatures with docstrings describing what to implement.
Replace every `raise NotImplementedError(...)` with real code.

## Run
```bash
pip install -r requirements.txt
python -m src.books_crawler
```
