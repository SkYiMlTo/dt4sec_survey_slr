import requests
from bs4 import BeautifulSoup
import csv
import time


def extract_years_from_search(query, max_pages=10):
    base_url = "https://www.computer.org/csdl/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    years = []

    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "page": page
        }
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('div', class_='search-result')

        for article in articles:
            try:
                year = article.find('span', class_='pub-date').text.strip()[-4:]
                years.append(year)
            except AttributeError:
                continue

        print(f"Processed page {page}")
        time.sleep(1)  # Be respectful with delays to avoid getting blocked

    return years


# Example usage
query = '"digital twin" OR "digital twins"'
years = extract_years_from_search(query)

# Write results to a CSV file
with open('years.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Year"])
    for year in years:
        writer.writerow([year])

print(f"Extracted {len(years)} years")
