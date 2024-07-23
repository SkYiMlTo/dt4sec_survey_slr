import matplotlib.pyplot as plt


# Function to read years and counts from a text file
def read_years_and_counts_from_file(filename):
    years_counts = []
    with open(filename, 'r') as file:
        for line in file:
            year, count = line.strip().split(',')
            year, count = int(year), int(count)
            years_counts.extend([year] * count)
    return years_counts


# Function to plot the histogram
def plot_years_histogram(years_counts, output_file):
    plt.figure(figsize=(12, 8))
    plt.hist(years_counts, bins=range(min(years_counts), max(years_counts) + 1), edgecolor='black', alpha=0.7)
    plt.title('Publication per year about Digital Twin on IEEEXplore')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.grid(axis='y', alpha=0.75)

    # Rotate x-axis labels for better readability
    plt.xticks(range(min(years_counts), max(years_counts) + 1), rotation=45)

    plt.tight_layout()  # Adjust layout to make room for the rotated labels
    plt.savefig(output_file)
    plt.close()
    print(f"Histogram saved as {output_file}")


# Main script
input_file = 'ieeexplore_articles_per_year_new.txt'  # Replace with your file path
output_file = 'articles_per_year_new.png'

years_counts = read_years_and_counts_from_file(input_file)
plot_years_histogram(years_counts, output_file)
