import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

def fetch_data(page):
    url = 'https://bidplus.gem.gov.in/all-bids-data'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Origin': 'https://bidplus.gem.gov.in/all-bids',
        'Host': 'bidplus.gem.gov.in',
        'Referer': 'https://bidplus.gem.gov.in/all-bids',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Cookie': '_ga=GA1.3.1284515974.1711530737; csrf_gem_cookie=e0452987f4f2237ab902801133dac509; GEMDCPROD=NODE3; _gid=GA1.3.1879095634.1714371692; TS01024d38=015c77a21ce12721954f5985105f1271c78916b0cbbd86906b66ac1ae5ca822461cdcf7a81f48b82a7060d870a70415f2c144810b5c9cfa1fcf80b269c9c0739c2de3f483a; ci_session=7a9d50ecd529e7c0ed709094b958b5dcbf919c38; TS01fd1721=015c77a21cfc92edb41b3ac92b16f205969a9794d9c0cacc2303aeb90867ce28e321d05574e667e3056e352539e498ff1b270f213d60257d98b920007f9e02708974327bfddebce1db4729fce25f8eac4af7e17dd841535c5a56b59d63aca24afc7c5fd3d2; _gat=1; _ga_MMQ7TYBESB=GS1.3.1714371692.3.1.1714373402.60.0.0'
    }
    form_data = {
        'csrf_bd_gem_nk': 'e0452987f4f2237ab902801133dac509',
        'payload': json.dumps({
            "page": page,
            "param": {
                "searchBid": "",
                "searchType": "fullText"
            },
            "filter": {
                "bidStatusType": "ongoing_bids",
                "byType": "all",
                "highBidValue": "",
                "byEndDate": {
                    "from": "",
                    "to": ""
                },
                "sort": "Bid-End-Date-Oldest"
            }
        })
    }
    m = MultipartEncoder(fields=form_data)
    headers['Content-Type'] = m.content_type

    response = requests.post(url, headers=headers, data=m, verify=False)
    
    if response.status_code != 200:
        raise Exception(f"Network response was not ok: {response.status_code} {response.reason}")

    return response.json()
