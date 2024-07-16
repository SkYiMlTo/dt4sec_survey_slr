from os import walk
import json


def main_remove_duplicates():
    articles_known = []
    input_filenames = next(walk("../../../old/1_initial_request_articles"), (None, None, []))[2]
    for input_filename in input_filenames:
        counter = 0
        output_without_duplicates = []
        file_input = json.load(open("1_initial_request_articles/" + input_filename, "r", encoding="utf-8"))
        for article in file_input:
            if article["title"] not in articles_known:
                articles_known.append(article["title"])
                output_without_duplicates.append(article)
                counter += 1
        print(input_filename + " has " + str(counter) + " articles")
        output_filename = open("2_remove_duplicates/" + input_filename, "w", encoding="utf-8")
        json.dump(output_without_duplicates, output_filename, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    remove_duplicates_main()
