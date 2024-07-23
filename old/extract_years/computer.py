import json
import requests
from math import ceil


class Computer:
    def request_computer(self, page_number=1):
        cookies = {
            'osano_consentmanager_uuid': '375849de-906c-4977-9c20-a4aea3d9c181',
            'osano_consentmanager': '1K77SB_8PrUgk0tLb9XVfufqT5nJwrzs2_OHH20T7E2eDLQgyx-TqSWItMB4smSx1JrzAk2Sqs_tWMP1woVLqPtSWAXJVpaVpY3fF2-5rGgVN__CIJclC4NIHOz03Mg403uqAzILBUAailcJaCrQAdK7Zfl2PR9qjqiii1xQraT1khK6YFoxaYeU6XiQg4ayZk1kBTsEG5d4zJwE6v5xq0dv3cIJ8ZFDwjLV9osVntCHUEb3RQW-c6WKmTRjuSizLPeVmjvNzdwgZv2HacJTXOmwTko=',
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en,fr;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'osano_consentmanager_uuid=375849de-906c-4977-9c20-a4aea3d9c181; osano_consentmanager=1K77SB_8PrUgk0tLb9XVfufqT5nJwrzs2_OHH20T7E2eDLQgyx-TqSWItMB4smSx1JrzAk2Sqs_tWMP1woVLqPtSWAXJVpaVpY3fF2-5rGgVN__CIJclC4NIHOz03Mg403uqAzILBUAailcJaCrQAdK7Zfl2PR9qjqiii1xQraT1khK6YFoxaYeU6XiQg4ayZk1kBTsEG5d4zJwE6v5xq0dv3cIJ8ZFDwjLV9osVntCHUEb3RQW-c6WKmTRjuSizLPeVmjvNzdwgZv2HacJTXOmwTko=',
            'origin': 'https://www.computer.org',
            'priority': 'u=1, i',
            'referer': 'https://www.computer.org/csdl/search/default?queryState=%7B%22basicSearchText%22:%5Bnull,%22%5C%22digital%20twin%5C%22%20or%20%5C%22digital%20twin%5C%22%22%5D,%22basicSearchTextSubmitted%22:%5B%22%22,%22%5C%22digital%20twin%5C%22%20or%20%5C%22digital%20twin%5C%22%22%5D,%22searchResultLimit%22:%5B10,100%5D%7D',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        json_data = {
            'search': '"digital twin" OR "digital twins"',
            'doiSearch': None,
            'acronymSearch': None,
            'authorSearch': None,
            'authorAffiliationSearch': None,
            'advancedSearch': None,
            'publicationSearch': None,
            'beginPubDate': 1960,
            'endPubDate': 2025,
            'accessType': 'all',
            'searchInner': [],
            'resultLimit': 100,
            'currentPage': page_number,
            'authors': [],
            'authorsAffiliation': [],
            'publications': [],
            'contentTypes': [],
            'sortBy': 'rel',
            'includePreprints': True,
        }

        return requests.post('https://www.computer.org/csdl/search/api/v1/search', cookies=cookies, headers=headers,
                             json=json_data)

    def request_all_infos_computer(self):
        response = self.request_computer()
        json_content = json.loads(response.text)
        with open('computer_years2.txt', 'a', encoding='utf-8') as f:
            for elem in json_content["results"]:
                f.write(elem["pubDate"].split(' ')[0] + "\n")
        number_of_pages = ceil(json_content["numHits"] / json_content["resultLimit"])
        # print(number_of_pages)
        for i in range(2, number_of_pages + 1):
            with open('computer_years2.txt', 'a', encoding='utf-8') as f:
                response_current = self.request_computer(i)
                temp = json.loads(response_current.text)["results"]
                for elem in temp:
                    f.write(elem["pubDate"].split(' ')[0] + "\n")
