import matplotlib.pyplot as plt


# Function to read years from a text file
def read_years_from_file(filename):
    with open(filename, 'r') as file:
        years = [int(line.strip()) for line in file]
    return years


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
def plot_years_histogram(years, output_file):
    plt.figure(figsize=(12, 8))
    plt.hist(years, bins=range(min(years), max(years) + 1), edgecolor='black', alpha=0.7)
    plt.title('Publication per year about Digital Twin on IEEEXplore & Computer')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.grid(axis='y', alpha=0.75)

    # Rotate x-axis labels for better readability
    plt.xticks(range(min(years), max(years) + 1), rotation=45)

    plt.tight_layout()  # Adjust layout to make room for the rotated labels
    plt.savefig(output_file)
    plt.close()
    print(f"Histogram saved as {output_file}")


# Main script
file1 = 'computer_years2.txt'  # Replace with your first file path
file2 = 'ieeexplore_articles_per_year_new.txt'  # Replace with your second file path
output_file = 'combined_years_histogram.png'

# Read data from both files
years = read_years_from_file(file1)
years_counts = read_years_and_counts_from_file(file2)

# Combine the data
combined_years = years + years_counts

# Plot the combined data
plot_years_histogram(combined_years, output_file)
