"""
This module is for the class of the scraper
"""
import random
import time
import os

from scholarly import scholarly, ProxyGenerator
import pandas as pd

from Research_Scraper_Code import utils
from Research_Scraper_Code.scraper_types.scraper_ieee import ScraperIEEE
from Research_Scraper_Code.scraper_types.scraper_sciencedirect import ScraperScienceDirect
from Research_Scraper_Code.scraper_types.scraper_springer import ScraperSpringer


class ResearchScraper:
    """
    Research scraper that handles multiple specialised scrapers and can be extended easily
    """

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
            print('\n\n unknown error caught', e)
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

    def download_pdf_of_publication_by_doi_live(self, doi, write_folder='../Application/exports/pdf_downloads'):
        """
        Scrapes pdf url and downloads it if possible
        :param write_folder: path of folder where pdf is saved
        :param doi: DOI of publication
        :return: void, writes pdf to disk
        """
        scrape_result = self.scrape_publication_by_doi(doi, ['doi', 'pdf'])
        if scrape_result.get('pdf') is None:
            print(f'No pdf link found for {doi}, thus no pdf downloaded')
            return
        if scrape_result.get('pdf') is not None and scrape_result.get('doi') is not None:
            filename = scrape_result.get('doi').replace('/', '_')
            pdf_url = scrape_result.get('pdf')
            utils.download_pdf(url=pdf_url, filename=filename, write_folder_path=write_folder)

    def download_pdf_of_publications_by_doi_list_live(self, doi_list,
                                                      write_folder='../Application/exports/pdf_downloads'):
        """
        Scrapes pdf url and downloads it if possible
        :param write_folder: path of folder where pdf is saved
        :param doi_list: List of DOI numbers
        :return: void, writes pdf to disk
        """
        for doi in doi_list:
            self.download_pdf_of_publication_by_doi_live(doi, write_folder)

    def download_pdf_of_publications_by_scraping_results(self, scraping_result,
                                                         write_folder='../Application/exports/pdf_downloads'):
        """
        Reads scraping results and downloads every pdf inside if possible
        :param write_folder: path of folder where pdf is saved
        :param scraping_result: List of scrape results
        :return: void, writes pdf to disk
        """
        all_publications_with_pdf = [{'doi': x.get('doi'),
                                      'pdf': x.get('pdf')}
                                     for x in scraping_result if x.get('pdf') is not None and x.get('doi') is not None]
        # iterate over all publications with pdf
        for idx, publication in enumerate(all_publications_with_pdf):
            # wait random time to avoid being blocked from 1 second to 5 seconds
            time.sleep(random.randint(0, 3))

            print(f'>>> Downloading pdf {idx + 1} of {len(all_publications_with_pdf)}')

            if publication.get('pdf') is not None and publication.get('doi') is not None:
                filename = publication.get('doi').replace('/', '_')
                pdf_url = publication.get('pdf')
                utils.download_pdf(url=pdf_url, filename=filename, write_folder_path=write_folder)

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

    def handle_proxy(self, proxy=None):
        """
        Handle the procxy, by default no proxy thus None
        :param proxy: choose whether to use proxy, we can add premium proxied if needed later
        :return: void
        """

        if proxy is None:
            scholarly.use_proxy(None)
        elif proxy == 'free':
            pg = ProxyGenerator()
            success = pg.FreeProxies()
            print(f'Free proxy success: {success}')
            scholarly.use_proxy(pg)
        elif proxy == 'scraper_api':
            pg = ProxyGenerator()
            success = pg.ScraperAPI(os.environ['SCRAPER_API_KEY'])
            scholarly.use_proxy(pg)
        else:
            print('No proxy recognized')

    def search_author_information_from_google_scholar(self, details, sections=['basics', 'indices', 'counts']):
        """
        Searches for author information from google scholar (fill mode)
        :param details: query details
        :param sections: fill params
        :return: author information dict
        """
        result = scholarly.search_author(details)
        # get first result
        found_author = next(result)
        filled_author = scholarly.fill(found_author, sections=sections)
        # remove unwanted values from filled_author
        del filled_author['container_type']
        del filled_author['filled']
        del filled_author['source']
        return filled_author

    def get_url_from_publication_with_scholarly(self, search_query):
        """
        Searches for publication url with scholarly
        (think whether you want to init a proxy prior to using this function)
        :param search_query:
        :return:
        """
        scholarly_search = scholarly.search_pubs(search_query)
        publication = next(scholarly_search)
        url = publication.get('pub_url')

        return url

    # method that takes list of dict {cris_id: cris-id, title:title, authors:authors} an tries to receive a url from scholar
    def get_urls_from_scholar_list_of_publications(self, publications, filename):
        # create a list of publications with {cris_id: cris-id, title:title, authors:authors, url:url}
        publications_with_url = []
        # iterate over publications
        for idx, publication in enumerate(publications):
            print(f'publication {idx + 1} of {len(publications)}: {publication.get("title")}')
            # get title and authors
            title = publication.get('title')
            authors = publication.get('authors')
            # if authors nan then make ''
            if pd.isna(authors):
                authors = ''
            cris_id = publication.get('cris_id')

            # create a query
            query = title
            # if authors are available add them to the query
            if authors is not None:
                query = query + ' ' + authors

            try:
                # search for url with query
                publication['url'] = self.get_url_from_publication_with_scholarly(query)
                print(f' Found url: {publication["url"]}')
            except Exception as e:
                print(f' Error: {e}')
                print(f'Could not find url for cris: {cris_id}, Google scholar blocked us')
            else:
                # add complete publication to publications_with_url
                publications_with_url.append(publication)
                utils.write_results(publications_with_url, filename)

        return publications_with_url
