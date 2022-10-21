from Research_Scraper_Code import utils
from Research_Scraper_Code.scraper_types.scraper_ieee import ScraperIEEE
from Research_Scraper_Code.scraper_types.scraper_sciencedirect import ScraperScienceDirect
from Research_Scraper_Code.scraper_types.scraper_springer import ScraperSpringer
import time


class ResearchScraper:

    # initialize the class with all the scrapers
    def __init__(self):
        # here one cann add another scraper  (of course after importing the script above)
        self.all_scraper = [ScraperSpringer(), ScraperScienceDirect(), ScraperIEEE()]

    def scrape_publication_by_url(self, url, params):
        """
        Scrapes a publication by a given url
        :param url: URL of the publication
        :param params: Parameter for scraping
        :return: Dict with results
        """

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
                    msg = f'[DEBUG - ResearchScraper] - Found scraper for {url} -> {type(scraper).__name__}'
                    # print green background
                    print('\x1b[6;30;42m' + msg + '\x1b[0m')
                    scraper_found = True
                    result = scraper.scrape_by_url(url, params)
                    break

            # if no scraper was found return None
            if not scraper_found:
                msg = f'[DEBUG - ResearchScraper] - No scraper found for {url}'
                # print orange background black font
                print('\x1b[6;30;43m' + msg + '\x1b[0m')
                # return only url for logging purposes
                return {'error': 'No scraper found for this url', 'url': url}

            # dict keys whose values are not none
            not_none_keys = [key for key, value in result.items() if value is not None]

            msg = f' Scraped keys: {not_none_keys}'
            # print green font
            print('\x1b[6;30;32m' + msg + '\x1b[0m')
            return result
        except Exception as e:
            print('\n\n unknown error catched', e)
            return {'error': str(e), 'error_url': url}

    def scrape_publication_by_doi(self, doi, params):
        """
        Scrapes a publication by a given doi
        :param doi: DOI of a publication
        :param params: Parameter for scraping
        :return: Dict with results
        """
        # check if it is a doi
        if not utils.check_if_doi_number(doi):
            return {'error': 'no valid doi passed', 'error_doi': doi}
        url = utils.create_doi_link(doi)
        if url is None:
            return {'error': 'url could not be resolved for DOI', 'error_doi': doi}
        return self.scrape_publication_by_url(url, params)

    def scrape_publication_by_doi_list(self, doi_list, params=['full']):
        """
        Scrapes a list of publication by its DOI numbers
        :param doi_list: List of DOI numbers
        :param params: Parameter for scraping
        :return: List of dicts with results
        """

        start = time.time()
        print(f'Time of scrape start: {time.strftime("%Y_%m_%d__%H_%M")}')
        results = []
        for idx, doi in enumerate(doi_list):
            scraping_log = f'>>> Scraping {doi} #{idx}'
            # print blue background with black font
            print('\x1b[6;30;44m' + scraping_log + '\x1b[0m')
            result = self.scrape_publication_by_doi(doi, params)
            print(f'>>>> Scraping {doi} done')
            results.append(result)
            print(f'>>>> Scraping {doi} added to results')
        print(f'>>>> Scraping {len(doi_list)} publications done')
        utils.write_results(results, f'scrapings_{time.strftime("%Y_%m_%d__%H_%M")}')
        print(f'Time of scrape end: {time.strftime("%Y_%m_%d__%H_%M")}')
        end = time.time()
        print(f'Total time took: {round((end - start) / 60, 2)} minutes')
        return results

    def __check_params_type(self, params):
        """
        Checks the type of params and raises errors if necessary \n
        Params must be a list of strings
        :param params: Parameter for scraping
        :return: void, raises errors if necessary
        """
        # check format of params
        if not isinstance(params, list):
            raise Exception('Input "params" must be a list')
        for param in params:
            if not isinstance(param, str):
                raise Exception('"Params" must consist only of strings')
