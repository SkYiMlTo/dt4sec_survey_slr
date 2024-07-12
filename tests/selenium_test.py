import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)

driver.get("https://google.com")
time.sleep(10)


# button = driver.find_element(By.CLASS_NAME, u"infoDismiss")
# driver.implicitly_wait(10)
# ActionChains(driver).move_to_element(button).click(button).perform()

# try:
#     search_box = driver.find_element(By.NAME, "q")
#     search_box.clear()
#     search_box.send_keys("John Doe")  # enter your name in the search box
#     search_box.submit()  # submit the search
#     results = driver.find_elements(By.XPATH, "//*[@id='b_tween']/span")
#     for result in results:
#         text = result.text.split()[1]  # extract the number of results
#         print(text)
#         # save it to a file
#         with open("results.txt", "w") as f:
#             f.write(text)
# except Exception as e:
#     print(f"An error occurred: {e}")
