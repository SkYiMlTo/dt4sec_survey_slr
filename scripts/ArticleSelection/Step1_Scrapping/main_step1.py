import logging
import os
import threading
import time
from scripts.ArticleSelection.Step1_Scrapping.acm_digital_library import scrap_acm_digital_library
from scripts.ArticleSelection.Step1_Scrapping.computer import scrap_computer
from scripts.ArticleSelection.Step1_Scrapping.scrap_springer_link import scrap_springler


def thread_function():
    print("")
    time.sleep(2)
    print("b")


def main_scrap_databases(request, path):
    path = path + "step1/"
    if not os.path.exists(path):
        os.mkdir(path)
    x = threading.Thread(target=scrap_acm_digital_library, args=(request, path), daemon=False)
    y = threading.Thread(target=scrap_computer, args=(request, path), daemon=False)
    z = threading.Thread(target=scrap_springler, args=(request, path), daemon=False)
    # x.start()
    # y.start()
    z.start()
    # x.join()
    # y.join()
    z.join()
    print("All Scrapping Completed")
