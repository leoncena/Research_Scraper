from Research_Scraper_Code import utils
from Research_Scraper_Code.scraper_types.scraper_ieee import ScraperIEEE
from Research_Scraper_Code.scraper_types.scraper_sciencedirect import ScraperScienceDirect
from Research_Scraper_Code.scraper_types.scraper_springer import ScraperSpringer


class ResearchScraper:

    # initialize the class with all the scrapers
    def __init__(self):
        # here one cann add another scraper  (of course after importing the script above)
        self.all_scraper = [ScraperSpringer(), ScraperScienceDirect(), ScraperIEEE()]

    def scrape_publication_by_url(self, url, params):

        try:
            self.__check_params_type(params)  # check format of params

            # check if url is valid or a doi
            if utils.check_if_doi_link(url):
                print(f'URL (\'{url}\') is a DOI link, Links is now resolved properly')
                url = utils.resolve_url(url)

                # check if doi could be resolved
                if 'doi.org' in url:
                    print(f'URL (\'{url}\') could not be resolved to a valid link')
                    return None

                print(f'Resolved DOI link to: {url}')

            result = {}

            scraper_found = False

            # search suitable scraper
            for scraper in self.all_scraper:
                if scraper.check_scrape_possible(url):
                    print(f'[DEBUG - ResearchScraper] - Found scraper for {url} -> {type(scraper).__name__}')
                    scraper_found = True
                    result = scraper.scrape_by_url(url, params)
                    break

            # if no scraper was found return None
            if not scraper_found:
                print(f'[DEBUG - ResearchScraper] - No scraper found for {url}')
                return None

            return result
        except Exception as e:
            print('\n\n\n\n\n unknown error catched', e)
            return {'error': str(e), 'error_url': url}

    def scrape_publication_by_doi(self, doi, params):
        # check if it is a doi
        if not utils.check_if_doi_number(doi):
            return None
        url = utils.create_doi_link(doi)
        return self.scrape_publication_by_url(url, params)

    def __check_params_type(self, params):
        # check format of params
        if not isinstance(params, list):
            raise Exception('Input "params" must be a list')
        for param in params:
            if not isinstance(param, str):
                raise Exception('"Params" must consist only of strings')
