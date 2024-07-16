import requests
import json
from math import ceil


class SemanticScholar:
    def __init__(self):
        pass

    def request_semantic_scholar(self, page_number=1):
        cookies = {
            's2Exp': 'new_ab_framework_aa%3D-control%26pdp_citation_and_reference_paper_cues%3D-enable_citation_and_reference_paper_cues%26venues%3D-enable_venues%26reader_link_styling%3D-control%26topics_beta3%3D-topics_beta3%26alerts_aa_test%3D-control%26personalized_author_card_cues%3D-control%26term_understanding%3D-control%26aa_user_based_test%3D-control%26paper_cues%3D-all_paper_cues%26new_ab_framework_mock_ab%3D-control%26aa_stable_hash_session_test%3Dtest',
            'tid': 'rBIABmaCp11RPwAIBUZ9Ag==',
            'sid': 'af8f3a1d-b799-468b-a8fd-2884e2c451a6',
            's2_copyright_dismissed': '1',
            'aws-waf-token': 'bc0e1634-4190-4323-81ce-e647579e4174:DAoAm89aaKkAAAAA:22h83V3XDRmpO/OUX5VS5dvjzukO5/aB914rRCEFYG7JMMiVGh8q1zC+O/UOY9PxJ5KwP87BwC5B0JIq+h5W8bFDpyIoSD85yVj58YdFZdRZk9gXX27/YtAOVOct5WtkLsR06wOHugZxUuJ4kexn9G1WxLMJ1UBTy3ugU4EMsXhPxZh56WVQZ1mvHhUn9gesKrfA3cPyZeUfC4u6jfAOvPAdx7/c7EAWuSqjmKsrrRqUqKbkRHylIbpgbUsWzsZdBSl6xpNIrt3wXkKE5geh2StLTQ==',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'en,fr;q=0.9',
            'cache-control': 'no-cache,no-store,must-revalidate,max-age=-1',
            'content-type': 'application/json',
            # 'cookie': 's2Exp=new_ab_framework_aa%3D-control%26pdp_citation_and_reference_paper_cues%3D-enable_citation_and_reference_paper_cues%26venues%3D-enable_venues%26reader_link_styling%3D-control%26topics_beta3%3D-topics_beta3%26alerts_aa_test%3D-control%26personalized_author_card_cues%3D-control%26term_understanding%3D-control%26aa_user_based_test%3D-control%26paper_cues%3D-all_paper_cues%26new_ab_framework_mock_ab%3D-control%26aa_stable_hash_session_test%3Dtest; tid=rBIABmaCp11RPwAIBUZ9Ag==; sid=af8f3a1d-b799-468b-a8fd-2884e2c451a6; aws-waf-token=bc0e1634-4190-4323-81ce-e647579e4174:DAoAm89aaKkAAAAA:22h83V3XDRmpO/OUX5VS5dvjzukO5/aB914rRCEFYG7JMMiVGh8q1zC+O/UOY9PxJ5KwP87BwC5B0JIq+h5W8bFDpyIoSD85yVj58YdFZdRZk9gXX27/YtAOVOct5WtkLsR06wOHugZxUuJ4kexn9G1WxLMJ1UBTy3ugU4EMsXhPxZh56WVQZ1mvHhUn9gesKrfA3cPyZeUfC4u6jfAOvPAdx7/c7EAWuSqjmKsrrRqUqKbkRHylIbpgbUsWzsZdBSl6xpNIrt3wXkKE5geh2StLTQ==',
            'origin': 'https://www.semanticscholar.org',
            'priority': 'u=1, i',
            'referer': 'https://www.semanticscholar.org/search?q=%28%22Digital%20Twin%22%20OR%20%22Digital%20Twins%22%29%20AND%20%28%22cyber%20attacks%22%20OR%20%22cybersecurity%22%20OR%20%22cyber-security%22%29%20AND%20%28%22internet%20of%20things%22%20OR%20%22IoT%22%20OR%20%22CPS%22%20OR%20%22cyber-physical%20systems%22%20OR%20%22cyber-physical%20systems%22%29&sort=relevance',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-s2-client': 'webapp-browser',
            'x-s2-ui-version': '11b36f882d6c52d827cc9963015caa1d12fe8f2e',
        }

        json_data = {
            'queryString': '("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")',
            'page': page_number,
            'pageSize': 10,
            'sort': 'relevance',
            'authors': [],
            'coAuthors': [],
            'venues': [],
            'yearFilter': None,
            'requireViewablePdf': False,
            'fieldsOfStudy': [],
            'hydrateWithDdb': True,
            'includeTldrs': True,
            'performTitleMatch': True,
            'includeBadges': True,
            'getQuerySuggestions': False,
            'cues': [
                'CitedByLibraryPaperCue',
                'CitesYourPaperCue',
                'CitesLibraryPaperCue',
            ],
            'includePdfVisibility': True,
        }

        return requests.post('https://www.semanticscholar.org/api/1/search', cookies=cookies, headers=headers,
                                 json=json_data)

    def request_all_infos_semantic_scholar(self):
        response = self.request_semantic_scholar()
        json_content = json.loads(response.text)
        number_of_pages = ceil(json_content["totalPages"])
        # print(number_of_pages)
        for i in range(1, number_of_pages+1):
            response_current = self.request_semantic_scholar(i)
            temp = json.loads(response_current.text)["results"]
            for elem in temp:
                json_content["results"].append(elem)
        with open('0_initial_request_raw/semantic_scholar_raw.json', 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=4)
