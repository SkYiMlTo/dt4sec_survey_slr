from yearsRepartition.main_years_repartition import main_years_repartition
from authorsContribution.main_authors_contribution import main_authors_contribution
from createReadme.main_create_readme import main_create_readme


def main_data_visualization(path):
    main_years_repartition(path)
    main_authors_contribution(path)
    main_create_readme(path)
