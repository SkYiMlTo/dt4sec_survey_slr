import json
import requests
from math import ceil


class Computer:
    def request_computer(self, page_number=1):
        cookies = {
            'osano_consentmanager_uuid': '550a1f81-2edc-42c8-acad-30d19558ca5a',
            'osano_consentmanager': 'TxXsJX-XJL3AWdkZInQBJfllSd3ynnQ8JcYwx99ovkKnsi2hwuQS72xN_rxPa5R5As8qFTZwM0sL4m-c4b3WTgp5lzM4rzBw_SXeLnhIhVn86uU0qhvANak_XnnbUoAfbCCyWooXfqbYhQKBW8bcoWaLXgRk7QgXvcWyqFwyoi095vP1m-ysStSPhrveOrR-oF5aXKOny6mUM-k5HuFK9h-pOk-cJ4mpVNh5GOatricGQ4LkUXoPwTWZhvjUenxpmN3Kx7buVyDKBLmGPSVi_xX9tqqDBrDOH3jdNA==',
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en,fr;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'osano_consentmanager_uuid=550a1f81-2edc-42c8-acad-30d19558ca5a; osano_consentmanager=TxXsJX-XJL3AWdkZInQBJfllSd3ynnQ8JcYwx99ovkKnsi2hwuQS72xN_rxPa5R5As8qFTZwM0sL4m-c4b3WTgp5lzM4rzBw_SXeLnhIhVn86uU0qhvANak_XnnbUoAfbCCyWooXfqbYhQKBW8bcoWaLXgRk7QgXvcWyqFwyoi095vP1m-ysStSPhrveOrR-oF5aXKOny6mUM-k5HuFK9h-pOk-cJ4mpVNh5GOatricGQ4LkUXoPwTWZhvjUenxpmN3Kx7buVyDKBLmGPSVi_xX9tqqDBrDOH3jdNA==',
            'origin': 'https://www.computer.org',
            'priority': 'u=1, i',
            'referer': 'https://www.computer.org/csdl/search/default?queryState=%7B%22basicSearchText%22:%5Bnull,%22(%5C%22Digital%20Twin%5C%22%20OR%20%5C%22Digital%20Twins%5C%22)%20AND%20(%5C%22cyber%20attacks%5C%22%20OR%20%5C%22cybersecurity%5C%22%20OR%20%5C%22cyber-security%5C%22)%20AND%20(%5C%22internet%20of%20things%5C%22%20OR%20%5C%22IoT%5C%22%20OR%20%5C%22CPS%5C%22%20OR%20%5C%22cyber-physical%20systems%5C%22%20OR%20%5C%22cyber-physical%20systems%5C%22)%22%5D,%22basicSearchTextSubmitted%22:%5B%22%22,%22(%5C%22Digital%20Twin%5C%22%20OR%20%5C%22Digital%20Twins%5C%22)%20AND%20(%5C%22cyber%20attacks%5C%22%20OR%20%5C%22cybersecurity%5C%22%20OR%20%5C%22cyber-security%5C%22)%20AND%20(%5C%22internet%20of%20things%5C%22%20OR%20%5C%22IoT%5C%22%20OR%20%5C%22CPS%5C%22%20OR%20%5C%22cyber-physical%20systems%5C%22%20OR%20%5C%22cyber-physical%20systems%5C%22)%22%5D,%22doiSearchText%22:%5Bnull,%22%22%5D,%22publicationSearchTextSubmitted%22:%5B%22%22,null%5D,%22proceedingAcronymSearchTextSubmitted%22:%5B%22%22,null%5D,%22authorSearchTextSubmitted%22:%5B%22%22,null%5D,%22authorAffiliationSearchTextSubmitted%22:%5B%22%22,null%5D,%22searchResultLimit%22:%5B10,100%5D%7D',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        json_data = {
            'search': '("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")',
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
        number_of_pages = ceil(json_content["numHits"] / json_content["resultLimit"])
        print(number_of_pages)
        for i in range(2, number_of_pages + 1):
            response_current = self.request_computer(i)
            temp = json.loads(response_current.text)["results"]
            for elem in temp:
                json_content["results"].append(elem)
        with open('contents_raw/computer_raw.json', 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=4)
