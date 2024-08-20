import os
import csv
import json


def csv_generation(input_path, output_path):
    fields = ['Title', 'Authors', 'Year of Publication', 'DOI', "Source"]

    input_filenames = next(os.walk(input_path), (None, None, []))[2]

    with open(output_path + "articles.csv", 'w', newline='', encoding="utf-8") as input_file:
        csvwriter = csv.writer(input_file)
        csvwriter.writerow(fields)
        for input_filename in input_filenames:
            file_input = json.load(open(input_path + input_filename, "r", encoding="utf-8"))
            for item in file_input:
                title = item['title']
                authors = ', '.join([author['lastName'] for author in item['authors']]) if item[
                    'authors'] else 'No authors'
                publication_year = item['publicationYear']
                doi = item['doi']
                source = item['source']
                csvwriter.writerow([title, authors, publication_year, doi, source])


def main_csv_generation(path):
    input_path = path + "step2/"
    output_path = path + "step3/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    csv_generation(input_path, output_path)
