from scripts.DataVisualization.yearsRepartition.main_years_repartition import main_years_repartition
from scripts.DataVisualization.authorsContribution.main_authors_contribution import main_authors_contribution
from scripts.DataVisualization.createReadme.main_create_readme import main_create_readme


def main_data_visualization(path):
    main_years_repartition(path)
    main_authors_contribution(path)
    main_create_readme(path)
