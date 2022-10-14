import time

from Research_Scraper_Code.Research_Scraper import *

# test urls
url_ieee = 'https://ieeexplore.ieee.org/document/7887648'
url_springer = 'https://link.springer.com/article/10.1007/s12525-020-00445-0'
url_doi = 'https://doi.org/10.1007/978-0-387-73947-2_8'
url_elsevier = 'https://www.sciencedirect.com/science/article/pii/S2451929420300851?via%3Dihub'
url_springer2 = 'https://doi.org/10.1007/s00450-009-0054-z'
test_urls = [url_ieee, url_springer]

scraper = ResearchScraper()


# print(f'Testing scraping the doi link {url_doi} > Result: {scraper.scrape_publication_by_url(url_doi, ["title", "authors"])}')


def test_scrape_url():
    global start, result, key, value, end
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
    global start, result, key, value, end
    test_doi = '10.1007/s11943-021-00292-1'
    start = time.time()
    result = scraper.scrape_publication_by_doi(test_doi, params=['full'])
    if result is not None:
        print('\nTest Start for: ', test_doi, '\n______________________________________________________')
        for key, value in result.items():
            print(key, ': \n', '> ', value, '\n')

        end = time.time()
        print(f'Total time : {end - start}')


test_scrape_doi()
