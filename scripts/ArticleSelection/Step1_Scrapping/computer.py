import time
import json

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def scrap_computer():
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    driver.get(
        "https://www.computer.org/csdl/search/default?queryState=%7B%22basicSearchTextSubmitted%22:%5B%22%22,null%5D,%22searchResultLimit%22:%5B10,100%5D%7D")
    time.sleep(2)
    close_popup = driver.find_element(By.CLASS_NAME, "osano-cm-denyAll")
    close_popup.click()
    time.sleep(2)
    # display100 = driver.find_element(By.ID, "limitDropdown")
    # toto = driver.find_element(By.XPATH, "//*[contains(text(), '100')]")
    # display100.click()
    # toto.send_keys(Keys.TAB)
    # toto.click()
    # time.sleep(20)
    # root = driver.find_element(By.XPATH, "/*")
    # root.send_keys(Keys.CONTROL, Keys.SHIFT, "c")
    # time.sleep(1)
    # root.send_keys(Keys.CONTROL, Keys.SHIFT, "i")
    # time.sleep(5)
    search_bar = driver.find_element(By.ID, "basic-search-input")
    # search_bar = driver.find_element(By.XPATH, "//input[@id ='basic-search-mobile-input']")
    time.sleep(1)
    search_bar.click()
    search_bar.send_keys('("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")')
    search_bar.send_keys(Keys.ENTER)
    time.sleep(3)

    is_last_page = False
    file_output = open("../../../old/1_initial_request_articles/acm_digital_library.json", "w", encoding="utf-8")
    json_content_output = []
    counter = 0
    while not is_last_page:
        time.sleep(3)
        articles_html = driver.find_elements(By.XPATH, ".//li[@class ='search__item issue-item-container']")
        for article in articles_html:
            counter += 1

            title = article.find_element(By.TAG_NAME, "h5").text

            year = \
            article.find_element(By.XPATH, ".//div[@class ='bookPubDate simple-tooltip__block--b']").text.split(' ')[1]

            authors = []
            try:
                authors_list = article.find_elements(By.XPATH, ".//span[@class ='hlFld-ContribAuthor']")
                for author in authors_list:
                    authors.append({"lastName": author.text.split(' ')[-1]})
            except:
                pass

            doi = ""
            try:
                doi = article.find_element(By.XPATH, ".//a[@class ='issue-item__doi dot-separator']").text
            except:
                pass
            # print(title + " - " + year + " - " + ','.join(authors) + " - " + doi)
            json_content_output.append({
                "title": title,
                "authors": authors,
                "publicationYear": year,
                "doi": doi,
            })
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, "ul + span")
            next_page.click()
        except:
            is_last_page = True
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)

    time.sleep(200)


scrap_computer()
