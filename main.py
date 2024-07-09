import json
from math import ceil
import requests


def request_ieee(page_number=1):
    cookies = {
        '_zitok': '050435a5c898fbf72eee1719240246',
        'osano_consentmanager_uuid': 'a844dfd0-8ebb-4350-843b-d8ef9f3d4435',
        'osano_consentmanager': 'tZhCNOWcQf2n2owY7xsPk4WpOXbkZbrvKGIxPl6aqZzxitMYbXg5z8-JU9W9dT-1XkZZ7jeSMYY5jBClyCNthKq7K_pUnhE3oXFJwYrIab4B6s1_jgM0E5utX2IwHJfEv3w0RT7PBu4AFJ57GXPynXNHan8I7JadGoOaPbDUN19k88sV9hrCmhDUdTMgzWkFhflV_ZrygEaX0kMB-oZ1uItUMm8OcIhLAUHBeGzJQZpN2srffIIJgAg4pAUpSL7FVINvfpaduf62dtwaJEEVSpmnEsec2Y4TeLKiCA==',
        'AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg': 'T',
        's_fid': '61306A06BFF4A040-39E874041D24AF28',
        'hum_ieee_visitor': '2ac17f11-1729-4a41-bb3a-eb351268da5c',
        'JSESSIONID': 'D0FB3A2C38ED6D80B2F6AFE40077CBA2',
        'ipCheck': '2a01:e0a:1b7:10b0:297c:df36:852c:cda8',
        'AWSALBAPP-1': '_remove_',
        'AWSALBAPP-2': '_remove_',
        'AWSALBAPP-3': '_remove_',
        'WLSESSION': '1510109706.47873.0000',
        'AMCVS_8E929CC25A1FB2B30A495C97%40AdobeOrg': '1',
        's_cc': 'true',
        's_sq': '%5B%5BB%5D%5D',
        'TS016349ac': '01f15fc87c0beb0adfe36c48b27b8374a293c788a7321fade614872bcff03d45630fe30d6aeee86853643058522c8f907ccdea81fa',
        'AWSALBAPP-0': 'AAAAAAAAAADc1S8DU5iza+Q6a5f6jYn3KamgXAl/THZQHbf9tHSjjH/cR1ip8Hjyw55jJ3w7aSM/Xfdn3wmeaMoGlLAHNepSrVC1sKA/UaAeoCCPde+uAdEXkKlbNoVi1Ni/W3wCjaq3peG3Fttqh/itjgSXRyTwzB0dmcSiKFdUSc2q3A6CieXCEjYvvv5CtIcWHOoiefnm5/OYt06bfA==',
        'TSaf720a17029': '0807dc117eab2800e9615c714cd1d31ddab00f9ad2c4c438dfffcd24369f363ac13cf45ea9788036357d4740e6bc299f',
        'TS8b476361027': '0807dc117eab2000228a57d4f718a8647105030b47d2cd7b05187113d67345169c61c36d4188048108bd19e4a911300072753070202c8c4a45af47faaeec68bd336ea5eff8f5b0d47a0cb99a43425beba579b12107e7b760700131c21b78e1b3',
        'utag_main': 'vapi_domain:ieee.org$v_id:019096614f4f002ec7cfbf7fb76c0506f004506700bd0$_sn:1$_se:26$_ss:0$_st:1720512845216$ses_id:1720509878097%3Bexp-session$_pn:8%3Bexp-session',
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,fr;q=0.9',
        'content-type': 'application/json',
        # 'cookie': '_zitok=050435a5c898fbf72eee1719240246; osano_consentmanager_uuid=a844dfd0-8ebb-4350-843b-d8ef9f3d4435; osano_consentmanager=tZhCNOWcQf2n2owY7xsPk4WpOXbkZbrvKGIxPl6aqZzxitMYbXg5z8-JU9W9dT-1XkZZ7jeSMYY5jBClyCNthKq7K_pUnhE3oXFJwYrIab4B6s1_jgM0E5utX2IwHJfEv3w0RT7PBu4AFJ57GXPynXNHan8I7JadGoOaPbDUN19k88sV9hrCmhDUdTMgzWkFhflV_ZrygEaX0kMB-oZ1uItUMm8OcIhLAUHBeGzJQZpN2srffIIJgAg4pAUpSL7FVINvfpaduf62dtwaJEEVSpmnEsec2Y4TeLKiCA==; AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg=T; s_fid=61306A06BFF4A040-39E874041D24AF28; hum_ieee_visitor=2ac17f11-1729-4a41-bb3a-eb351268da5c; JSESSIONID=D0FB3A2C38ED6D80B2F6AFE40077CBA2; ipCheck=2a01:e0a:1b7:10b0:297c:df36:852c:cda8; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; WLSESSION=1510109706.47873.0000; AMCVS_8E929CC25A1FB2B30A495C97%40AdobeOrg=1; s_cc=true; s_fid=61306A06BFF4A040-39E874041D24AF28; s_sq=%5B%5BB%5D%5D; TS016349ac=01f15fc87c0beb0adfe36c48b27b8374a293c788a7321fade614872bcff03d45630fe30d6aeee86853643058522c8f907ccdea81fa; AWSALBAPP-0=AAAAAAAAAADc1S8DU5iza+Q6a5f6jYn3KamgXAl/THZQHbf9tHSjjH/cR1ip8Hjyw55jJ3w7aSM/Xfdn3wmeaMoGlLAHNepSrVC1sKA/UaAeoCCPde+uAdEXkKlbNoVi1Ni/W3wCjaq3peG3Fttqh/itjgSXRyTwzB0dmcSiKFdUSc2q3A6CieXCEjYvvv5CtIcWHOoiefnm5/OYt06bfA==; TSaf720a17029=0807dc117eab2800e9615c714cd1d31ddab00f9ad2c4c438dfffcd24369f363ac13cf45ea9788036357d4740e6bc299f; TS8b476361027=0807dc117eab2000228a57d4f718a8647105030b47d2cd7b05187113d67345169c61c36d4188048108bd19e4a911300072753070202c8c4a45af47faaeec68bd336ea5eff8f5b0d47a0cb99a43425beba579b12107e7b760700131c21b78e1b3; utag_main=vapi_domain:ieee.org$v_id:019096614f4f002ec7cfbf7fb76c0506f004506700bd0$_sn:1$_se:26$_ss:0$_st:1720512845216$ses_id:1720509878097%3Bexp-session$_pn:8%3Bexp-session',
        'origin': 'https://ieeexplore.ieee.org',
        'priority': 'u=1, i',
        'referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=(%22Digital%20Twin%22%20OR%20%22Digital%20Twins%22)%20AND%20(%22cyber%20attacks%22%20OR%20%22cybersecurity%22%20OR%20%22cyber-security%22)%20AND%20(%22internet%20of%20things%22%20OR%20%22IoT%22%20OR%20%22CPS%22%20OR%20%22cyber-physical%20systems%22%20OR%20%22cyber-physical%20systems%22)&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&rowsPerPage=100&pageNumber=1',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-security-request': 'required',
    }

    json_data = {
        'newsearch': True,
        'queryText': '("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")',
        'highlight': True,
        'returnType': 'SEARCH',
        'matchPubs': True,
        'rowsPerPage': '100',
        'pageNumber': page_number,
        'returnFacets': [
            'ALL',
        ],
    }

    return requests.post('https://ieeexplore.ieee.org/rest/search', cookies=cookies, headers=headers,
                         json=json_data)


def request_all_infos_ieeexplore():
    response = request_ieee()
    json_content = json.loads(response.text)
    number_of_pages = json_content["totalPages"]
    # print(number_of_pages)
    for i in range(2, number_of_pages + 1):
        response_current = request_ieee(i)
        temp = json.loads(response_current.text)["records"]
        for elem in temp:
            json_content["records"].append(elem)
    with open('contents/ieeexplore_raw.json', 'w', encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=4)


def get_articles_and_authors_ieeexplore():
    with open('contents/ieeexplore.json', 'r', encoding='utf-8') as input_file:
        output_file = open("contents/ieeexplore_articles.json", "w", encoding='utf-8')
        content = json.load(input_file)
        for elem in content["records"]:
            auth = ""
            for authors in elem["authors"]:
                if authors == elem["authors"][-1]:
                    auth += authors["normalizedName"]
                else:
                    auth += authors["normalizedName"] + ", "
            output_file.write(elem["articleTitle"] + ", Authors : " + auth + "\n")


def request_computer(page_number=1):
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


def request_all_infos_computer():
    response = request_computer()
    json_content = json.loads(response.text)
    number_of_pages = ceil(json_content["numHits"]/json_content["resultLimit"])
    print(number_of_pages)
    for i in range(2, number_of_pages + 1):
        response_current = request_computer(i)
        temp = json.loads(response_current.text)["results"]
        for elem in temp:
            json_content["results"].append(elem)
    with open('contents/computer_raw.json', 'w', encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=4)


def compare_ieee_computer():
    ieee = json.load(open("contents/ieeexplore.json", "r", encoding='utf-8'))
    computer = json.load(open("contents/computer_raw.json", "r", encoding='utf-8'))
    ieee_articles_names = []
    for article in ieee["records"]:
        ieee_articles_names.append(article["articleTitle"])
    computer_articles_names = []
    for article in computer["results"]:
        computer_articles_names.append(article["title"])
    print(ieee_articles_names)
    print(computer_articles_names)
    print(set(ieee_articles_names).intersection(computer_articles_names))


def main():
    compare_ieee_computer()


if __name__ == '__main__':
    main()
