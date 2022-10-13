from Research_Scraper_Code.scraper_types.scraper_springer import ScraperSpringer
from Research_Scraper_Code.scraper_types.scraper_sciencedirect import ScraperScienceDirect
from Research_Scraper_Code.scraper_types.scraper_ieee import ScraperIEEE
import re


class ResearchScraper:

    # initialize the class with all the scrapers
    def __init__(self):
        # here one cann add another scraper
        self.all_scraper = [ScraperSpringer(), ScraperScienceDirect(), ScraperIEEE()]

    def scrape_publication_by_url(self, url, params):
        self.__check_params_type(params)

        # todo doi regex
        # check if url is a doi.link with regex (re.search or simple x in y)
        # regex for doi link : doi.org/
        # if doi resolve

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


url_ieee = 'https://ieeexplore.ieee.org/document/7887648'
url_springer = 'https://link.springer.com/chapter/10.1007/978-3-030-06234-7_27'
test_urls = [url_ieee, url_springer]

researchscraper = ResearchScraper()
print(researchscraper.scrape_publication_by_url(url_springer, params=['full']))
