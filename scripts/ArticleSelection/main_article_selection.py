from scripts.ArticleSelection.Step1_Scrapping.main_step1 import main_scrap_databases
from scripts.ArticleSelection.Step2_DuplicateRemoval.main_step2 import main_remove_duplicates
from scripts.ArticleSelection.Step4_CSVGeneration.main_step4 import main_excel_generation
from scripts.ArticleSelection.Step3_RemoveNoDOI.main_step3 import remove_empty_doi
import os


def main_article_selection(request, path):
    path += "articleSelection/"
    if not os.path.exists(path):
        os.mkdir(path)
    main_scrap_databases(request, path)
    main_remove_duplicates(path)
    remove_empty_doi(path)
    main_excel_generation(path)

