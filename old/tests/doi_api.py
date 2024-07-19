import requests


def get_article_info(doii):
    url = f"https://api.crossref.org/works/{doii}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


# Example DOI
doi = "10.1109/MC.2018.2876181"

# Fetch article information
article_info = get_article_info(doi)

if article_info:
    print("Article Information:")
    print(f"Title: {article_info['message']['title'][0]}")
    print(f"Authors: {[author['given'] + ' ' + author['family'] for author in article_info['message']['author']]}")
    print(f"Publication Year: {article_info['message']['published-print']['date-parts'][0][0]}")
    print(f"Journal: {article_info['message']['container-title'][0]}")
    print(f"DOI: {article_info['message']['DOI']}")
else:
    print("Failed to retrieve article information.")
