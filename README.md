# Ekantipur Scraper

A Playwright automation script that extracts structured data from [ekantipur.com](https://ekantipur.com) — Nepal's leading news website.

Built as part of the **Audio Bee** Data Extraction Intern practical assessment.

---

## What it extracts

- **Top 5 Entertainment news articles** from the मनोरञ्जन section
  - Title, image URL, category, author
- **Cartoon of the Day** (ग्यात्र)
  - Title, image URL, cartoonist name

---

## Project structure

```
ekantipur-scraper/
├── scraper.py        # Main Playwright automation script
├── output.json       # Extracted data (generated on run)
├── prompts.txt       # AI prompts used during development
├── pyproject.toml    # Project config and dependencies (uv)
├── uv.lock           # Locked dependency versions (auto-generated)
└── README.md         # This file
```

---

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

---

## Setup

### 1. Install uv

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install dependencies

```bash
uv add playwright
uv run playwright install chromium
```

### 3. Run the scraper

```bash
uv run python scraper.py
```

This generates `output.json` in the project root.

---

## Output format

```json
{
  "entertainment_news": [
    {
      "title": "Article headline here",
      "image_url": "https://ekantipur.com/uploads/...",
      "category": "मनोरञ्जन",
      "author": "Author Name or null"
    }
  ],
  "cartoon_of_the_day": {
    "title": "ग्यात्र caption",
    "image_url": "https://ekantipur.com/uploads/...",
    "author": "Cartoonist Name"
  }
}
```

---

## Debugging tips

- Set `headless=False` in `scraper.py` to watch the browser run live
- Use `page.pause()` to open the Playwright inspector mid-run
- Use `page.screenshot(path="debug.png")` to capture the page state
- Print `element.inner_html()` to inspect the raw HTML of a selected element

---

## Tech stack

- [Playwright for Python](https://playwright.dev/python/) — browser automation
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
