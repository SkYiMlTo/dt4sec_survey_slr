from ArticleSelection.Step1_Scrapping.main_step1 import main_scrap_databases
from ArticleSelection.Step2_DuplicateRemoval.main_step2 import main_remove_duplicates
from ArticleSelection.Step3_CSVGeneration.main_step3 import main_csv_generation
import os


def main_article_selection(request, path):
    path += "articleSelection/"
    if not os.path.exists(path):
        os.mkdir(path)
    main_scrap_databases(request, path)
    main_remove_duplicates(path)
    main_csv_generation(path)
