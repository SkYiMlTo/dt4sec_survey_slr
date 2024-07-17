import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def scrap_acm_digital_library(request, path):
    print("ACMDL STARTING SCRAPING")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    driver.get(
        "https://dl.acm.org/action/doSearch?AllField=%28%22Digital+Twin%22+OR+%22Digital+Twins%22%29+AND+%28%22cyber+attacks%22+OR+%22cybersecurity%22+OR+%22cyber-security%22%29+AND+%28%22internet+of+things%22+OR+%22IoT%22+OR+%22CPS%22+OR+%22cyber-physical+systems%22+OR+%22cyber-physical+systems%22%29&startPage=0&pageSize=50")
    time.sleep(2)
    close_popup = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll")
    close_popup.click()
    # search_bar = driver.find_element(By.NAME, "AllField")
    # search_bar.send_keys('("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")')
    # search_bar.send_keys(Keys.ENTER)
    # time.sleep(3)
    is_last_page = False
    file_output = open(path + "acm_digital_library.json", "w", encoding="utf-8")
    json_content_output = []
    counter = 0
    while not is_last_page:
        time.sleep(3)
        articles_html = driver.find_elements(By.XPATH, ".//li[@class ='search__item issue-item-container']")
        for article in articles_html:
            counter += 1

            title = article.find_element(By.TAG_NAME, "h5").text

            year = article.find_element(By.XPATH, ".//div[@class ='bookPubDate simple-tooltip__block--b']").text.split(' ')[1]

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
    driver.quit()
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)
    print("ACMDL FINISHED SCRAPING")
