import requests

""" comment https://www.amazon.com/product-reviews/B0DBPZZRGC/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2 by karen m
search string: Best sheets we have ever had. Worth the high cost. """
# cookies does not change in comments of the same product on diff pages, x-main changes on diff products, but interchangeable between products
cookies = {
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
    # 'session-token': 'AOdG0ynfUF2/pcvE81EfFT9LkSyZDukz0Dqy9Bp/OM6vP/6jvIGPe0JVQ8Q35SQZLrZMhE7nAbPuX7vUSvTK+XQdH8Ecy7bV+Ay1ZETV7qj+Gbb1uxU5vNagIW5rHuToUr9+Chw9B2RlROospjvV4pTEU2bKRme2RpemjkZW7/wXp5DMtxYggrRQ7L9FO63H0j/vK5h4dBVuyJwRA2r3yZR3tbiozKnEJbBxsAc82sXRB830t7+BGKb0QTqYirkogeBAPBRs12sb7CUiWSW+eBcDD7va4q8WCihG6rij4+VRfkdKmOvdnG2MytXQifbhBlEWhUMa0lXym/jOSo1w1sBIUK3ZCvmTCf6kwm27iGfvxnvMd4voGiFI9Cq7pHe6',
    # this one changes on diff products
    'x-main': '"GNs2Rj7umoQel@v2B6xyElY@0tv8YsraJxEwQ9B772Se4drMiswbbK@mB?QOQI07"',
    # 'csm-hit': 'tb:s-RWTN3N4WGHSDPPZT16CN|1758025305778&t:1758025305873&adb:adblk_no',
    # 'rxc': 'ANseot6vd89w2MGTr2A',
}


headers = {
    # 'accept': 'text/html,*/*',
    # 'accept-language': 'en-US,en;q=0.9',
    'anti-csrftoken-a2z': 'hHaerDfRdIGFQHCPNU9hUol1XTr5orlt4M0d%2BJAR4wEDAAAAAGjJVlkAAAAB',
    # 'cache-control': 'no-cache',
    # 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    # 'device-memory': '8',

    # 'downlink': '10',
    # 'dpr': '1.5',
    # 'ect': '4g',
    # 'origin': 'https://www.amazon.com',
    # 'pragma': 'no-cache',
    # 'priority': 'u=1, i',
    # 'referer': 'https://www.amazon.com/product-reviews/B0DBPZZRGC/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews',
    # 'rtt': '0',

    # 'sec-ch-device-memory': '8',
    # 'sec-ch-dpr': '1.5',
    # 'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Windows"',
    # 'sec-ch-ua-platform-version': '"19.0.0"',
    # 'sec-ch-viewport-width': '1217',

    # 'sec-fetch-dest': 'empty',
    # 'sec-fetch-mode': 'cors',
    # 'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    # 'viewport-width': '1217',
    # 'x-requested-with': 'XMLHttpRequest',
    # 'cookie': 'ubid-main=135-9735178-2965835; aws-target-data=%7B%22support%22%3A%221%22%7D; regStatus=registered; session-id=130-8483115-7485730; remember-account=true; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; i18n-prefs=USD; lc-main=en_US; kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent=general=in; kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity=CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=; aws-target-visitor-id=1717359572436-390315.44_0; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==; skin=noskin; at-main=Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw; sess-at-main="nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="; sst-main=Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo; session-id-time=2082787201l; session-token=AOdG0ynfUF2/pcvE81EfFT9LkSyZDukz0Dqy9Bp/OM6vP/6jvIGPe0JVQ8Q35SQZLrZMhE7nAbPuX7vUSvTK+XQdH8Ecy7bV+Ay1ZETV7qj+Gbb1uxU5vNagIW5rHuToUr9+Chw9B2RlROospjvV4pTEU2bKRme2RpemjkZW7/wXp5DMtxYggrRQ7L9FO63H0j/vK5h4dBVuyJwRA2r3yZR3tbiozKnEJbBxsAc82sXRB830t7+BGKb0QTqYirkogeBAPBRs12sb7CUiWSW+eBcDD7va4q8WCihG6rij4+VRfkdKmOvdnG2MytXQifbhBlEWhUMa0lXym/jOSo1w1sBIUK3ZCvmTCf6kwm27iGfvxnvMd4voGiFI9Cq7pHe6; x-main="GNs2Rj7umoQel@v2B6xyElY@0tv8YsraJxEwQ9B772Se4drMiswbbK@mB?QOQI07"; csm-hit=tb:s-RWTN3N4WGHSDPPZT16CN|1758025305778&t:1758025305873&adb:adblk_no; rxc=ANseot6vd89w2MGTr2A',
}

data = {
    'sortBy': '',
    'reviewerType': 'all_reviews',
    'formatType': '',
    'mediaType': '',
    'filterByStar': '',
    'filterByAge': '',
    'pageNumber': '2',
    'filterByLanguage': '',
    'filterByKeyword': '',
    'shouldAppend': 'undefined',
    'deviceType': 'desktop',
    'canShowIntHeader': 'undefined',
    'reftag': 'cm_cr_arp_d_paging_btm_next_2',
    'pageSize': '10',
    'asin': 'B0DBPZZRGC',
    'scope': 'reviewsAjax1',
}

# response = requests.post(
#     'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_paging_btm_next_2',
#     cookies=cookies,
#     headers=headers,
#     data=data,
# )

""" same product diff page """

cookies_same_product_page3 = {
    'ubid-main': '135-9735178-2965835',
    'aws-target-data': '%7B%22support%22%3A%221%22%7D',
    'regStatus': 'registered',
    'session-id': '130-8483115-7485730',
    'remember-account': 'true',
    'aws-userInfo': '%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D',
    'i18n-prefs': 'USD',
    'lc-main': 'en_US',
    'kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent': 'general=in',
    'kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity': 'CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=',
    'aws-target-visitor-id': '1717359572436-390315.44_0',
    'AMCV_7742037254C95E840A4C98A6%40AdobeOrg': '1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0',
    'csd-key': 'eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==',
    'skin': 'noskin',
    'at-main': 'Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw',
    'sess-at-main': '"nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="',
    'sst-main': 'Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo',
    'session-id-time': '2082787201l',
    'session-token': 'EhZuWEgH3DmUHddZARCaU+jwXe/Dub7Zys2SNQOwwHl4IBeqZUkj0w7Rysvts3qUTTc5yTbHtTCvqRG67lwk+Vo/R3mCA9ZTw3Mn55tZYOIeN/Uisav5Pj/oP/B7qk063NX4T24SDNmTYJyHabF+jKrfWomM5zRx3iSB0B9WQESf2qgM8BAxl//F2xbOhf2IJGYSt37BXGpW5kmIJ87sJOSsl1IFXIykuQYpaMrEQLg8E7r/tzw7CC8B5amor71WSCRg8L2WhAqmqE8Xrqf492eQdgpKNV0PSvMftT3/O8Sy0+bapWUGwu67tPpaqB/9ksfZlIKYIlcPxqC3rk2Nf9KbIx1zux1YJPYNuv1h4HBl9q3NZ+QV53inWiKBtFYU',
    'x-main': '"xgK1a0Wb3Az?dpzoCJZjKi8YvMW99fOT189hBlYN4UW763A3qheCmC9WrjNCGg2O"',
    'csm-hit': 'tb:RFT6GNRWBV1F2VQ5TWPY+sa-RFT6GNRWBV1F2VQ5TWPY-VGQB4KWK4032VV53CJ5S|1758039075740&t:1758039075740&adb:adblk_no',
    'rxc': 'ANseot7arc9w2MGTr2A',
}

headers_same_product_page3 = {
    'accept': 'text/html,*/*',
    'accept-language': 'en-US,en;q=0.9',
    'anti-csrftoken-a2z': 'hMAbVqq7brhAsDc%2F792GzBQSpoABjQR9ASo3Yq6wmrwjAAAAAGjJjBgAAAAB',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'device-memory': '8',
    'downlink': '10',
    'dpr': '1.5',
    'ect': '4g',
    'origin': 'https://www.amazon.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.amazon.com/product-reviews/B0DBPZZRGC/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2',
    'rtt': '0',
    'sec-ch-device-memory': '8',
    'sec-ch-dpr': '1.5',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-ch-viewport-width': '1217',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'viewport-width': '1217',
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': 'ubid-main=135-9735178-2965835; aws-target-data=%7B%22support%22%3A%221%22%7D; regStatus=registered; session-id=130-8483115-7485730; remember-account=true; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; i18n-prefs=USD; lc-main=en_US; kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent=general=in; kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity=CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=; aws-target-visitor-id=1717359572436-390315.44_0; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==; skin=noskin; at-main=Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw; sess-at-main="nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="; sst-main=Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo; session-id-time=2082787201l; session-token=EhZuWEgH3DmUHddZARCaU+jwXe/Dub7Zys2SNQOwwHl4IBeqZUkj0w7Rysvts3qUTTc5yTbHtTCvqRG67lwk+Vo/R3mCA9ZTw3Mn55tZYOIeN/Uisav5Pj/oP/B7qk063NX4T24SDNmTYJyHabF+jKrfWomM5zRx3iSB0B9WQESf2qgM8BAxl//F2xbOhf2IJGYSt37BXGpW5kmIJ87sJOSsl1IFXIykuQYpaMrEQLg8E7r/tzw7CC8B5amor71WSCRg8L2WhAqmqE8Xrqf492eQdgpKNV0PSvMftT3/O8Sy0+bapWUGwu67tPpaqB/9ksfZlIKYIlcPxqC3rk2Nf9KbIx1zux1YJPYNuv1h4HBl9q3NZ+QV53inWiKBtFYU; x-main="xgK1a0Wb3Az?dpzoCJZjKi8YvMW99fOT189hBlYN4UW763A3qheCmC9WrjNCGg2O"; csm-hit=tb:RFT6GNRWBV1F2VQ5TWPY+sa-RFT6GNRWBV1F2VQ5TWPY-VGQB4KWK4032VV53CJ5S|1758039075740&t:1758039075740&adb:adblk_no; rxc=ANseot7arc9w2MGTr2A',
}

data_same_product_page3 = {
    'sortBy': '',
    'reviewerType': 'all_reviews',
    'formatType': '',
    'mediaType': '',
    'filterByStar': '',
    'filterByAge': '',
    'pageNumber': '3',
    'filterByLanguage': '',
    'filterByKeyword': '',
    'shouldAppend': 'undefined',
    'deviceType': 'desktop',
    'canShowIntHeader': 'undefined',
    'reftag': 'cm_cr_getr_d_paging_btm_next_3',
    'pageSize': '10',
    'asin': 'B0DBPZZRGC',
    'scope': 'reviewsAjax2',
}

"""diff product
https://www.amazon.com/product-reviews/B0CQM9M4YH/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1
"""

cookies_diff_product_page1 = {
    'ubid-main': '135-9735178-2965835',
    'aws-target-data': '%7B%22support%22%3A%221%22%7D',
    'regStatus': 'registered',
    'session-id': '130-8483115-7485730',
    'remember-account': 'true',
    'aws-userInfo': '%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D',
    'i18n-prefs': 'USD',
    'lc-main': 'en_US',
    'kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent': 'general=in',
    'kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity': 'CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=',
    'aws-target-visitor-id': '1717359572436-390315.44_0',
    'AMCV_7742037254C95E840A4C98A6%40AdobeOrg': '1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0',
    'csd-key': 'eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==',
    'skin': 'noskin',
    'at-main': 'Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw',
    'sess-at-main': '"nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="',
    'sst-main': 'Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo',
    'session-id-time': '2082787201l',
    'session-token': 'EhZuWEgH3DmUHddZARCaU+jwXe/Dub7Zys2SNQOwwHl4IBeqZUkj0w7Rysvts3qUTTc5yTbHtTCvqRG67lwk+Vo/R3mCA9ZTw3Mn55tZYOIeN/Uisav5Pj/oP/B7qk063NX4T24SDNmTYJyHabF+jKrfWomM5zRx3iSB0B9WQESf2qgM8BAxl//F2xbOhf2IJGYSt37BXGpW5kmIJ87sJOSsl1IFXIykuQYpaMrEQLg8E7r/tzw7CC8B5amor71WSCRg8L2WhAqmqE8Xrqf492eQdgpKNV0PSvMftT3/O8Sy0+bapWUGwu67tPpaqB/9ksfZlIKYIlcPxqC3rk2Nf9KbIx1zux1YJPYNuv1h4HBl9q3NZ+QV53inWiKBtFYU',
    'x-main': '"xgK1a0Wb3Az?dpzoCJZjKi8YvMW99fOT189hBlYN4UW763A3qheCmC9WrjNCGg2O"',
    'csm-hit': 'tb:5ATMRGFRQEC9MZTRXPQR+sa-SD5EHVHX2Q06QJ2VEHW5-NATZ8JBHSCF8MNJZ1B13|1758039178926&t:1758039178926&adb:adblk_no',
    'rxc': 'ANseot5vrc9w2MGTr2A',
}

headers_diff_product_page1 = {
    'accept': 'text/html,*/*',
    'accept-language': 'en-US,en;q=0.9',
    'anti-csrftoken-a2z': 'hOkIV7M6oABq7%2FSh0f9bPzlOalMCLVtNbiBZKedtXKl2AAAAAGjJbZIAAAAB',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'device-memory': '8',
    'downlink': '10',
    'dpr': '1.5',
    'ect': '4g',
    'origin': 'https://www.amazon.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.amazon.com/product-reviews/B0CQM9M4YH/ref=cm_cr_getr_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2',
    'rtt': '0',
    'sec-ch-device-memory': '8',
    'sec-ch-dpr': '1.5',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-ch-viewport-width': '1217',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'viewport-width': '1217',
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': 'ubid-main=135-9735178-2965835; aws-target-data=%7B%22support%22%3A%221%22%7D; regStatus=registered; session-id=130-8483115-7485730; remember-account=true; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; i18n-prefs=USD; lc-main=en_US; kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent=general=in; kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity=CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=; aws-target-visitor-id=1717359572436-390315.44_0; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==; skin=noskin; at-main=Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw; sess-at-main="nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="; sst-main=Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo; session-id-time=2082787201l; session-token=EhZuWEgH3DmUHddZARCaU+jwXe/Dub7Zys2SNQOwwHl4IBeqZUkj0w7Rysvts3qUTTc5yTbHtTCvqRG67lwk+Vo/R3mCA9ZTw3Mn55tZYOIeN/Uisav5Pj/oP/B7qk063NX4T24SDNmTYJyHabF+jKrfWomM5zRx3iSB0B9WQESf2qgM8BAxl//F2xbOhf2IJGYSt37BXGpW5kmIJ87sJOSsl1IFXIykuQYpaMrEQLg8E7r/tzw7CC8B5amor71WSCRg8L2WhAqmqE8Xrqf492eQdgpKNV0PSvMftT3/O8Sy0+bapWUGwu67tPpaqB/9ksfZlIKYIlcPxqC3rk2Nf9KbIx1zux1YJPYNuv1h4HBl9q3NZ+QV53inWiKBtFYU; x-main="xgK1a0Wb3Az?dpzoCJZjKi8YvMW99fOT189hBlYN4UW763A3qheCmC9WrjNCGg2O"; csm-hit=tb:5ATMRGFRQEC9MZTRXPQR+sa-SD5EHVHX2Q06QJ2VEHW5-NATZ8JBHSCF8MNJZ1B13|1758039178926&t:1758039178926&adb:adblk_no; rxc=ANseot5vrc9w2MGTr2A',
}

data_diff_product_page1 = {
    'sortBy': '',
    'reviewerType': 'all_reviews',
    'formatType': '',
    'mediaType': '',
    'filterByStar': '',
    'filterByAge': '',
    'pageNumber': '1',
    'filterByLanguage': '',
    'filterByKeyword': '',
    'shouldAppend': 'undefined',
    'deviceType': 'desktop',
    'canShowIntHeader': 'undefined',
    'reftag': 'cm_cr_getr_d_paging_btm_prev_1',
    'pageSize': '10',
    'asin': 'B0CQM9M4YH',
    'scope': 'reviewsAjax3',
}


def run_request(cookies_override=None, headers_override=None, data_override=None, url=None):
    used_cookies = cookies if cookies_override is None else cookies_override
    used_headers = headers if headers_override is None else headers_override
    used_data = data if data_override is None else data_override
    used_url = (
        'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_next_2'
        if url is None else url
    )
    resp = requests.post(
        used_url,
        cookies=used_cookies,
        headers=used_headers,
        data=used_data,
    )
    return resp.text


if __name__ == "__main__":
    print(run_request())

# """
# # cookies = {
# #     'ubid-main': '135-9735178-2965835',
# #     'aws-target-data': '%7B%22support%22%3A%221%22%7D',
# #     'regStatus': 'registered',
# #     'session-id': '130-8483115-7485730',
# #     'remember-account': 'true',
# #     'aws-userInfo': '%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D',
# #     'i18n-prefs': 'USD',
# #     'lc-main': 'en_US',
# #     'kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent': 'general=in',
# #     'kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity': 'CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=',
# #     'aws-target-visitor-id': '1717359572436-390315.44_0',
# #     'AMCV_7742037254C95E840A4C98A6%40AdobeOrg': '1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0',
# #     'csd-key': 'eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==',
# #     'skin': 'noskin',
# #     'at-main': 'Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw',
# #     'sess-at-main': '"nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="',
# #     'sst-main': 'Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo',
# #     'session-id-time': '2082787201l',
# #     'session-token': 'AOdG0ynfUF2/pcvE81EfFT9LkSyZDukz0Dqy9Bp/OM6vP/6jvIGPe0JVQ8Q35SQZLrZMhE7nAbPuX7vUSvTK+XQdH8Ecy7bV+Ay1ZETV7qj+Gbb1uxU5vNagIW5rHuToUr9+Chw9B2RlROospjvV4pTEU2bKRme2RpemjkZW7/wXp5DMtxYggrRQ7L9FO63H0j/vK5h4dBVuyJwRA2r3yZR3tbiozKnEJbBxsAc82sXRB830t7+BGKb0QTqYirkogeBAPBRs12sb7CUiWSW+eBcDD7va4q8WCihG6rij4+VRfkdKmOvdnG2MytXQifbhBlEWhUMa0lXym/jOSo1w1sBIUK3ZCvmTCf6kwm27iGfvxnvMd4voGiFI9Cq7pHe6',
# #     'x-main': '"GNs2Rj7umoQel@v2B6xyElY@0tv8YsraJxEwQ9B772Se4drMiswbbK@mB?QOQI07"',
# #     'csm-hit': 'tb:NEPGDSYQJAT2Y8E126BY+sa-RWTN3N4WGHSDPPZT16CN-SKFNB88KW12E5EZ9BPFN|1758028269990&t:1758028269990&adb:adblk_no',
# #     'rxc': 'ANseot6YSM9w2MGTr2A',
# # }

# headers = {
#     'accept': 'text/html,*/*',
#     'accept-language': 'en-US,en;q=0.9',
#     'anti-csrftoken-a2z': 'hHaerDfRdIGFQHCPNU9hUol1XTr5orlt4M0d%2BJAR4wEDAAAAAGjJVlkAAAAB',
#     'cache-control': 'no-cache',
#     'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
#     'device-memory': '8',
#     'downlink': '10',
#     'dpr': '1.5',
#     'ect': '4g',
#     'origin': 'https://www.amazon.com',
#     'pragma': 'no-cache',
#     'priority': 'u=1, i',
#     'referer': 'https://www.amazon.com/product-reviews/B0DBPZZRGC/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2',
#     'rtt': '0',
#     'sec-ch-device-memory': '8',
#     'sec-ch-dpr': '1.5',
#     'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-ch-ua-platform-version': '"19.0.0"',
#     'sec-ch-viewport-width': '1217',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-origin',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
#     'viewport-width': '1217',
#     'x-requested-with': 'XMLHttpRequest',
#     # 'cookie': 'ubid-main=135-9735178-2965835; aws-target-data=%7B%22support%22%3A%221%22%7D; regStatus=registered; session-id=130-8483115-7485730; remember-account=true; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A047276618994%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Yuxian%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; i18n-prefs=USD; lc-main=en_US; kndctr_7742037254C95E840A4C98A6_AdobeOrg_consent=general=in; kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity=CiY1NDg5OTE0NjMzNDExNzA3ODIxMDAzODY3MDU1ODkxMjU5Mjg4MlISCJCrg5LyMhABGAEqA1ZBNjAA8AHwrd2i-TI=; aws-target-visitor-id=1717359572436-390315.44_0; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20289%7CMCMID%7C11830691514499522683169632618378224020%7CMCAAMLH-1753529570%7C7%7CMCAAMB-1753529570%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1752931970s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; csd-key=eyJ3YXNtVGVzdGVkIjp0cnVlLCJ3YXNtQ29tcGF0aWJsZSI6dHJ1ZSwid2ViQ3J5cHRvVGVzdGVkIjpmYWxzZSwidiI6MSwia2lkIjoiYjBjNzMxIiwia2V5IjoiU1gxdG9FM2wxTTFrSFFjaTM5QkNoQTdneEJmY0tjY0g0NndaTVhDdlpaRzBLU09UUnM4ODJqVGRYVVNsdk5yTlBCMDV4QlZpV2M4RFRicUpCalB5b2pxbkl5T09FN2J4U0NrQ1lYQWFjS3FpZlVreVh4d2FFRjcvdnpxVnBOUk1FTlUwYjdLVXRIbHFRRVJUblZsa2tOWE9qRCtQOWx2V2ZUM2FSdzdFakk5UVRaTVZWZ0kwdEZnd0tqWjFyOWppajZadmx3STBSa09HdHkrSlh5MXdRcHR6Q0pOTTZvOUUzNUd5QVRsQzRFSXBBMFRHdlRuOHNsUlRQSEREN3laRVRicnNmczE2ZzVpRm5DNUFqQzBPbUkxTm82ck85cGRNd2JJa2hVT2RBY3pIaGtmWWF6MlpFSjRIVlNNc25iYkVwS05DckttQlQ1STBOV2luVlZIeWJnPT0ifQ==; skin=noskin; at-main=Atza|IwEBIFMcBIeWNJD24EbyL58q-9Sf-GXh-XJerrOKTEfEBBX5d89uzqCCYoI_tYxauLhQ_vNnbeANm1ZNIVLGqRcDNhIBtH7ae6DK4AGiVjQSZEkvsr6DkglZgoIkZ2pMnR6fZYtHhnKVH8xg_cFDryBL2Me8Saf_IAOp-ZADrBhAgGq6whWHNpRc-4pQ-_kyezd3trTcb1VGduBNdwDEY5QW8SZT53iluChQ37nlZ8-BLRIQjw; sess-at-main="nzStb8hih3+f+wKctBfVXfycma4U8iXxKOjmHfPpMB0="; sst-main=Sst1|PQEA5zLUWUKMdQA3doj38m3sDKiLICyIqP3MvZjOKNn4tEzAkyKh2NU6TG_h0qPlJWQhnNmZKuQXtEQBPf-itO1-VQnTkt1-Xdjja_hpIYXgCnuaO4EuSDf1zXnkWVLpYkkDYSLuKbjx-VwCz76qfZmaK3v8jwZPLBEV9LWKovz4CK1CTI1tHAVrxQlst9gW9tIp4zVegZRFK8IREUZKdtVkjXaZ-6gqalsfUQvw1aobcnO6V1kfJpv-Dkm8WlFrByI-QZUsFzRqSopZndYKsaXqJTNFmC9xjhEbBa8GjfN5O3_I4OaQtlzZ3WD7Ji13AMu4Y57WexmweeDY-qjhJ4wXTA1rruj2iWkNMLHBr5mrspo; session-id-time=2082787201l; session-token=AOdG0ynfUF2/pcvE81EfFT9LkSyZDukz0Dqy9Bp/OM6vP/6jvIGPe0JVQ8Q35SQZLrZMhE7nAbPuX7vUSvTK+XQdH8Ecy7bV+Ay1ZETV7qj+Gbb1uxU5vNagIW5rHuToUr9+Chw9B2RlROospjvV4pTEU2bKRme2RpemjkZW7/wXp5DMtxYggrRQ7L9FO63H0j/vK5h4dBVuyJwRA2r3yZR3tbiozKnEJbBxsAc82sXRB830t7+BGKb0QTqYirkogeBAPBRs12sb7CUiWSW+eBcDD7va4q8WCihG6rij4+VRfkdKmOvdnG2MytXQifbhBlEWhUMa0lXym/jOSo1w1sBIUK3ZCvmTCf6kwm27iGfvxnvMd4voGiFI9Cq7pHe6; x-main="GNs2Rj7umoQel@v2B6xyElY@0tv8YsraJxEwQ9B772Se4drMiswbbK@mB?QOQI07"; csm-hit=tb:NEPGDSYQJAT2Y8E126BY+sa-RWTN3N4WGHSDPPZT16CN-SKFNB88KW12E5EZ9BPFN|1758028269990&t:1758028269990&adb:adblk_no; rxc=ANseot6YSM9w2MGTr2A',
# }

# data = {
#     'sortBy': '',
#     'reviewerType': 'all_reviews',
#     'formatType': '',
#     'mediaType': '',
#     'filterByStar': '',
#     'filterByAge': '',
#     'pageNumber': '3',
#     'filterByLanguage': '',
#     'filterByKeyword': '',
#     'shouldAppend': 'undefined',
#     'deviceType': 'desktop',
#     'canShowIntHeader': 'undefined',
#     'reftag': 'cm_cr_getr_d_paging_btm_next_3',
#     'pageSize': '10',
#     'asin': 'B0DBPZZRGC',
#     'scope': 'reviewsAjax2',
# }

# response = requests.post(
#     'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_next_3',
#     cookies=cookies,
#     headers=headers,
#     data=data,
# )
# """
