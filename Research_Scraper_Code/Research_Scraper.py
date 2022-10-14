import re

from Research_Scraper_Code.scraper_types.scraper_ieee import ScraperIEEE
from Research_Scraper_Code.scraper_types.scraper_sciencedirect import ScraperScienceDirect
from Research_Scraper_Code.scraper_types.scraper_springer import ScraperSpringer


class ResearchScraper:

    # initialize the class with all the scrapers
    def __init__(self):
        # here one cann add another scraper
        self.all_scraper = [ScraperSpringer(), ScraperScienceDirect(), ScraperIEEE()]

    def scrape_publication_by_url(self, url, params):
        self.__check_params_type(params)

        # todo doi regex
        if self.check_if_doi_link(url):
            print(f'URL (\'{url}\') is a DOI link, please resolve DOI link first otherwise the scraper will not work '
                  f'properly')
            # todo call doi resolver here
            return None  # until doi resolver is implemented

        result = {}

        for scraper in self.all_scraper:
            if scraper.check_scrape_possible(url):
                print(f'[DEBUG - ResearchScraper] - Found scraper for {url} -> {type(scraper).__name__}')
                result = scraper.scrape_by_url(url, params)
                break
            print(f'[DEBUG - ResearchScraper] - No suitable scraper found for "{url}" ->'
                  f' {type(scraper).__name__}')
        return result

    def __check_params_type(self, params):
        # check format of params
        if not isinstance(params, list):
            raise Exception('Input "params" must be a list')
        for param in params:
            if not isinstance(param, str):
                raise Exception('"Params" must consist only of strings')

    # todo move later to utils
    def check_if_doi_link(self, url):
        doi_link_regex = re.compile(r'^(https?:\/\/)?'  # A doi links starts with http:// or https://
                                    r'(www\.)?'  # or start with www.
                                    r'(doi\.org\/)'  # followed by doi.org/
                                    r'([a-zA-Z0-9\-\.\_]+'  # prefix: any character, number, - or . or _ any number of times
                                    r'\/[a-zA-Z0-9\-\.\_]+)'  # suffix: any character, number, - or . or _ any number of times
                                    r'$')

        if doi_link_regex.match(url):
            return True
        else:
            return False


url_ieee = 'https://ieeexplore.ieee.org/document/7887648'
url_springer = 'https://link.springer.com/article/10.1007/s12525-020-00445-0'
url_doi = 'https://doi.org/10.1007/978-0-387-73947-2_8'

test_urls = [url_ieee, url_springer]

researchscraper = ResearchScraper()

if False:
    print(
        f'Testing scraping the doi link {url_doi} > Result: {researchscraper.scrape_publication_by_url(url_doi, ["title", "authors"])}')

if True:
    test_url = url_springer
    result = researchscraper.scrape_publication_by_url(test_url, params=['full'])
    print('Test Start for: ', test_url, '\n______________________________________________________')
    for key, value in result.items():
        print(key, ': \n', '> ', value, '\n')
