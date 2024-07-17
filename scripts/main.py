from scripts.ArticleSelection.main_article_selection import main_article_selection
from scripts.DataVisualization.main_data_visualization import main_data_visualization

import datetime
import os


REQUEST = ('("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ('
           '"internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")')
ROOT_STORAGE = "../output/"


def destination_folder():
    return str(datetime.datetime.now()).replace(':', '-')


def main():
    # Define where the results of execution will be stored #
    dest_folder = destination_folder()
    os.mkdir(ROOT_STORAGE + dest_folder)
    path = ROOT_STORAGE + dest_folder + "/"
    main_article_selection(REQUEST, path)
    main_data_visualization(path)


if __name__ == '__main__':
    main()
