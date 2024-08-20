import time
import json
import re

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def scrap_nested_page(link):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1200')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    driver.get(link)
    try:
        close_popup = driver.find_element(By.CLASS_NAME, "osano-cm-denyAll")
        close_popup.click()
    except:
        pass

    doi = ""

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='article-metadata']/div/a"))
        )
        doi = driver.find_element(By.XPATH, "//div[@class='article-metadata']/div/a").text
    except:
        pass
    driver.quit()

    return "https://doi.org/" + doi


def scrap_computer(request, path):
    print("COMPUTER STRATING SCRAPING")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1200')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    driver.get(
        "https://www.computer.org/csdl/search/default?queryState=%7B%22basicSearchTextSubmitted%22:%5B%22%22,null%5D,%22searchResultLimit%22:%5B10,100%5D%7D")
    time.sleep(5)
    # try:
    #     close_popup = driver.find_element(By.CLASS_NAME, "osano-cm-denyAll")
    #     close_popup.click()
    # except:
    #     pass
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
    search_bar.send_keys(request)
    search_bar.send_keys(Keys.ENTER)
    time.sleep(1)

    is_last_page = False
    file_output = open(path + "computer.json", "w", encoding="utf-8")
    json_content_output = []
    counter = 0
    while not is_last_page:
        time.sleep(3)
        articles_html = driver.find_elements(By.XPATH, ".//div[@class ='search-result']")
        # print(len(articles_html))
        # for article in articles_html:
        #     print(article.get_attribute("innerHTML"))
        for article in articles_html:
            pass
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "article-title"))
            )
            counter += 1
            not_good = True
            title = ""
            while not_good:
                try:
                    # print(article.get_attribute("innerHTML"))
                    title = article.find_element(By.CLASS_NAME, "article-title").text
                    not_good = False
                except:
                    print("Title not found")
                    print(article)
                    not_good = False
                    # raise Exception("EXCEPTION " + str(counter))
            year = ""
            try:
                year = re.search(r'\d{4}|$', article.find_element(By.XPATH, ".//div[@class ='metadata']").text).group()
            except:
                print("EXCEPTION " + str(counter))
            authors = []
            try:
                authors_list = article.find_elements(By.XPATH, ".//button[@class ='article-author']")
                for author in authors_list:
                    authors.append({"lastName": author.text.split(' ')[-1]})
            except:
                pass
            doi = scrap_nested_page(article.find_element(By.CLASS_NAME, "article-title").get_attribute("href"))
            json_content_output.append({
                "title": title,
                "authors": authors,
                "publicationYear": year,
                "doi": doi,
                "source": "https://www.computer.org/csdl",
            })
            print(counter)
            # time.sleep(2)
        # try:
        # try:
        #     WebDriverWait(driver, 30).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, "osano-cm-denyAll"))
        #     )
        #     close_popup = driver.find_element(By.CLASS_NAME, "osano-cm-denyAll")
        #     close_popup.click()
        # except:
        #     pass
        for elem in driver.find_elements(By.XPATH, "//a[@aria-label='Next']"):
            print(elem.get_attribute("innerHTML"))
        try:
            if driver.find_elements(By.XPATH, "//a[@aria-label='Next']")[1].get_attribute("aria-disabled") == "true":
                is_last_page = True
        except:
            pass
        if not is_last_page:
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']"))
                )
                next_page = driver.find_elements(By.XPATH, "//a[@aria-label='Next']")[1]
                # next_page = next_page.find_element(By.XPATH, './..')
                next_page.send_keys(Keys.ENTER)
                print("NEXT")
            except:
                # is_last_page = True
                print("fuck")
        # except:
        #     is_last_page = True
    driver.quit()
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)

    print("COMPUTER FINISHED SCRAPING")
