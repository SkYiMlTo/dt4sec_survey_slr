import json


def normalisation_ieee_xplore():
    file_input = json.load(open("0_initial_request_raw/ieeexplore_raw.json", "r", encoding="utf-8"))
    file_output = open("1_initial_request_articles/ieeexplore.json", "w", encoding="utf-8")
    json_content_output = []
    for elem in file_input["records"]:
        authors = []
        if elem["authors"]:
            for author in elem["authors"]:
                authors.append({"lastName": author["lastName"]})
        json_content_output.append({
            "title": elem["articleTitle"],
            "authors": authors,
            "publicationYear": elem["publicationYear"],
        })
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)


def normalisation_computer():
    file_input = json.load(open("0_initial_request_raw/computer_raw.json", "r", encoding="utf-8"))
    file_output = open("1_initial_request_articles/computer.json", "w", encoding="utf-8")
    json_content_output = []
    for elem in file_input["results"]:
        authors = []
        if elem["authors"]:
            for author in elem["authors"]:
                authors.append({"lastName": author["surname"]})
        json_content_output.append({
            "title": elem["pubTitle"],
            "authors": authors,
            "publicationYear": elem["year"],
        })
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)


def normalisation_scopus():
    file_input = json.load(open("0_initial_request_raw/scopus_raw.json", "r", encoding="utf-8"))
    file_output = open("1_initial_request_articles/scopus.json", "w", encoding="utf-8")
    json_content_output = []
    for elem in file_input["items"]:
        authors = []
        if elem["authors"]:
            for author in elem["authors"]:
                authors.append({"lastName": author["preferredName"]["last"]})
        json_content_output.append({
            "title": elem["title"],
            "authors": authors,
            "publicationYear": elem["pubYear"],
        })
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)


def normalisation_semantic_scholar():
    file_input = json.load(open("0_initial_request_raw/semantic_scholar_raw.json", "r", encoding="utf-8"))
    file_output = open("1_initial_request_articles/semantic_scholar.json", "w", encoding="utf-8")
    json_content_output = []
    for elem in file_input["results"]:
        authors = []
        if elem["authors"]:
            for author in elem["authors"]:
                authors.append({"lastName": author[0]["structuredName"]["lastName"]})
        json_content_output.append({
            "title": elem["title"]["text"],
            "authors": authors,
            "publicationYear": elem["year"]["text"],
        })
    json.dump(json_content_output, file_output, ensure_ascii=False, indent=4)


def normalisation_main():
    normalisation_ieee_xplore()
    normalisation_computer()
    normalisation_scopus()
    normalisation_semantic_scholar()


if __name__ == '__main__':
    normalisation_main()
