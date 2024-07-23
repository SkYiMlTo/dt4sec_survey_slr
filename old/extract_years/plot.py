import matplotlib.pyplot as plt


# Function to read years from a text file
def read_years_from_file(filename):
    with open(filename, 'r') as file:
        years = [int(line.strip()) for line in file]
    return years


# Function to plot the histogram
def plot_years_histogram(years, output_file):
    plt.figure(figsize=(12, 8))
    plt.hist(years, bins=range(min(years), max(years) + 1), edgecolor='black', alpha=0.7)
    plt.title('Publication per year about Digital Twin on Computer')
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
input_file = 'computer_years2.txt'  # Replace with your file path
output_file = 'years_histogram_relevant.png'

years = read_years_from_file(input_file)
plot_years_histogram(years, output_file)
