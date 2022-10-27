"""
Script using the research scraper on cris data
"""
import json
import time

import pandas as pd
from Research_Scraper_Code import utils

from Research_Scraper_Code.Research_Scraper import ResearchScraper

scraper = ResearchScraper()


def get_all_dois(df):
    dois = df['doi']
    # remove NaNs
    dois = dois.dropna()
    dois.tolist()
    return dois



def scrape_sample_of_dois(dois, n):
    # only for debugging purposes
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

    utils.write_results(results, f'sample_{time.strftime("%Y_%m_%d__%H_%M")}')
    return results


def scrape_cris_publications():
    # Big scraping
    df_publications = utils.load_publications_from_csv()
    publication_dois = get_all_dois(df_publications)
    print(f'There are {len(publication_dois)} publication dois')
    # doi_list_sample = publication_dois.sample(n=1000)
    scraping_results = scraper.scrape_publication_by_doi_list(publication_dois, params=['full'])
    return scraping_results


# main
if __name__ == '__main__':
    # possible usages below in comments

    # init scraper
    scraper = ResearchScraper()

    # Big cris scraping
    # cris_scraping_results = scrape_cris_publications()

    # download one pdf live
    # scraper.download_pdf_of_publication_by_doi_live('10.1007/s00180-017-0742-2')

    # download list pdfs live
    # doi_list = ['10.1007/s10796-009-9214-8','10.1007/s11147-010-9056-z', '10.1007/BF01205357']
    # scraper.download_pdf_of_publications_by_doi_list_live(doi_list)

    # download all pdfs
    # cris_scraping_results = scrape_cris_publications()
    # scraping_results = utils.load_and_clean_scraping_results(filename='scrapings_2022_10_21__03_38')
    # scraper.download_pdf_of_publications_by_scraping_results(scraping_results)

    # scrape 5 publications as example
    df_publications = utils.load_publications_from_csv()
    publication_dois = get_all_dois(df_publications)
    scraper.scrape_publication_by_doi_list(publication_dois[0:5], params=['full'])

    # Scrape one publication by url
    # url_test = 'https://linkinghub.elsevier.com/retrieve/pii/S2405896316326283'
    # result = scraper.scrape_publication_by_url(url_test, params=['full'])
    # print(result.get('keywords'))

    # scholarly example
    # prof_gieseke = scraper.search_author_information_from_google_scholar('Fabian Gieseke Münster')
    # print(prof_gieseke)
    # prof gieseke interests
    # print(prof_gieseke.get('interests'))
