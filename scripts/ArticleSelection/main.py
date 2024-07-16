from scripts.ArticleSelection.Step1_Scrapping.main_step1 import main_scrap_databases
from scripts.ArticleSelection.Step2_DuplicateRemoval.main_step2 import main_remove_duplicates
from scripts.ArticleSelection.Step3_CSVGeneration.main_step3 import main_csv_generation

REQUEST = ('("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ('
           '"internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")')


def main():
    main_scrap_databases(REQUEST)
    # main_remove_duplicates()
    # main_csv_generation()


if __name__ == '__main__':
    main()
