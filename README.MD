## Welcome to literature crawler

The main goal of this python application is to assist performing an SLR for literature reviews.
By searching into popular database engine with one query, this tool is capable of giving you a csv file of all articles retrieved in a CSV file.
It also generates some plots with the data gathered.


This code is used for my PhD about Digital Twin for cybersecurity purposes. It is used to track the state of the art.

## What happens

This tool gather data from a request and summarize the results following these steps :

1. Scrapping

    First, the request is performed on databases to scrap all the articles. Here are the databases used:
    - [ACM DL](https://dl.acm.org/)
    - [Computer](https://www.computer.org/csdl)
    - [Springer Link](https://link.springer.com/)
    
    The data collected in store in JSONs, their structure is detailed [here](#structure-of-files-generated).
    Each website scrapped has its own JSON created.<br /><br />

2. Remove duplicates

    Then duplicates are removed from the data collected.
    All the JSONs are parsed, and we only keep one instance of every item gathered.<br /><br />

3. Aggregate data

    Since all data is ready to be merged, it is gathered in a [CSV file](#structure-of-files-generated).<br /><br />
    
4. Remove item without DOIs

    To ensure the quality of the data gathered we then remove items without a [DOI](https://www.doi.org/).<br /><br />

5. Generate graphs

    For further analysis, some graphs are generated.
   - Number of articles over the years
   - Authors with the most publications

## How to use it

This repository is automatically run with GitHub actions.
If you want to use it you can clone the project and edit the request in scripts/main.py.

You can either run the project manually (workflow_dispatch) or it will be executed every monday at 8AM (UTC).
To edit the configuration, change the .github/workflows/main.yml.

All the files generated from a run will be stored in "output" and the child directory will be named after the date and time the code has been run.
You will be able to find the "articleSelection" folder containing all steps described above as well as "dataVisualization" containing the plots created.

## Technical details - Structure of the repository
### Tree
Here is the structure of the repository:
```bash
/
├── .github/workflows
├── scripts
│   ├── Article selection
│   │   ├── Main.py
│   │   ├── Step 1 - Scrapping
│   │   ├── Step 2 - Duplicate removal
│   │   ├── Step 3 - Data aggregation
│   │   └── Step 4 - Remove items without a DOI
│   └── Data Visualization
│       ├── Articles per country
│       └── Year repartition
├── output
│   ├── YY/MM/DD
│   │   ├── Step 1 - JSONs
│   │   │   ├── Database 1
│   │   │   ├── Database 2
│   │   │   └── ...
│   │   ├── Step 2 - JSONs
│   │   │   ├── Database 1
│   │   │   ├── Database 2
│   │   │   └── ...
│   │   ├── Step 3 - CSV file
│   │   │   └── File
│   │   ├── Step 4 - CSV file
│   │   │   └── File
│   │   └── Data visualization
│   │   │   ├── Plot 1
│   │   │   ├── Plot 2
│   │   │   └── ...
│   └── YY/MM/DD
│       └── ...
└── requirements.txt
```

### Explanations
There is 3 mains components as follows:
1. GitHub workflow

    A GitHub workflow is running every monday at 8 AM (UTC) in this repository tracking the evolution of the state of the art.
    It can also be run manually in the GitHub actions (with workflow_dispatch).

    In the main.yml you can find all the steps to autonomously run the project.<br /><br />

2. Python scripts

    Here is all the code used to scrap online databases, generate json, csv files and perform actions on the data gathered.
It also generates the plots.

    This code is working here with this request :
    ```sql
    ("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")
    ```
    To edit this request you need to change it in the scripts/main.py.<br /><br />

3. Output files

    Here is where all files generated are stored.
    When the code is run, each execution has its own folder created with all its file in it.
    The name of the folder is the date and time the code has been executed (starting time).

## Structure of files generated
### JSON
Here is the architecture of each article in the JSON files :

```json
{
  "title": "...",
  "authors": [{
    "lastName" : "..."
  },{
    "lastName" : "..."
  },
  "..."
  ],
  "publicationYear": "...",
  "doi": "...",
  "source": "..."
}
```
### CSV
Here is the architecture of each article in the CSV files :

```csv
title, publicationYear, doi, authors, source
```

All the names are self-explanatory, except source.
The source in CSV files are to show with which engine the data was acquired from, like computer, ACM DL, ...
Note that, the authors names are separated with comas.

## Contact

If you have any suggestion, question, or whatever you want to talk about, feel free to contact me!
- Mail: [hugo@bourreau.ovh](mailto:hugo@bourreau.ovh)
- Discord: sky_imlto

I speak French and English :)

## LICENSE
This project is under MIT license, more [here](./LICENSE.MD).
