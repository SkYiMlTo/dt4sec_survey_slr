from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import re


def scrap_springler(request, path):

    # Set up the WebDriver (Chrome)
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1200')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    # Navigate to Springer website
    driver.get('https://link.springer.com/')
    time.sleep(2)
    try:
        driver.find_element(By.XPATH, '//button[@class="cc-button cc-button--secondary cc-button--contrast cc-banner__button cc-banner__button-accept"]').click()
    except:
        pass

    # Find the search box and input the query
    search_box = driver.find_elements(By.NAME, 'query')[1]
    search_box.send_keys(request)
    search_box.send_keys(Keys.RETURN)

    # Allow time for the results to load
    time.sleep(2)

    # Scrape data from all pages
    all_data = scrape_all_pages(driver)

    # Close the WebDriver
    driver.quit()

    # Save the data to a JSON file
    with open(path + 'springler_link.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    # Print confirmation
    print("Data has been saved to springler_link.json")


# Function to extract data from a single result
def extract_data(result):
    # print(result.get_attribute('innerHTML'))
    try:
        title = result.text.split('\n')[0]
        # title = result.find_element(By.XPATH, '//h3[@data-test="title"]').text
    except:
        title = "N/A"
    try:
        authors_text = result.find_element(By.XPATH, './/span[@data-test="authors"]').text
        # Split the authors text based on commas and strip any leading/trailing spaces
        authors = [{'lastName': author.strip()} for author in authors_text.split(',')]
    except:
        authors = []
    try:
        year = re.search(r'\d{4}|$', result.find_element(By.XPATH, '//span[@data-test="published"]').text).group()
    except:
        year = "N/A"
    try:
        # doi = result.find_element(By.XPATH, '//a[@data-track-action="view Article"]').get_attribute('href')
        doi = re.search(r'href="([^"]+)"', result.get_attribute('innerHTML')).group()
        doi = doi.replace('href="/article', 'https://doi.org')
        doi = doi.replace('"', '')
    except:
        doi = "N/A"
    return {
        "title": title,
        "authors": authors,
        "publicationYear": year,
        "doi": doi,
        "source": "https://link.springer.com/",
    }


# Function to scrape all pages
def scrape_all_pages(driver):
    data = []
    while True:
        # Find all search results on the page
        results = driver.find_elements(By.XPATH, '//li[@data-test="search-result-item"]')

        # Iterate over results and extract data
        for result in results:
            data.append(extract_data(result))

        # Check if there's a "Next" button to go to the next page
        try:
            next_button = driver.find_element(By.XPATH, '//a[@data-test="next-page"]')
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
        except:
            break  # No more pages to scrape
    return data

# REQUEST = ('("Digital Twin" OR "Digital Twins") AND ("cyberattack" OR "cyberattacks" OR "cyber attack" OR "cyber '
#            'attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR '
#            '"cyber-physical systems" OR "cyber-physical systems")')
# scrap_springler(REQUEST, 'springer_link.json')