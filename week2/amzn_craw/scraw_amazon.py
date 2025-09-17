from __future__ import annotations

import json
import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup
import requests

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
    # 'session-token': 'aSs9oJtdUTmyiOmFFjnNkTHjzHG+ANW6i2r9quUP9goaHZYKRIyADvipxK6lUXc1MXmwZ8eXfa3bb3BAxnEZoUIO+8Q3Sj6tw2nuH88eHYbLK+qdW/6B989Q8nkM+aW2X+osRFAADD1EJA9lvbQyi3BrxYxlQeHwoDVw1OV8pTrpPmI8kcZ32jyQn1fe69SpqiQk7S1YSsxIx3PNQ+iMFjlouxqPLMWGZY/UqE27qH8dJt3usJ1ekezkbB8gVnE3byC5uc8zfuNg3++YxaT+R/yhglR3FT5oR94PfDnglLhoaEkdnfLWQLqdf7R+xFcoFg5xQ2eoq+mZ106OSKNsKB8J8RfsYDlnsjPz8Akmfq4/gtDOLodF5kXzJcHfeaEg',
    'x-main': '"RK3HFyysOzrv?SfUy4SdzHQj5f0UJQ6a3wA20@DhfNgcx9hFX8N@rrGgIvPmK6Fz"',
    # 'csm-hit': 'tb:RFT6GNRWBV1F2VQ5TWPY+s-0F5Q5D7VNZD1DTB4HNMD|1758076044776&t:1758076044776&adb:adblk_no',
    # 'rxc': 'ANseot5iPcxw2MGTr2A',
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
    # 'pageSize': '10',
    'asin': ASIN,
    # 'scope': 'reviewsAjax5',
}


def _extract_text_with_br(span: BeautifulSoup) -> str:
    # Preserve <br/> as literal tags in output as shown in instructions
    texts: List[str] = []
    for child in span.children:
        if getattr(child, "name", None) == "br":
            texts.append("<br/>")
        else:
            texts.append(str(child).strip())
    return "".join(texts).strip()


def parse_reviews(html: str) -> tuple[List[Dict[str, Any]], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    reviews: List[Dict[str, Any]] = []

    # Extract lazyWidgetCsrfToken from the full HTML
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

    return reviews, token


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fetch_reviews_and_token(
    asin: str,
    cookies: Dict[str, str],
    headers: Dict[str, str],
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
    response = requests.get(url, cookies=cookies, headers=headers)
    html = response.text
    reviews, token = parse_reviews(html)
    return reviews, token


if __name__ == "__main__":
    reviews, token = fetch_reviews_and_token(ASIN, COOKIES, HEADERS_STATIC, PARAMS)
    print(json.dumps(reviews, ensure_ascii=False, indent=2))
    print(token)




    # This constructs the path to the HTML file by replacing the current Python file name
    # with "find_fields.html" in the same directory. If this file is 
    # "week2/amzn_craw/scraw_amazon.py", it becomes "week2/amzn_craw/find_fields.html"
    # html_path = __file__.replace("scraw_amazon.py", "find_fields.html")
    # try:
    #     html_content = _read_file(html_path)
    # except FileNotFoundError:
    #     raise SystemExit(f"Could not find HTML at {html_path}")

    # result = parse_reviews(html_content)
    # print(json.dumps(result, ensure_ascii=False, indent=2))


