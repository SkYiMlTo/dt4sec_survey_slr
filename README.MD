## Welcome to literature crawler

The main goal of this python application is to assist performing an SLR for literature reviews.
By searching into popular database engine with one query, this tool is capable of giving you the list
of articles of each database. In a second step, it removes any duplicate and present you the results in
a CSV file (as well as a JSON file) easy to read and parse.

## Structure of the repository
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
│   │   └── Step 3 - CSV generation
│   └── Data Visualization
│       ├── Articles per country
│       └── Year repartition
├── output
│   ├── YY/MM/DD
│   │   ├── Step 1 - JSONs
│   │   │   ├── Database 1
│   │   │   ├── Database 2
│   │   │   ├── Database 3
│   │   │   └── ...
│   │   ├── Step 2 - JSONs
│   │   │   ├── Database 1
│   │   │   ├── Database 2
│   │   │   ├── Database 3
│   │   │   └── ...
│   │   ├── CSV file
│   │   └── Data visualization
│   └── YY/MM/DD
│       └── ...
└── requirements.txt
```

### Explanations
There is 3 mains components as follows:
1. GitHub workflow

This code is used for my PhD about Digital Twin for cybersecurity purposes. It is used to track the state of the art.
There is a GitHub workflow running every week in this repository tracking the evolution of the state of the art.

This code is working autonomously with this request :
```sql
("Digital Twin" OR "Digital Twins") AND ("cyber attacks" OR "cybersecurity" OR "cyber-security") AND ("internet of things" OR "IoT" OR "CPS" OR "cyber-physical systems" OR "cyber-physical systems")
```

To edit this request you need to change it in the main.py.

2. Python scripts

Here is all the code used to scrap online databases, generate json and csv files. It also generates various plots for
information.

3. Output files

Here is where all files generated are stored. 

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
  "doi": "..."
}
```
### CSV
Here is the architecture of each article in the CSV files :

```csv
title, publicationYear, doi, authors
```

## Automation
























