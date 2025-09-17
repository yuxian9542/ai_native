from __future__ import annotations

import json
import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup
import requests


def _extract_text_with_br(span: BeautifulSoup) -> str:
    # Preserve <br/> as literal tags in output as shown in instructions
    texts: List[str] = []
    for child in span.children:
        if getattr(child, "name", None) == "br":
            texts.append("<br/>")
        else:
            texts.append(str(child).strip())
    return "".join(texts).strip()


def parse_reviews(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    reviews: List[Dict[str, Any]] = []

    for li in soup.select('li[data-hook="review"]'):
        review: Dict[str, Any] = {}

        # content
        body_span = li.select_one('div.review-data span[data-hook="review-body"] span')
        if body_span:
            review["content"] = _extract_text_with_br(body_span)
        else:
            review["content"] = ""

        # star -> extract float from e.g. "5.0 out of 5 stars"
        star_text_el = li.select_one('i[data-hook="review-star-rating"] span.a-icon-alt')
        star_value: float | None = None
        if star_text_el and star_text_el.text:
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)", star_text_el.text)
            if m:
                try:
                    star_value = float(m.group(1))
                except ValueError:
                    star_value = None
        review["star"] = star_value

        # reviewer name
        name_span = li.select_one('div.a-profile-content span.a-profile-name')
        review["reviewer"] = name_span.text.strip() if name_span and name_span.text else ""

        # review_date -> e.g. "Reviewed in the United States on August 2, 2025" => "August 2, 2025"
        date_span = li.select_one('span[data-hook="review-date"]')
        date_value = ""
        if date_span and date_span.text:
            m = re.search(r"on\s+(.+)$", date_span.text.strip())
            date_value = m.group(1).strip() if m else date_span.text.strip()
        review["review_date"] = date_value

        # verified purchase -> presence of span[data-hook="avp-badge"] with text "Verified Purchase"
        avp_span = li.select_one('span[data-hook="avp-badge"]')
        review["verified_purchase"] = avp_span.text.strip() if avp_span and avp_span.text else ""

        reviews.append(review)

    return reviews


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fetch_reviews_and_token(
    asin: str,
    cookies: Dict[str, str],
    headers: Dict[str, str],
    params: Dict[str, str],
) -> tuple[List[Dict[str, Any]], str | None]:
    """Fetch product reviews page and return (parsed_reviews, lazyWidgetCsrfToken).

    Performs:
    response = requests.get(
        f'https://www.amazon.com/product-reviews/{ASIN}/ref=cm_cr_dp_d_show_all_btm',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    Then parses response.text via parse_reviews and extracts lazyWidgetCsrfToken.
    """
    url = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm"
    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    html = response.text

    token: str | None = None
    token_patterns = [
        r'"lazyWidgetCsrfToken"\s*:\s*"([^"]+)"',
        r'lazyWidgetCsrfToken\s*[:=]\s*\"([^\"]+)\"',
    ]
    for pattern in token_patterns:
        m = re.search(pattern, html)
        if m:
            token = m.group(1)
            break

    return parse_reviews(html), token


if __name__ == "__main__":
    # This constructs the path to the HTML file by replacing the current Python file name
    # with "find_fields.html" in the same directory. If this file is 
    # "week2/amzn_craw/scraw_amazon.py", it becomes "week2/amzn_craw/find_fields.html"
    html_path = __file__.replace("scraw_amazon.py", "find_fields.html")
    try:
        html_content = _read_file(html_path)
    except FileNotFoundError:
        raise SystemExit(f"Could not find HTML at {html_path}")

    result = parse_reviews(html_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))


