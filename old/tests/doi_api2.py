import requests


def get_article_info(doi):
    url = f"https://api.semanticscholar.org/v1/paper/{doi}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


# Example DOI
doi = "10.1037/0022-3514.74.6.1464"

# Fetch article information
article_info = get_article_info(doi)

if article_info:
    title = article_info.get('title', 'N/A')
    authors = [author['name'] for author in article_info.get('authors', [])]
    publication_year = article_info.get('year', 'N/A')
    journal = article_info.get('venue', 'N/A')
    keywords = article_info.get('keywords', 'N/A')

    print("Article Information:")
    print(f"Title: {title}")
    print(f"Authors: {', '.join(authors)}")
    print(f"Publication Year: {publication_year}")
    print(f"Journal: {journal}")
    print(f"Keywords: {', '.join(keywords) if keywords != 'N/A' else 'N/A'}")
else:
    print("Failed to retrieve article information.")
