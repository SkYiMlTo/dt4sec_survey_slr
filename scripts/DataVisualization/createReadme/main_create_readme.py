def main_create_readme(path):
    plot_filename_years = "DataVisualization/plt_years_repartition.png"
    plot_filename_authors = "DataVisualization/plt_top_10_authors.png"
    readme_content = \
        f"""
# Publication Data Analysis

## Distribution of Publications by Year
![Publication Years Distribution]({plot_filename_years})

## Top 10 Authors with Most Publications
![Top 10 Authors]({plot_filename_authors})
"""

    # Write the README.MD file
    with open(path + 'README.MD', 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme_content)
