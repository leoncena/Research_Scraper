import time
import csv
import json
import pandas as pd
import os

import pandas as pd
from Research_Scraper_Code.Research_Scraper import ResearchScraper

# test urls
url_ieee = 'https://ieeexplore.ieee.org/document/7887648'
url_springer = 'https://link.springer.com/article/10.1007/s12525-020-00445-0'
url_doi = 'https://doi.org/10.1007/978-0-387-73947-2_8'
url_elsevier = 'https://www.sciencedirect.com/science/article/pii/S2451929420300851?via%3Dihub'
url_springer2 = 'https://doi.org/10.1007/s00450-009-0054-z'
test_urls = [url_ieee, url_springer]

scraper = ResearchScraper()


def test_scrape_url():
    test_url = url_springer2
    start = time.time()
    result = scraper.scrape_publication_by_url(test_url, params=['full'])
    print('\nTest Start for: ', test_url, '\n______________________________________________________')
    for key, value in result.items():
        print(key, ': \n', '> ', value, '\n')
    end = time.time()
    print(f'Total time : {end - start}')


# test_scrape_url()


def test_scrape_doi():
    test_doi = '10.1007/s11943-021-00292-1'
    start = time.time()
    result = scraper.scrape_publication_by_doi(test_doi, params=['full'])
    print_it = False
    if print_it:
        if result is not None:
            print('\nTest Start for: ', test_doi, '\n______________________________________________________')
            for key, value in result.items():
                print(key, ': \n', '> ', value, '\n')

            end = time.time()
            print(f'Total time : {end - start}')


# test_scrape_doi()


def test_and_write_multiple_pubs():
    results = []
    results.append(scraper.scrape_publication_by_url(url_ieee, params=['full']))
    results.append(scraper.scrape_publication_by_url(url_springer, params=['full']))

    write_results(results)


def write_results(results, name):
    if results is not None:
        with open(f'{name}.json', 'w') as f:
            json.dump(results, f, indent=4)


# test_and_write_multiple_pubs()


def load_publications_from_csv():
    data = 'data/publications_without_abstract.csv'

    with open(data) as f:
        df = pd.read_csv(f, sep=';')
    return df


def get_all_dois():
    df = load_publications_from_csv()
    dois = df['doi']
    # remove NaNs
    dois = dois.dropna()
    dois.tolist()
    return dois


def scrape_sample_of_dois():
    dois = get_all_dois()

    # get a sample of 10 from dois
    sample = dois.sample(n=50)
    print(sample)
    results = []

    for doi in sample:
        print(f'Scraping {doi}')
        start = time.time()
        result = scraper.scrape_publication_by_doi(doi, params=['full'])
        end = time.time()
        print(f'Total time : {end - start}')
        results.append(result)
    write_results(results, 'sample')


scrape_sample_of_dois()
