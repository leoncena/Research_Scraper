import json
import re

import requests

from Research_Scraper_Code.scraper_types.scraper_abstract import ScraperAbstract


class ScraperIEEE(ScraperAbstract):
    """
    Class for the specific IEEE Scraper
    """

    @property
    def domain(self):
        return 'ieeexplore.ieee.org'

    @property
    def legal_params(self):
        legal_params = {
            'full',
            'main',
            'title',
            'doi',
            'authors',
            'keywords',
            'abstract',
            'publisher',
            'year',
            'start_page',
            'end_page',
            'publication_type',
            'full_text',  # does not work yet
            'references',
            'journal_name',
            'journal_volume',
            'journal_issue',
            'conference_name',
            'conference_location',
            'publication_id',  # IEE ID
            'amount_citations',
        }
        return legal_params

    def scrape_by_url(self, url, params=None):
        """
        Scrape a publication with a url \n
        You will get by default the main data (xxxx todo add) \n
        You can scrape everything with params=['full']
        You can also choose what you want to scrape with e.g. params=['authors', 'title']

        :param url: URL of a publication
        :param params: What data do you want to scrape? ([str])
        :return: Dictionary with scraped data
        """

        # ETL process
        # 1. Extract: Get the data from the website and create soup object
        # 2. Transform: Extract the data from the soup object
        # 3. Load: Write the data into the dict and return the result

        # check if scraper can scrape this url (defined in super method)
        # raise error if not
        super(ScraperIEEE, self).scrape_by_url(url, params)

        scrape_result = {'url': url}

        # params logic

        # check if params are legal otherwise raise error
        self.check_params_legal(params)

        if params is None:
            params = ['main']

        if params == ['main']:
            params = ['title', 'authors']  # todo finalize at the end: define what counts as main

        if params == ['full']:
            params = self.legal_params  # full = all legal params

        # get soup to extract the json data
        # bs = self.get_bs(url)

        # extract the json data
        json_data = self.get_json_data(url)

        # get title
        if 'title' in params:
            scrape_result['title'] = self.get_title(json_data)

        # get doi
        if 'doi' in params:
            scrape_result['doi'] = self.get_doi(json_data)

        # get authors
        if 'authors' in params:
            scrape_result['authors'] = self.get_authors(json_data)

        # get keywords
        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(json_data)

        # get abstract
        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(json_data)

        # if 'full_text' in params:
        #     scrape_result['full_text'] = self.get_full_text()  # helium needed for full texts

        if 'publisher' in params:
            scrape_result['publisher'] = self.get_publisher(json_data)

        if 'year' in params:
            scrape_result['year'] = self.get_year(json_data)

        if 'start_page' in params:
            scrape_result['start_page'] = self.get_start_page(json_data)

        if 'end_page' in params:
            scrape_result['end_page'] = self.get_end_page(json_data)

        if 'references' in params:
            scrape_result['references'] = self.get_references(json_data)

        if 'journal_name' in params:
            scrape_result['journal_name'] = self.get_journal_conference_name(json_data)

        if 'conference_name' in params:
            scrape_result['conference_name'] = self.get_journal_conference_name(json_data)
        #
        if 'journal_volume' in params:
            scrape_result['journal_volume'] = self.get_journal_volume(json_data)
        #
        if 'journal_issue' in params:
            scrape_result['journal_issue'] = self.get_journal_issue(json_data)

        if 'conference_location' in params:
            scrape_result['conference_location'] = self.get_conference_location(json_data)

        if 'amount_citations' in params:
            scrape_result['amount_citations'] = self.get_amount_citations(json_data)  # helium needed for references

        # remove None values from result dict
        scrape_result = {key: value for key, value in scrape_result.items() if value is not None}

        # todo elsevier only papers? -> publication type should give maybe straight paper

        # todo implement
        # if 'year' in params:
        #     scrape_result['year'] = self.get_year(json_data, url)

        return scrape_result

    # Extract the meta data from the json object
    def get_json_data(self, url):
        """
        Extracts the json object with meta data from the page and parses it to a dict.
        :param url: URL of th publication
        :return: Dict with content of the JSON object
        """
        # extract the line of the text containing the json object
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}
        try:
            r = requests.get(url, headers=headers)
            print(r.status_code)
            if r.status_code != 200:
                raise Exception('Connection not successful - Status code not 200')
        except Exception as e:
            print('Error: ', e)
            print('Error: ', url)
            return None
        html_text = r.text
        json_data_regex_pattern = re.compile(r'xplGlobal.document.metadata=.*};')
        json_regex_matches = re.findall(json_data_regex_pattern, html_text)

        assert len(json_regex_matches) == 1

        json_string = json_regex_matches[0]
        json_string = json_string.removeprefix('xplGlobal.document.metadata=')  # remove JS prefix

        json_string = json_string.removesuffix(';')  # remove semicolon at the end
        json_parsed = json.loads(json_string)
        assert isinstance(json_parsed, dict)
        return json_parsed

    # Parsing the data

    def get_doi(self, json_data):
        """
        Extract the DOI from the JSON data
        :param json_data: JSON object with meta data
        :return: DOI number
        """
        doi = json_data.get('doi')
        return doi

    def get_authors(self, json_data):
        """
        Extracts the authors from the json object.
        :param json_data: JSON object with meta data
        :return: List of dicts with author name and their ieee id
        """
        authors_raw = json_data.get('authors')
        authors = []
        for el in authors_raw:
            author_name = el.get('name')
            author_id = el.get('id')
            authors.append({
                'name': author_name,
                'id_ieee': author_id
            })
        return authors

    def get_title(self, json_data):
        """
        Extracts the title of the publication.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('title')

    def get_keywords(self, json_data):
        """
        Extracts the keywords from the json object. \n
        There are multiple types of keywords merged. Can de split when demanded.
        :param json_data: JSON object with meta data
        :return: List of strings
        """
        keywords_raw = json_data.get('keywords')
        keywords = []
        for el in keywords_raw:
            keywords.extend(el.get('kwd'))
        return keywords

    def get_abstract(self, json_data):
        """
        Extracts the abstract from the publication.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('abstract')

    def get_publisher(self, json_data):
        """
        Extracts the publisher from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('publisher')

    def get_year(self, json_data):
        """
        Extracts the publication year from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('publicationYear')

    def get_start_page(self, json_data):
        """
        Extracts the start page from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('startPage')

    def get_end_page(self, json_data):
        """
        Extracts the end page from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('endPage')

    def get_publication_type(self, json_data):
        """
        Extracts the publication type from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('xploreDocumentType')

    def fetch_reference_data_json(self, json_data):
        """
        Fetches the reference data from IEEE (Rest API) and returns the the dict of the json response.
        :param json_data: JSON meta data object
        :return: Dict
        """
        publication_id = self.get_publication_id(json_data)
        url = f'https://ieeexplore.ieee.org/rest/document/{publication_id}/references'
        payload = ''
        headers = {
            'Referer': f'https://ieeexplore.ieee.org/document/{publication_id}'
        }
        response = requests.request("GET", url, data=payload, headers=headers)
        reference_data = json.loads(response.text).get('references')
        return reference_data

    def get_references(self, json_data):
        """
        Extracts the references of a publication
        :param json_data: JSON meta data object
        :return: Dict
        """
        try:
            ref_raw = self.fetch_reference_data_json(json_data)
        except:
            return None
        references = []
        for ref in ref_raw:
            reference_text = None
            doi_link = None
            google_scholar_link = None
            reference_text = ref.get('text')
            if ref.get('links') is not None:
                doi_link = ref.get('links').get('crossRefLink')
                google_scholar_link = ref.get('links').get('googleScholarLink')
            references.append({
                'text': reference_text,
                'doi_link': doi_link,
                'google_scholar_link': google_scholar_link
            })
        return references

    def get_journal_conference_name(self, json_data):
        """
        Extracts the journal/conference publication name from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('publicationTitle')

    def get_journal_volume(self, json_data):
        """
        Extracts the journal volume from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('volume')

    def get_journal_issue(self, json_data):
        """
        Extracts the journal issue from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('issue')

    def get_conference_location(self, json_data):
        """
        Extracts the conference location from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('confLoc')

    def get_publication_id(self, json_data):
        """
        Extracts the publication id from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('articleNumber')

    def get_amount_citations(self, json_data):
        """
        Extracts the amount of citations from the publication json data.
        :param json_data: JSON object with meta data
        :return: String
        """
        metrics = json_data.get('metrics')
        if metrics is not None:
            return metrics.get('citationCountPaper')
        return None
