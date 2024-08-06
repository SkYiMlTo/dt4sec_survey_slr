import csv
import os


def remove_empty_doi(path):
    # Input and output file paths
    input_path = path + "step3/"
    output_path = path + "step4/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    input_file = input_path + 'articles.csv'
    output_file = output_path + 'articles.csv'

    # Read the CSV file and filter out rows with empty DOIs
    with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8',
                                                                      newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write the header to the output file
        writer.writeheader()

        # Filter rows and write to the output file
        for row in reader:
            if row['DOI'].strip():  # Check if DOI is not empty
                writer.writerow(row)
