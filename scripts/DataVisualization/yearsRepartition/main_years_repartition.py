import csv
import matplotlib.pyplot as plt
import os


def years_repartition(input_path, output_path):
    publication_years = []

    # Read the CSV file
    with open(input_path, 'r', encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip the header
        next(csvreader)

        # Extract publication years
        for row in csvreader:
            publication_year = row[2]
            publication_years.append(publication_year)

    # Count the frequency of each year
    year_counts = {}
    for year in publication_years:
        if year in year_counts:
            year_counts[year] += 1
        else:
            year_counts[year] = 1

    # Sort years for plotting
    sorted_years = sorted(year_counts.keys())
    sorted_counts = [year_counts[year] for year in sorted_years]

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(sorted_years, sorted_counts, color='skyblue')
    plt.xlabel('Publication Year')
    plt.ylabel('Number of Publications')
    plt.title('Distribution of Publications by Year')
    plt.savefig(output_path + "plt_years_repartition.png")
    plt.show()


def main_years_repartition(path):
    input_path = path + "articleSelection/step3/articles.csv"
    output_path = path + "dataVisualization/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    years_repartition(input_path, output_path)


# main_years_repartition("../../../output/2024-07-17 14-38-25.820397/")
