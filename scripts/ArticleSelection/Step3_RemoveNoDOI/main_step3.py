import csv
import os
import json

def remove_empty_doi(path):
    # Input and output file paths
    input_path = path + "step2/"
    output_path = path + "step3/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    # input_file = input_path + 'articles.csv'
    # output_file = output_path + 'articles.csv'

    remove_empty_doi_all(input_path, output_path)
    # # Read the CSV file and filter out rows with empty DOIs
    # with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8',
    #                                                                   newline='') as outfile:
    #     reader = csv.DictReader(infile)
    #     fieldnames = reader.fieldnames
    #     writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    #
    #     # Write the header to the output file
    #     writer.writeheader()
    #
    #     # Filter rows and write to the output file
    #     for row in reader:
    #         if row['DOI'].strip():  # Check if DOI is not empty
    #             writer.writerow(row)

def remove_empty_doi_all(input_path, output_path):
    articles_known = []
    input_filenames = next(os.walk(input_path), (None, None, []))[2]

    for input_filename in input_filenames:
        output_without_duplicates = []
        file_input = json.load(open(input_path + input_filename, "r", encoding="utf-8"))

        for article in file_input:
            # Check if the article has a DOI and if the title is not already in the list
            if "doi" in article and article["doi"] and article["title"] not in articles_known:
                articles_known.append(article["title"])
                output_without_duplicates.append(article)


        output_filename = open(output_path + input_filename, "w", encoding="utf-8")
        json.dump(output_without_duplicates, output_filename, ensure_ascii=False, indent=4)
