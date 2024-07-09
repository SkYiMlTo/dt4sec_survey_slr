import requests
import json
from math import ceil


class Scopus:
    def __init__(self):
        pass

    def request_scopus(self, offset=0):
        cookies = {
            'SCSessionID': '0CAFCB3DF6CD5D094846C71A057F605A.i-0341a23247c631c2d',
            'scopusSessionUUID': '9cc9776b-7589-460a-9',
            'scopus.machineID': '0CAFCB3DF6CD5D094846C71A057F605A.i-0341a23247c631c2d',
            'AWSELB': 'CB9317D502BF07938DE10C841E762B7A33C19AADB15E3B21963A5D24E6F040A846820A64A34BAA517C2F84167179DE7152C19EC16610BA32070D9964CEACBAE7C5777723B7602F10FBF90F69CD9EFBAA5585473B78',
            '__cf_bm': 'ZOROjGyhrRPVm0axWVPlm3LfJWLMwhBkoeNtDvd6NhY-1720535982-1.0.1.1-j9l.CHR7iDIg1dae7Ks.SxSY1r7tQZ9i3MIipM3xB1loTE71RD6c9u98fpO9ICSHq991cYP0I3zuW6yTxr05Xw',
            '_cfuvid': '6AUJmXe5hjZ5sO5sVKDdcmZy4_.dnbUCbEtIkJ5ntlA-1720535982332-0.0.1.1-604800000',
            'SCOPUS_JWT': 'eyJraWQiOiJjYTUwODRlNi03M2Y5LTQ0NTUtOWI3Zi1kMjk1M2VkMmRiYmMiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxMTgwNjgzOSIsImRlcGFydG1lbnRJZCI6IjExMjQ5OSIsImlzcyI6IlNjb3B1cyIsImluc3RfYWNjdF9pZCI6IjcyNzMxIiwiaXNFeHRlcm5hbFN1YnNjcmliZWRFbnRpdGxlbWVudHMiOmZhbHNlLCJwYXRoX2Nob2ljZSI6ZmFsc2UsImluZHZfaWRlbnRpdHkiOiJBTk9OIiwiZXhwIjoxNzIwNTM2ODgzLCJpYXQiOjE3MjA1MzU5ODMsImFuYWx5dGljc19pbmZvIjp7ImFjY291bnROYW1lIjoiSU1UIEF0bGFudGljIEJyaXR0YW55IENhbXB1cyBvZiBOYW50ZXMgSW5mb3JtYXRpb24gVGVjaG5vbG9neSBEZXBhcnRtZW50IiwiYWNjZXNzVHlwZSI6ImFlOkFOT046OklOU1Q6SVAiLCJ1c2VySWQiOiJhZToxMTgwNjgzOSIsImFjY291bnRJZCI6IjcyNzMxIn0sImRlcGFydG1lbnROYW1lIjoiTGlicmFyeSIsImluc3RfYWNjdF9uYW1lIjoiSU1UIEF0bGFudGljIEJyaXR0YW55IENhbXB1cyBvZiBOYW50ZXMgSW5mb3JtYXRpb24gVGVjaG5vbG9neSBEZXBhcnRtZW50Iiwic3Vic2NyaWJlciI6dHJ1ZSwid2ViVXNlcklkIjoiMTE4MDY4MzkiLCJpbnN0X2Fzc29jX21ldGhvZCI6IklQIiwiYWNjb3VudE51bWJlciI6IkMwMDAwNzI3MzEiLCJwYWNrYWdlSWRzIjpbXSwiYXVkIjoiU2NvcHVzIiwibmJmIjoxNzIwNTM1OTgzLCJmZW5jZXMiOltdLCJpbmR2X2lkZW50aXR5X21ldGhvZCI6IiIsImluc3RfYXNzb2MiOiJJTlNUIiwidXNhZ2VQYXRoSW5mbyI6IigxMTgwNjgzOSxVfDExMjQ5OSxEfDcyNzMxLEF8NTkwNTQ2LFN8NSxQfDEsUEwpKFNDT1BVUyxDT058YjE1M2Q1Mjc4OGQ2NjU0YzViNTllNDc5YjY2MjA2YWYzMTgzZ3hycWIsU1NPfEFOT05fSVAsQUNDRVNTX1RZUEUpIiwicHJpbWFyeUFkbWluUm9sZXMiOltdLCJhdXRoX3Rva2VuIjoiYjE1M2Q1Mjc4OGQ2NjU0YzViNTllNDc5YjY2MjA2YWYzMTgzZ3hycWIifQ.RGHyJLYew-PGCDw-TNfnLbZayE_SpjdNWMViJoamhYVgErDYdMmrxapVtRRwXfucD7HQrW0qZCLednf6jXBQgcJX9Hdv5J24IcqzM9Q5S8DxCCSFrPBSvaBJRDHlcLrotE4DaPN3ag70ICZ9MG2Xla8Yb2aIpKZbR4HzDXNuBOhEL5BMdiCgeCuBChYcvYXVGaEtXJM55Ie4_kMLVjEip9SdJE_6-olVTShSFFY9n1idRvdDYPGwe2zGXF76MgTKHh-eZyMmX7L8HPN4Cx0iyR6P4IPixXDtCfJLKndS0hfcosEySIQT0Rtb3MPSLp_n_117biUwPxvzd7TI6GRfHA',
            'Scopus-usage-key': 'enable-logging',
            'AT_CONTENT_COOKIE': '"KDP_FACADE_AFFILIATION_ENABLED:1,KDP_FACADE_ABSTRACT_ENABLED:1,KDP_SOURCE_ENABLED:0,KDP_FACADE_PATENT_ENABLED:1,KDP_FACADE_AUTHOR_ENABLED:1,"',
            '__cfruid': '8201257dfbc2faa7a231414f6a926a87a4fb0e07-1720535984',
            'at_check': 'true',
            'AMCVS_4D6368F454EC41940A4C98A6%40AdobeOrg': '1',
            'cf_clearance': 'qEhIJIFegcpQNBrn3cE8JcssIFOYKpUU7ro6rP2cGE8-1720535985-1.0.1.1-kdjLJPMkc_YRZnqgZAGZDnQnabiJZgnaDZ8Vo8wFFHetBe3MayE0vlYn2RZSIpr6VI1TcN6K2PFUv_ihTKcLFQ',
            'JSESSIONID': '504C56AC892739F30A63244AF00670D1',
            'AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg': '-2121179033%7CMCIDTS%7C19914%7CMCMID%7C10268944029864737171373808745143302721%7CMCAID%7CNONE%7CMCOPTOUT-1720543203s%7CNONE%7CvVersion%7C5.3.0',
            'mbox': 'session#7f6986e794d147e0bf6bfbb7b05be840#1720537864|PC#7f6986e794d147e0bf6bfbb7b05be840.37_0#1783780804',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'en,fr;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'scopus.machineID=3AC8459EAB19D50BF93488A72813AA82.i-0626e5286d0c1f760; SCSessionID=B2456012A4D5A959A0B4C51C4411CCE4.i-0889f01daf18619f3; scopusSessionUUID=7288e144-9d24-45ca-a; AWSELB=CB9317D502BF07938DE10C841E762B7A33C19AADB1467BAFA7310FCC24EB4A298B49C5B35CBFED5C687E1C1371746902E0C0AE09E810BA32070D9964CEACBAE7C5777723B76D6A62A3A2BA3BEC54C411ECD59584B3; __cf_bm=afQl2YWGWZpU2acTJhdDgqu6zAUCuhFIbQcN0Bbw0gg-1720527356-1.0.1.1-hP2qMLQR39cdlAA9eEmn7Db7W2A_a1upEU91Bsr7PJz437h5tGHPIAd07ZazTDiugmLgthnIerBsF7n.MYDvJQ; _cfuvid=Sk310sRseE0LAEVxXC2EigSFx5unUjtaUVcuWlIOPKA-1720527356783-0.0.1.1-604800000; SCOPUS_JWT=eyJraWQiOiJjYTUwODRlNi03M2Y5LTQ0NTUtOWI3Zi1kMjk1M2VkMmRiYmMiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxMTgwNjgzOSIsImRlcGFydG1lbnRJZCI6IjExMjQ5OSIsImlzcyI6IlNjb3B1cyIsImluc3RfYWNjdF9pZCI6IjcyNzMxIiwiaXNFeHRlcm5hbFN1YnNjcmliZWRFbnRpdGxlbWVudHMiOmZhbHNlLCJwYXRoX2Nob2ljZSI6ZmFsc2UsImluZHZfaWRlbnRpdHkiOiJBTk9OIiwiZXhwIjoxNzIwNTI4MjU3LCJpYXQiOjE3MjA1MjczNTcsImFuYWx5dGljc19pbmZvIjp7ImFjY2Vzc1R5cGUiOiJhZTpBTk9OOjpJTlNUOklQIiwidXNlcklkIjoiYWU6MTE4MDY4MzkiLCJhY2NvdW50SWQiOiI3MjczMSIsImFjY291bnROYW1lIjoiSU1UIEF0bGFudGljIEJyaXR0YW55IENhbXB1cyBvZiBOYW50ZXMgSW5mb3JtYXRpb24gVGVjaG5vbG9neSBEZXBhcnRtZW50In0sImRlcGFydG1lbnROYW1lIjoiTGlicmFyeSIsImluc3RfYWNjdF9uYW1lIjoiSU1UIEF0bGFudGljIEJyaXR0YW55IENhbXB1cyBvZiBOYW50ZXMgSW5mb3JtYXRpb24gVGVjaG5vbG9neSBEZXBhcnRtZW50Iiwic3Vic2NyaWJlciI6dHJ1ZSwid2ViVXNlcklkIjoiMTE4MDY4MzkiLCJpbnN0X2Fzc29jX21ldGhvZCI6IklQIiwiYWNjb3VudE51bWJlciI6IkMwMDAwNzI3MzEiLCJwYWNrYWdlSWRzIjpbXSwiYXVkIjoiU2NvcHVzIiwibmJmIjoxNzIwNTI3MzU3LCJmZW5jZXMiOltdLCJpbmR2X2lkZW50aXR5X21ldGhvZCI6IiIsImluc3RfYXNzb2MiOiJJTlNUIiwidXNhZ2VQYXRoSW5mbyI6IigxMTgwNjgzOSxVfDExMjQ5OSxEfDcyNzMxLEF8NTkwNTQ2LFN8NSxQfDEsUEwpKFNDT1BVUyxDT058N2FlMzYyNTc5OGI5MjU0YjYxNDk2OWY2OWUwMGEzNDJmMGFiZ3hycWIsU1NPfEFOT05fSVAsQUNDRVNTX1RZUEUpIiwicHJpbWFyeUFkbWluUm9sZXMiOltdLCJhdXRoX3Rva2VuIjoiN2FlMzYyNTc5OGI5MjU0YjYxNDk2OWY2OWUwMGEzNDJmMGFiZ3hycWIifQ.Zjrtoqcbii26XB-8PM8dYhsh74F9y2bOLqZuU03jlf3wQzwfAWqeKanweF0Ya3ZPKfCZnN8mJGxfNb5nBpDcHRxKL9zHX0b1aKKYmaxy4EqSJWJgGvnUZpXIxs_8zg2uNhErshO8zIGtAMxC75IsFcegXWuKA_i-g7mrhoPDN3S9d0x6cOrjxT4vKCxjdhHVwV6uw6xehJDq1Dz_RkmG3BE5ZAFCyX6BmaSn7yL2XTirhytc9wJMfbBGyMNe4wSw6ImObc02e2ts2qvGDPrGoq24LnEjWQUrzTZxVsolxoEoZXyrDBYMPHZXGC5EfJ7JJe8UFF8OFAK0dAozAlFywQ; Scopus-usage-key=enable-logging; AT_CONTENT_COOKIE="KDP_FACADE_AFFILIATION_ENABLED:1,KDP_FACADE_ABSTRACT_ENABLED:1,KDP_SOURCE_ENABLED:0,KDP_FACADE_PATENT_ENABLED:1,KDP_FACADE_AUTHOR_ENABLED:1,"; at_check=true; AMCVS_4D6368F454EC41940A4C98A6%40AdobeOrg=1; __cfruid=3a356da4055b39d67b96ed1e2e64f2e9a68ebed9-1720527360; cf_clearance=sx_x8WpZC6nMTxPWup7xYrL6CgQPkGhcQ0M1wCj_BFs-1720527360-1.0.1.1-Z4ttgeF0ndbJZHKYCDWPuL7jamonAYrX5UjMFFBgUEhTh0DkUWx0OWhbbCap34BewEkULLiLICKowSVKIWvU0Q; JSESSIONID=1309ECEE65E78C78311FFD347A4D2357; AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg=-2121179033%7CMCIDTS%7C19913%7CMCMID%7C31340885358065187017864998308487656247%7CMCAID%7CNONE%7CMCOPTOUT-1720534814s%7CNONE%7CvVersion%7C5.3.0; mbox=PC#02973003061a499299a89a00f9366f4d.37_0#1783772416|session#0b2109b49f0c46179a1be853bf58d25a#1720529476',
            'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjEyODExNjEiLCJhcCI6IjMxNDU1OTQ0IiwiaWQiOiIyZDFmYWRiODMwNDVmZDk2IiwidHIiOiI4MTQ1YzQ5YmE3ZDcwMzNjNGVhOGUxY2EwYzE4OTNjYiIsInRpIjoxNzIwNTI3NjE1NTkzLCJ0ayI6IjIwMzgxNzUifX0=',
            'origin': 'https://www.scopus.com',
            'priority': 'u=1, i',
            'referer': 'https://www.scopus.com/results/results.uri?sort=plf-f&src=s&st1=%28%22Digital+Twin%22+OR+%22Digital+Twins%22%29+AND+%28%22cyber+attacks%22+OR+%22cybersecurity%22+OR+%22cyber-security%22%29+AND+%28%22internet+of+things%22+OR+%22IoT%22+OR+%22CPS%22+OR+%22cyber-physical+systems%22+OR+%22cyber-physical+systems%22%29&sid=cf9591d7fc73d0f0791bb8896fecf7b2&sot=b&sdt=b&sl=212&s=TITLE-ABS-KEY%28%28%22Digital+Twin%22+OR+%22Digital+Twins%22%29+AND+%28%22cyber+attacks%22+OR+%22cybersecurity%22+OR+%22cyber-security%22%29+AND+%28%22internet+of+things%22+OR+%22IoT%22+OR+%22CPS%22+OR+%22cyber-physical+systems%22+OR+%22cyber-physical+systems%22%29%29&origin=searchbasic&editSaveSearch=&yearFrom=Before+1960&yearTo=Present&sessionSearchId=cf9591d7fc73d0f0791bb8896fecf7b2&limit=10',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'traceparent': '00-8145c49ba7d7033c4ea8e1ca0c1893cb-2d1fadb83045fd96-01',
            'tracestate': '2038175@nr=0-1-1281161-31455944-2d1fadb83045fd96----1720527615593',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        json_data = {
            'documentClassificationEnum': 'primary',
            'query': 'TITLE-ABS-KEY(("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems"))',
            'filters': {
                'yearFrom': 'Before 1960',
                'yearTo': 'Present',
            },
            'sort': 'plf-f',
            'itemcount': 200,
            'offset': offset,
            'showAbstract': True,
        }

        return requests.post('https://www.scopus.com/api/documents/search', cookies=cookies, headers=headers,
                             json=json_data)

    def request_all_infos_scopus(self):
        response = self.request_scopus()
        json_content = json.loads(response.text)
        number_of_pages = ceil(json_content["metadata"]["totalCount"]/json_content["metadata"]["itemCount"])
        # print(number_of_pages)
        for i in range(1, number_of_pages):
            response_current = self.request_scopus(i*json_content["metadata"]["itemCount"])
            temp = json.loads(response_current.text)["items"]
            for elem in temp:
                json_content["items"].append(elem)
        json_content["metadata"]["itemCount"] = json_content["metadata"]["totalCount"]
        with open('0_initial_request_raw/scopus_raw.json', 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=4)
