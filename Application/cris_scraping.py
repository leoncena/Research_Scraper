import json
import time

import pandas as pd

from Research_Scraper_Code.Research_Scraper import ResearchScraper

scraper = ResearchScraper()


def load_publications_from_csv():
    data = 'data/publications_without_abstract.csv'

    with open(data) as f:
        df = pd.read_csv(f, sep=';')
    return df


def get_all_dois(df):
    dois = df['doi']
    # remove NaNs
    dois = dois.dropna()
    dois.tolist()
    return dois


def write_results(results, name):
    if results is not None:
        with open(f'exports/scrapings/{name}.json', 'w') as f:
            json.dump(results, f, indent=4)


def scrape_sample_of_dois(dois, n):
    # get a sample of 10 from dois
    sample = dois.sample(n)
    # print(sample)
    results = []

    for doi in sample:
        print(f'Scraping {doi}')
        start = time.time()
        result = scraper.scrape_publication_by_doi(doi, params=['full'])
        end = time.time()
        print(f'Total time : {end - start}')
        old_len = len(results)
        results.append(result)
        print(f'\n \t  >>>>>> added new result, n went from {old_len} to n={len(results)}')
        # print(f'\t -> Results: {results}')

    # write_results(results, f'sample_{time.strftime("%Y_%m_%d__%H_%M")}')
    return results


def scrape_publication_by_doi_list(doi_list, params=['full']):
    print(f'Time of scrape start: {time.strftime("%Y_%m_%d__%H_%M")}')
    results = []
    for idx, doi in enumerate(doi_list):
        scraping_log = f'>>> Scraping {doi} #{idx}'
        print('\x1b[6;30;42m' + scraping_log + '\x1b[0m')
        result = scraper.scrape_publication_by_doi(doi, params)
        print(f'>>>> Scraping {doi} done')
        results.append(result)
        print(f'>>>> Scraping {doi} added to results')
    print(f'>>>> Scraping {len(doi_list)} publications done')
    write_results(results, f'scrapings_{time.strftime("%Y_%m_%d__%H_%M")}')
    print(f'Time of scrape end: {time.strftime("%Y_%m_%d__%H_%M")}')
    return results


# main
if __name__ == '__main__':
    # Big scraping
    df_publications = load_publications_from_csv()
    publication_dois = get_all_dois(df_publications)
    print(f'There are {len(publication_dois)} publication dois')
    # doi_list_sample = publication_dois.sample(n=1000)
    scraping_results = scrape_publication_by_doi_list(publication_dois, params=['full'])

    print('Fertig')
    print('')
    # url_test = 'https://link.springer.com/article/10.1007/s40558-015-0037-9'
    # result = scraper.scrape_publication_by_url(url_test, params=['full'])
    # print(result.get('keywords'))
