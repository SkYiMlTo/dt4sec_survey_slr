import os
import json


def remove_duplicates(input_path, output_path):
    articles_known = []
    input_filenames = next(os.walk(input_path), (None, None, []))[2]
    for input_filename in input_filenames:
        counter = 0
        output_without_duplicates = []
        file_input = json.load(open(input_path + input_filename, "r", encoding="utf-8"))
        for article in file_input:
            if article["title"] not in articles_known:
                articles_known.append(article["title"])
                output_without_duplicates.append(article)
                counter += 1
        print(input_filename + " has " + str(counter) + " articles")
        output_filename = open(output_path + input_filename, "w", encoding="utf-8")
        json.dump(output_without_duplicates, output_filename, ensure_ascii=False, indent=4)


def main_remove_duplicates(path):
    input_path = path + "step1/"
    output_path = path + "step2/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    remove_duplicates(input_path, output_path)
