from __future__ import annotations

import json
import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup


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


if __name__ == "__main__":
    html_path = __file__.replace("scraw_amazon.py", "find_fields.html")
    try:
        html_content = _read_file(html_path)
    except FileNotFoundError:
        raise SystemExit(f"Could not find HTML at {html_path}")

    result = parse_reviews(html_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))


