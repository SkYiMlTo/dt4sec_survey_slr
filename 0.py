import json
from math import ceil
import requests
from computer import Computer
from ieee_xplore import IeeeXplore
from scopus import Scopus
from semantic_scholar import SemanticScholar


def compare_ieee_computer():
    ieee = json.load(open("0_initial_request_raw/ieeexplore.json", "r", encoding='utf-8'))
    computer = json.load(open("0_initial_request_raw/computer_raw.json", "r", encoding='utf-8'))
    ieee_articles_names = []
    for article in ieee["records"]:
        ieee_articles_names.append(article["articleTitle"])
    computer_articles_names = []
    for article in computer["results"]:
        computer_articles_names.append(article["title"])
    print(ieee_articles_names)
    print(computer_articles_names)
    print(len(set(ieee_articles_names).intersection(computer_articles_names)))


def main():
    print("Fetching IEEE XPLORE... ", end='')
    ieee = IeeeXplore()
    ieee.request_all_infos_ieeexplore()
    print("done.")

    print("Fetching Computer... ", end='')
    computer = Computer()
    computer.request_all_infos_computer()
    print("done.")

    print("Fetching Scopus... ", end='')
    sc = Scopus()
    sc.request_all_infos_scopus()
    print("done.")

    print("Fetching Semantic Scholar... ", end='')
    ss = SemanticScholar()
    ss.request_all_infos_semantic_scholar()
    print("done.")


if __name__ == '__main__':
    main()
