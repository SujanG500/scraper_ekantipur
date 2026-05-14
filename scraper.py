
import json
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# ─── Helpers ────────────────────────────────────────────────────────────────

def absolute_url(base: str, href) -> str | None:
    """Return a full URL; resolve relative paths against the base domain."""
    if not href:
        return None
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base.rstrip("/") + href
    return href


def safe_text(el, selector=None):
    """Safely extract trimmed text from an element or a child via selector."""
    try:
        target = el.query_selector(selector) if selector else el
        if target is None:
            return None
        text = target.text_content()
        return text.strip() if text else None
    except Exception:
        return None


def safe_attr(el, selector, attr: str):
    """Safely get an HTML attribute from an element or child matched by selector."""
    try:
        target = el.query_selector(selector) if selector else el
        if target is None:
            return None
        return target.get_attribute(attr)
    except Exception:
        return None


# ─── Task 1: Entertainment News ─────────────────────────────────────────────

def extract_entertainment_news(page, base_url: str) -> list:
    """
    Navigate to /entertainment and return the top 5 articles.

    Confirmed selectors (from real HTML dump of ekantipur.com/entertainment):
      - Article cards : .category-inner-wrapper  (30 found on page)
      - Title         : h2 a  (text content)
      - Image         : img.loaded → src  (fully loaded CDN URL)
      - Author        : .author-name a  (text content)
      - Category      : .category-name a  (page-level label, e.g. "मनोरञ्जन")
    """
    print("[1/2] Navigating to Entertainment section...")

    page.goto(f"{base_url}/entertainment", wait_until="domcontentloaded", timeout=30000)

    try:
        page.wait_for_selector(".category-inner-wrapper", timeout=15000)
    except PlaywrightTimeoutError:
        print("   Warning: timed out waiting for article cards")

    page.wait_for_timeout(2000)

    # Page-level category label — same for every article on this section page
    category = safe_text(page.query_selector(".category-name a")) or "मनोरञ्जन"
    print(f"   Category: {category}")

    cards = page.query_selector_all(".category-inner-wrapper")
    print(f"   Found {len(cards)} article cards — extracting top 5...")

    articles = []
    for card in cards[:5]:
        title = safe_text(card, "h2 a")

        # img.loaded = already rendered; fall back to data-src for lazy images
        image_url = (
            safe_attr(card, "img.loaded", "src")
            or safe_attr(card, "img", "data-src")
            or safe_attr(card, "img", "src")
        )
        image_url = absolute_url(base_url, image_url)

        author = safe_text(card, ".author-name a") or None

        articles.append({
            "title": title,
            "image_url": image_url,
            "category": category,
            "author": author,
        })
        print(f"   ✓ {(title or 'N/A')[:70]}")

    return articles


# ─── Task 2: Cartoon of the Day ─────────────────────────────────────────────

def extract_cartoon_of_the_day(page, base_url: str) -> dict:
    """
    Extract the most recent cartoon from ekantipur.com/cartoon.

    Confirmed selectors (from real HTML dump of ekantipur.com/cartoon):
      - Cards         : .cartoon-wrapper  (one per cartoon)
      - Image         : img.loaded → src   (recent ones, fully loaded)
                        img.lazy  → data-src (older ones, lazy loaded)
      - Title         : img alt attribute  (e.g. "गजब छ बा")
      - Author        : .cartoon-description p — text AFTER " - "
                        e.g. "गजब छ बा! - अविन" → author = "अविन"
                        If nothing after " - ", author is null
      - Date          : .cartoon-description .date p (Nepali date, informational)
    """
    print("[2/2] Extracting Cartoon of the Day...")

    page.goto(f"{base_url}/cartoon", wait_until="domcontentloaded", timeout=30000)

    try:
        page.wait_for_selector(".cartoon-wrapper", timeout=15000)
    except PlaywrightTimeoutError:
        print("   Warning: timed out waiting for cartoon cards")

    page.wait_for_timeout(2000)

    # First card = most recent cartoon
    card = page.query_selector(".cartoon-wrapper")

    if not card:
        print("   ✗ No cartoon card found")
        return {"title": None, "image_url": None, "author": None}

    # Image: try img.loaded first (already rendered), then img.lazy (data-src)
    image_url = safe_attr(card, "img.loaded", "src")
    if not image_url:
        image_url = safe_attr(card, "img.lazy", "data-src")
    if not image_url:
        image_url = safe_attr(card, "img", "src") or safe_attr(card, "img", "data-src")
    image_url = absolute_url(base_url, image_url)

    # Title: from the img alt attribute (e.g. "गजब छ बा")
    title = safe_attr(card, "img", "alt") or None
    if title:
        title = title.strip() or None

    # Author: the .cartoon-description <p> contains "गजब छ बा! - अविन"
    # Split on " - " and take the part after it; return None if blank
    desc_text = safe_text(card, ".cartoon-description p")
    author = None
    if desc_text and " - " in desc_text:
        after_dash = desc_text.split(" - ", 1)[1].strip()
        author = after_dash if after_dash else None

    print(f"   ✓ Title:  {title}")
    print(f"   ✓ Author: {author}")
    print(f"   ✓ Image:  {image_url}")

    return {
        "title": title,
        "image_url": image_url,
        "author": author,
    }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    BASE_URL = "https://ekantipur.com"
    OUTPUT_FILE = "output.json"

    with sync_playwright() as p:
        # Set headless=False to watch the browser run while debugging
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            extra_http_headers={"Accept-Language": "ne,en;q=0.9"},
        )
        page = context.new_page()

        entertainment_news = extract_entertainment_news(page, BASE_URL)
        cartoon = extract_cartoon_of_the_day(page, BASE_URL)

        browser.close()

    output = {
        "entertainment_news": entertainment_news,
        "cartoon_of_the_day": cartoon,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False keeps Devanagari (Nepali) characters readable
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! Saved to '{OUTPUT_FILE}'")
    print(f"   Entertainment articles : {len(entertainment_news)}")
    print(f"   Cartoon of the Day     : {'✓' if cartoon['image_url'] else '✗'}")


if __name__ == "__main__":
    main()
