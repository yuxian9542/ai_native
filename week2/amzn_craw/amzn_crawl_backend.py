from __future__ import annotations

import json
import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup
import requests
import sys
import logging
import os
from datetime import datetime
from pathlib import Path

COOKIES = {
    'ubid-main': '135-9735178-2965835',
    # 'aws-target-data': '%7B%22support%22%3A%221%22%7D',
    # 'regStatus': 'registered',
    'session-id': '130-8483115-7485730',
    # 'remember-account': 'true',
    # 'aws-userInfo': '%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D',
    # 'i18n-prefs': 'USD',
    # 'lc-main': 'en_US',
    # 'kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent': 'general=in',
    # 'kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity': 'CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=',
    # 'aws-target-visitor-id': '1717359572436-390315.44_0',
    # 'AMCV_7742037254C95E840A4C98A6%40AdobeOrg': '1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0',
    # 'csd-key': 'eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==',
    # 'skin': 'noskin',
    'at-main': 'Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw',
    # 'sess-at-main': '"nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="',
    # 'sst-main': 'Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo',
    # 'session-id-time': '2082787201l',
    # 'session-token': 'Lu+1WqzQqBHHuY7fDKfOd3lO1gU8vKyUX2r1kuyDKYHk65HPyIXoKLXIhT+RzuKpKs7HfM2Kwn4fPmXSxJifadf3RrH+TfwT2OAmKV6JGfBZEant+X+2r0AkH4k6NIWkPRltGK+K0ERP1+QW70s5tG5GAyQBqFs4UiTke/fb2dRSXwrXIqrDO4Ywf/VO8Dj0SeRQnKe8VWuL1Q3hiqlL98l7cukl5GY/5NtiTWur9DPncdk/3sRvtTLqwebmaN/ecIhTCRmFHcHL1eBg63CnYmhea12v+vSJ0ZwGxQbSd7GEF9WRr26zNdXhqym5+al7cXQF1edArGrz2BL3RMuJ9oYu2tNnBrC4BwIhtFI9ioOaat2ctzn3WuNNTRvondOS',
    'x-main': '"FCGUifN3OOc?xu@tM2NSiNhgceYFqkDaHi4kdBwcbHf6PZyKUVbD92StspEuskMn"',
    # 'csm-hit': 'tb:VGAR7XXNB25ZESTV5WF0+s-TXY9AWEA3G5FWA9RP8Y3|1758114377835&t:1758114377835&adb:adblk_no',
    # 'rxc': 'ANseot52k8xw2MGTr2A',
}

HEADERS_STATIC = {
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # 'accept-language': 'en-US,en;q=0.9',
    # 'cache-control': 'no-cache',
    # 'device-memory': '8',
    # 'downlink': '10',
    # 'dpr': '1.5',
    # 'ect': '4g',
    # 'pragma': 'no-cache',
    # 'priority': 'u=0, i',
    # 'referer': 'https://www.amazon.com/GOKOTTA-Luxury-Derived-Cooling-Elastic/dp/B0DBPZZRGC/ref=cm_cr_arp_d_product_top?ie=UTF8&th=1',
    # 'rtt': '50',
    # 'sec-ch-device-memory': '8',
    # 'sec-ch-dpr': '1.5',
    # 'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Windows"',
    # 'sec-ch-ua-platform-version': '"19.0.0"',
    # 'sec-ch-viewport-width': '1217',
    # 'sec-fetch-dest': 'document',
    # 'sec-fetch-mode': 'navigate',
    # 'sec-fetch-site': 'same-origin',
    # 'sec-fetch-user': '?1',
    # 'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    # 'viewport-width': '1217',
    # 'cookie': 'ubid-main=135-9735178-2965835; aws-target-data=%7B%22support%22%3A%221%22%7D; regStatus=registered; session-id=130-8483115-7485730; remember-account=true; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; i18n-prefs=USD; lc-main=en_US; kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent=general=in; kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity=CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=; aws-target-visitor-id=1717359572436-390315.44_0; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==; skin=noskin; at-main=Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw; sess-at-main="nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="; sst-main=Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo; session-id-time=2082787201l; session-token=aSs9oJtdUTmyiOmFFjnNkTHjzHG+ANW6i2r9quUP9goaHZYKRIyADvipxK6lUXc1MXmwZ8eXfa3bb3BAxnEZoUIO+8Q3Sj6tw2nuH88eHYbLK+qdW/6B989Q8nkM+aW2X+osRFAADD1EJA9lvbQyi3BrxYxlQeHwoDVw1OV8pTrpPmI8kcZ32jyQn1fe69SpqiQk7S1YSsxIx3PNQ+iMFjlouxqPLMWGZY/UqE27qH8dJt3usJ1ekezkbB8gVnE3byC5uc8zfuNg3++YxaT+R/yhglR3FT5oR94PfDnglLhoaEkdnfLWQLqdf7R+xFcoFg5xQ2eoq+mZ106OSKNsKB8J8RfsYDlnsjPz8Akmfq4/gtDOLodF5kXzJcHfeaEg; x-main="RK3HFyysOzrv?SfUy4SdzHQj5f0UJQ6a3wA20@DhfNgcx9hFX8N@rrGgIvPmK6Fz"; csm-hit=tb:RFT6GNRWBV1F2VQ5TWPY+s-0F5Q5D7VNZD1DTB4HNMD|1758076044776&t:1758076044776&adb:adblk_no; rxc=ANseot5iPcxw2MGTr2A',
}

HEADERS_DYNAMIC = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
}

ASIN = 'B0DBPZZRGC'
ASIN2 = 'B0DRZSBQW3'
ASIN_NO_SEC_PAGE = 'B074NDQ143'
ASIN_NO_SEC_PAGE2 = 'B07BTRDGRM'
ASIN_NO_SEC_PAGE3 = 'B08QRT97Y8'
ASIN_LIST = ['B074NDQ143', 'B07BTRDGRM', 'B0F638S4MQ']
ASIN_LIST = [ASIN_NO_SEC_PAGE3]


DATA = {
    # 'sortBy': '',
    # 'reviewerType': 'all_reviews',
    # 'formatType': '',
    # 'mediaType': '',
    'filterByStar': '',
    # 'filterByAge': '',
    'pageNumber': '1',
    # 'filterByLanguage': '',
    # 'filterByKeyword': '',
    # 'shouldAppend': 'undefined',
    # 'deviceType': 'desktop',
    # 'canShowIntHeader': 'undefined',
    # 'reftag': 'cm_cr_getr_d_paging_btm_next_3',
    'pageSize': '10',
    # 'scope': 'reviewsAjax5',
}

STAR_MAP = {
    1: 'one_star',
    2: 'two_star',
    3: 'three_star',
    4: 'four_star',
    5: 'five_star'
}


# Simple logger configuration
logger = logging.getLogger("amzn_crawl")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(_handler)


def _mask_mapping(d: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if d is None:
        return None
    try:
        # Avoid dumping sensitive cookie/header values; show keys only
        return {"keys": list(d.keys()), "size": len(d)}
    except Exception:
        return {"repr": repr(d)}


def perform_request(method: str, url: str, *, params=None, data=None, headers=None, cookies=None, **kwargs) -> requests.Response:
    """Wrapper around requests with logging and printing.

    Logs method, url, params, data, and whether the request succeeded.
    """
    logger.info(
        "HTTP %s %s params=%s data=%s headers=%s cookies=%s",
        method,
        url,
        params,
        data,
        _mask_mapping(headers),
        _mask_mapping(cookies),
    )
    print(f"HTTP {method} {url} params={params} data={data}")
    try:
        resp = requests.request(method, url, params=params, data=data, headers=headers, cookies=cookies, **kwargs)
        logger.info("HTTP %s %s -> status=%s ok=%s len=%s", method, url, resp.status_code, resp.ok, len(resp.text))
        print(f"HTTP {method} {url} -> status={resp.status_code} ok={resp.ok}")
        return resp
    except Exception as exc:
        logger.exception("HTTP %s %s failed", method, url)
        print(f"HTTP {method} {url} failed: {exc}")
        raise


def set_run_log_file(file_path: str) -> None:
    """Attach a per-run FileHandler so each run logs to its own file.

    The file is created if missing. Existing file handlers are replaced.
    """
    # Ensure parent directory
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # Remove existing FileHandlers to avoid duplicates across runs
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            try:
                logger.removeHandler(h)
                h.close()
            except Exception:
                pass

    fh = logging.FileHandler(file_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(fh)
    logger.info("Run log file attached: %s", file_path)

def _extract_text_with_br(span: BeautifulSoup) -> str:
    # Preserve <br/> as literal tags in output as shown in instructions
    texts: List[str] = []
    for child in span.children:
        if getattr(child, "name", None) == "br":
            texts.append("<br/>")
        else:
            texts.append(str(child).strip())
    return "".join(texts).strip()


def _extract_token(text: str) -> str | None:
    for pattern in [
        r'"lazyWidgetCsrfToken"\s*:\s*"([^\"]+)"',
        r'lazyWidgetCsrfToken\s*[:=]\s*\"([^\"]+)\"',
    ]:
        m = re.search(pattern, text)
        if m:
            return m.group(1)
    return None


def _extract_reviews_from_soup(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    reviews: List[Dict[str, Any]] = []
    for li in soup.select('li[data-hook="review"]'):
        review: Dict[str, Any] = {}

        # Prefer original content if translated blocks exist; otherwise use first span or the body span itself
        body_container = li.select_one('div.review-data span[data-hook="review-body"]')
        body_span = None
        if body_container:
            body_span = body_container.select_one('.cr-original-review-content') or \
                        body_container.select_one('span') or \
                        body_container
        review["content"] = _extract_text_with_br(body_span) if body_span else ""

        star_text_el = li.select_one('i[data-hook="review-star-rating"] span.a-icon-alt')
        star_value: float | None = None
        if star_text_el and star_text_el.text:
            m = re.search(r"([0-9]+(?:\\.?[0-9]+)?)", star_text_el.text)
            if m:
                try:
                    star_value = float(m.group(1))
                except ValueError:
                    star_value = None
        review["star"] = star_value

        name_span = li.select_one('div.a-profile-content span.a-profile-name')
        review["reviewer"] = name_span.text.strip() if name_span and name_span.text else ""

        date_span = li.select_one('span[data-hook="review-date"]')
        date_value = ""
        if date_span and date_span.text:
            m = re.search(r"on\s+(.+)$", date_span.text.strip())
            date_value = m.group(1).strip() if m else date_span.text.strip()
        review["review_date"] = date_value

        avp_span = li.select_one('span[data-hook="avp-badge"]')
        review["verified_purchase"] = avp_span.text.strip() if avp_span and avp_span.text else ""

        reviews.append(review)
    return reviews


def _has_next_from_soup(soup: BeautifulSoup) -> tuple[bool, str | None, Dict[str, str] | None]:
    anchor = soup.select_one('nav#cm_cr-pagination_bar li.a-last a')
    nav = soup.select_one('nav#cm_cr-pagination_bar')
    reftag = nav.get('data-reftag') if nav else None
    has_next = bool(anchor and ("Next page" in anchor.get_text(strip=True)))

    # Also derive product info (name, image, link) if present on page
    product_name: str | None = None
    product_image: str | None = None
    product_link: str | None = None

    # Name candidates (search page title card, product page title, or product link)
    el = soup.select_one('div[data-cy="title-recipe"] h2 span')
    if el and el.text.strip():
        product_name = el.text.strip()
    elif soup.select_one('#productTitle'):
        product_name = soup.select_one('#productTitle').text.strip()
    elif soup.select_one('a[data-hook="product-link"]'):
        product_name = soup.select_one('a[data-hook="product-link"]').get_text(strip=True)

    # Image candidates
    img = soup.select_one('img.s-image') or soup.select_one('img[data-hook="cr-product-image"]') or soup.select_one('img#landingImage')
    if img and img.get('src'):
        product_image = img.get('src')

    # Link candidates
    a = soup.select_one('a.a-link-normal.s-no-outline') or soup.select_one('a[data-hook="product-link"]')
    if a and a.get('href'):
        href = a.get('href')
        if not href.startswith('http'):
            href = f'https://www.amazon.com{href}'
        product_link = href.split('&', 1)[0]

    product: Dict[str, str] | None = None
    if product_name or product_image or product_link:
        product = {
            'name': product_name or '',
            'image': product_image or '',
            'link': product_link or '',
        }

    return has_next, reftag, product


def parse_top_asins(html: str, limit: int) -> List[str]:
    """Extract top N ASINs from a search/listing HTML.

    Looks for elements like:
    <div role="listitem" data-asin="B0F3RZRQ87" ...>
    Returns a de-duplicated list in document order, capped at limit.
    """
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one('div.s-main-slot.s-result-list.s-search-results.sg-row')
    if not container:
        return []
    seen: set[str] = set()
    result: List[str] = []
    for div in container.select('div[role="listitem"][data-asin]'):
        asin = (div.get("data-asin") or "").strip()
        if not asin or asin in seen:
            continue
        result.append(asin)
        if limit != -1 and len(result) >= limit:
            break
    return result


def parse_reviews(html: str, debug: bool = False) -> tuple[List[Dict[str, Any]], str | None, bool, str | None, Dict[str, str] | None]:
    soup = BeautifulSoup(html, "html.parser")
    token = _extract_token(html)
    reviews = _extract_reviews_from_soup(soup)
    has_next, reftag, product = _has_next_from_soup(soup)

    return reviews, token, has_next, reftag, product


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_reviews_ajax(text: str, debug: bool = False) -> tuple[List[Dict[str, Any]], str | None, bool, str | None, Dict[str, str] | None]:
    """Parse reviews from Amazon AJAX response format (e.g., page_3.html).

    The response contains multiple JSON-ish chunks like:
    ["append", "#cm_cr-review_list", "<ul>...<li data-hook=\"review\">...</li>...</ul>"]
    We extract and concatenate those HTML payloads and then parse reviews similarly to parse_reviews.
    """
    token = _extract_token(text)

    # Collect HTML payloads that target the reviews list via append or update
    html_parts: List[str] = []
    
    # Updated regex to handle the massive HTML content properly
    # The key issue was the original regex was too greedy and not handling escaped quotes properly
    append_pattern = r'\[\s*"append"\s*,\s*"#cm_cr-review_list"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]'
    update_pattern = r'\[\s*"update"\s*,\s*"#cm_cr-review_list"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]'
    
    if debug:
        print(f"Searching for AJAX patterns in text of length {len(text)}")
    
    for pat in (append_pattern, update_pattern):
        matches = list(re.finditer(pat, text, re.DOTALL))
        if debug:
            print(f"Pattern found {len(matches)} matches")
        for m in matches:
            part = m.group(1)
            # Unescape JSON string properly
            part = part.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/').replace('\\\\', '\\')
            if debug:
                print(f"Found HTML part of length {len(part)}")
                print(f"First 200 chars: {part[:200]}")
            html_parts.append(part)

    combined_html = "\n".join(html_parts)
    if debug:
        print(f"Combined HTML length: {len(combined_html)}")

    soup = BeautifulSoup(combined_html, "html.parser")
    reviews = _extract_reviews_from_soup(soup)
    has_next, reftag, product = _has_next_from_soup(soup)
    
    # Fallback: if no reviews found but raw <li data-hook="review"> blocks exist in text, extract via regex
    if not reviews:
        li_blocks = re.findall(r"<li[^>]*data-hook=\"review\"[\s\S]*?</li>", combined_html or text)
        if debug:
            print(f"Fallback found {len(li_blocks)} li blocks")
        if li_blocks:
            soup_alt = BeautifulSoup("\n".join(li_blocks), "html.parser")
            reviews = _extract_reviews_from_soup(soup_alt)
    
    return reviews, token, has_next, reftag, product

from typing import List, Dict, Any  # already imported at top

def extract_reviews_from_ajax_text(text: str) -> List[Dict[str, Any]]:
    reviews, _token, _has_next, _reftag, _product = parse_reviews_ajax(text, debug=False)
    return reviews

def extract_reviews_from_ajax_file(file_path: str) -> List[Dict[str, Any]]:
    text = _read_file(file_path)
    return extract_reviews_from_ajax_text(text)

def _print_reviews(reviews: List[Dict[str, Any]]) -> None:
    print(f"Found {len(reviews)} reviews")
    for i, r in enumerate(reviews, 1):
        print(
            f"{i}) reviewer={r.get('reviewer','')} "
            f"star={r.get('star','')} "
            f"date={r.get('review_date','')} "
            f"verified={r.get('verified_purchase','')} "
            f"body={r.get('content','')}"
        )


def fetch_reviews_and_token(
    url: str,
    cookies: Dict[str, str],
    headers: Dict[str, str],
    data: Dict[str, str],
    post: bool,
    params: Dict[str, str] = None,
    debug: bool = False,
) -> tuple[List[Dict[str, Any]], str | None, bool, str | None, Dict[str, str] | None]:
    """Fetch a reviews page (GET or POST) and parse reviews, token, and next-page flag."""
    try:
        if not post:
            response = perform_request('GET', url, cookies=cookies, headers=headers, params=params)
        else:
            response = perform_request('POST', url, cookies=cookies, headers=headers, data=data)
    except Exception as e:
        # Return empty result on failure while preserving return arity
        return [], None, False, None, None
    html = response.text
    if not post:
        reviews, found_token, has_next, reftag, product = parse_reviews(html, debug=debug)
    else:
        reviews, found_token, has_next, reftag, product = parse_reviews_ajax(html, debug=debug)
        reftag = None
    return reviews, found_token, has_next, reftag, product


def search_prod(search_term, num_result, debug=False):
    if debug:
        return ASIN_LIST
    url = 'https://www.amazon.com/s/ref=nb_sb_noss_1'
    params = {
        'field-keywords': search_term,
    }
    response = perform_request('GET', url, params=params, cookies=COOKIES, headers=HEADERS_STATIC)
    html = response.text
    asins = parse_top_asins(html, num_result)
    return asins


def amzn_review_main(search_term: str, num_result: int = 3, star: int | None = None, total_pages: int = 2, debug=False) -> Dict[str, List[Dict[str, Any]]]:
    asins = search_prod(search_term, num_result, debug=debug)
    ref_static = 'cm_cr_dp_d_show_all_btm' if star is None else 'cm_cr_unknown'
    params = None if star is None else {'filterByStar': STAR_MAP[star]}

    results: Dict[str, List[Dict[str, Any]]] = {}

    for asin in asins:
        print(f'asin={asin}')
        url_static = f"https://www.amazon.com/product-reviews/{asin}/ref={ref_static}"
        url_dynamic = ''
        headers = dict(HEADERS_STATIC)
        data = dict(DATA)
        data['asin'] = asin
        if star is not None:
            data['filterByStar'] = STAR_MAP[star]

        asin_reviews: List[Dict[str, Any]] = []
        for page_num in range(1, total_pages + 1):
            post = page_num > 1
            url = url_static if not post else (url_dynamic + str(page_num))

            if not post:
                reviews, token, has_next, _reftag, _product = fetch_reviews_and_token(
                    url=url,
                    cookies=COOKIES,
                    headers=headers,
                    data=data,
                    post=False,
                    params=params,
                )
                if token:
                    headers['anti-csrftoken-a2z'] = token
 

            else:
                url_dynamic_prefix = f'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref={_reftag}'
                url_dynamic = url_dynamic_prefix + '_next_' + str(page_num)
                url = url_dynamic
                data['pageNumber'] = str(page_num)
                reviews, token, has_next, _reftag, _ = fetch_reviews_and_token(
                    url=url,
                    cookies=COOKIES,
                    headers=headers,
                    data=data,
                    post=True,
                )


            asin_reviews.extend(reviews)
            if not has_next:
                break
        results[asin] = {}
        results[asin]['comments'] = asin_reviews
        results[asin]['product'] = _product
    logger.info([(i, len(results[i]['comments']), results[i]['product']) for i in results])
    return results



def extract_reviews_from_jax_file(file_path: str) -> List[Dict[str, Any]]:
    """Extract reviews from a .jax file containing Amazon review HTML/AJAX data.
    
    Args:
        file_path: Path to the .jax file
        
    Returns:
        List of review dictionaries with keys: reviewer, star, review_date, verified_purchase, content
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try AJAX parsing first with debug enabled
    reviews, _, _, _, _ = parse_reviews_ajax(content, debug=True)
    
    if not reviews:
        # Fall back to regular HTML parsing
        soup = BeautifulSoup(content, 'html.parser')
        reviews = _extract_reviews_from_soup(soup)
    
    return reviews


def test_extract_reviews():
    """Test function to extract and display reviews from test.jax"""
    import os
    from pathlib import Path
    
    # Get the test file path
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    test_file = current_dir.parent / "test.jax"
    
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return
    
    # Extract reviews
    reviews = extract_reviews_from_jax_file(str(test_file))
    
    # Display results
    print(f"\n=== EXTRACTED {len(reviews)} REVIEWS FROM {test_file.name} ===\n")
    
    for i, review in enumerate(reviews, 1):
        print(f"Review #{i}:")
        print(f"  Reviewer: {review.get('reviewer', 'N/A')}")
        print(f"  Rating: {review.get('star', 'N/A')} stars")
        print(f"  Date: {review.get('review_date', 'N/A')}")
        print(f"  Verified: {review.get('verified_purchase', 'N/A')}")
        print(f"  Content: {review.get('content', 'N/A')[:100]}...")
        print()
    
    return reviews


# ... existing code ...

if __name__ == "__main__":
    # ... existing code ...
    
    # Test the extraction function
    # test_extract_reviews()

    # Create a per-run log file similar to frontend naming
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    output_dir = current_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = output_dir / f"results_{ts}.log"
    set_run_log_file(str(log_file))

    response = amzn_review_main('bed', total_pages=2, debug=True)
    print([(i, len(response[i]['comments'])) for i in response])