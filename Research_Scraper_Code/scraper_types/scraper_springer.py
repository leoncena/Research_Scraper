import json

from Research_Scraper_Code import utils
from Research_Scraper_Code.scraper_types.scraper_abstract import ScraperAbstract


class ScraperSpringer(ScraperAbstract):
    """
    Class for the specific Springer Scraper
    """

    @property
    def domain(self):
        return 'link.springer.com'

    @property
    def legal_params(self):
        legal_params = [
            'full',
            'main',
            'title',
            'authors',
            'keywords',
            'abstract',
            'pdf',
            'publisher',
            'year',
            'start_page',
            'end_page',
            'publication_type',
            'full_text',
            'references',
            'journal_name',
            'journal_volume',
            'conference_name',
            'conference_proceedings',
            'book_title',
            'editors',
            'book_subtitle',
            'article_accesses',
            'amount_citations']
        return legal_params

    def scrape_by_url(self, url, params=None):
        """
        Scrape a publication with a url \n
        You will get by default the main data (xxxx # todo ergänzen) \n
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
        super(ScraperSpringer, self).scrape_by_url(url, params)

        # if not self.check_scrape_possible(url):
        #     raise Exception("Yeee This scraper cannot scrape this url")

        scrape_result = {}

        # params logic

        # check if params are legal
        self.check_params_legal(params)

        if params is None:
            params = ['main']

        if params == ['main']:
            params = ['title', 'authors']  # todo finalize at the end: define what counts as main

        if params == ['full']:
            params = self.legal_params  # full means all legal params

        # get soup for subsequent parsing
        bs = self.get_bs(url)
        json_data = self.get_json_data(bs)

        if 'title' in params:
            scrape_result['title'] = self.get_title(bs)

        if 'authors' in params:
            scrape_result['authors'] = self.get_authors(json_data)

        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(json_data)

        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(url, json_data)

        if 'pdf' in params:
            scrape_result['pdf'] = self.get_pdf(bs, url)

        if 'publisher' in params:
            scrape_result['publisher'] = self.get_publisher(json_data)

        if 'year' in params:
            scrape_result['year'] = self.get_year(json_data, url)

        if 'start_page' in params:
            scrape_result['start_page'] = self.get_start_page(json_data, url)

        if 'end_page' in params:
            scrape_result['end_page'] = self.get_end_page(json_data, url)

        if 'publication_type' in params:
            scrape_result['publication_type'] = self.get_publication_type(bs, url)

        if 'full_text' in params:
            scrape_result['full_text'] = self.get_full_text(bs, url)

        if 'references' in params:
            scrape_result['references'] = self.get_references(bs, url)

        if 'journal_name' in params:
            scrape_result['journal_name'] = self.get_journal_name(json_data, url)

        if 'journal_volume' in params:
            scrape_result['journal_volume'] = self.get_journal_volume(json_data, url)

        if 'conference_name' in params:
            scrape_result['conference_name'] = self.get_conference_name(bs, url)

        if 'conference_proceedings' in params:
            scrape_result['conference_proceedings'] = self.get_proceedings(bs, json_data, url)

        if 'book_title' in params:
            scrape_result['book_title'] = self.get_book_title(bs, json_data, url)

        if 'editors' in params:
            scrape_result['editors'] = self.get_editors(bs, json_data, url)

        if 'book_subtitle' in params:
            scrape_result['book_subtitle'] = self.get_book_subtitle(json_data, url)

        if 'article_accesses' in params:
            scrape_result['article_accesses'] = self.get_accesses(bs)

        if 'amount_citations' in params:
            scrape_result['amount_citations'] = self.get_amount_citations(bs)

        # remove None values from result dict
        scrape_result = {key: value for key, value in scrape_result.items() if value is not None}

        return scrape_result

    def get_json_data(self, bs):
        json_string = bs.find('script', {'type': 'application/ld+json'}).text
        json_data = json.loads(json_string)

        if '{"mainEntity":' in json_string:
            return json_data['mainEntity']
        return json_data

    def get_title(self, bs):
        """
        Returns title of a publication
        :return: Title
        """
        try:
            title = bs.find('h1', {'class': 'c-article-title'}).text.strip()
            return title
        except:
            return None

    def get_authors(self, json_data):
        """
        Return list of authors in the format:
        [{'name': 'Author Name', 'orcid': orcid}, ...]

        :param json_data: Json data of the publication
        :return: list of dicts
        """
        try:
            authors = []
            for author in json_data.get('author'):
                name = author.get('name')
                # split name at comma and reverse
                name = name.split(', ')
                name = name[1] + ' ' + name[0]
                orcid = author.get('url')
                authors.append({'name': name,
                                'orcid': orcid})
            return authors
        except:  # if no author is found you cannot iterate over None
            return None

    def get_keywords(self, json_data):
        """
        Return list of keywords from json data
        :param json_data: Received json data
        :return:
        """

        try:
            keywords_string = json_data.get('keywords')
            keywords = keywords_string.split(',')
            return keywords
        except:
            print("Error: no keywords found")
            return None

    def get_abstract(self, url, json_data):
        """
        Returns the abstract of the articles, books/proceedings do not have abstracts.
        :param json_data: Received json data
        :param url: Received url of the publication
        :return: String
        """
        if '/book/' in url:
            return None

        try:
            abstract = json_data.get('description')
            return abstract
        except:
            print("Error: no abstract found")
            return None

    def get_pdf(self, bs, url):
        """
        Returns the pdf link of the publication, if available. Download might require login. Sometimes the pdf is not in the soup object unfortunately
        :param bs: Received bs of the publication
        :param url:
        :return:
        """
        try:
            pdf = None
            # todo automate download
            # differentiate between article, chapter and book
            if '/article/' in url:
                pdf = bs.find('div', class_='c-pdf-container').find('a', {'data-article-pdf': 'true'}).get('href')

            elif '/chapter/' in url:
                pdf_box = bs.find('div', {'class': 'c-article-access-provider'})
                pdf = pdf_box.find('a', {'data-track-action': 'Pdf download'}).get('href')

            elif '/book/' in url:
                pdf = bs.find('div', {'data-test': 'download-article-link-wrapper',
                                      'class': 'js-context-bar-sticky-point-desktop'}).find('a').get('href')
            if pdf is not None:
                # append base url if necessary
                if 'link.springer.com' in pdf:
                    return pdf
                return f'https://link.springer.com{pdf}'

            return None
        except Exception:
            print("Error: no pdf found")
            return None

    def get_publisher(self, json_data):
        """
        Returns the publisher of the publication
        :param json_data: Received json data
        :return: String
        """
        try:
            publisher = json_data.get('publisher').get('name')
            return publisher
        except:
            print("Error: no publisher found")
            return None

    def get_year(self, json_data, url):
        """
        Returns the year of the publication
        :param url: URL of the publication
        :param json_data: Received json data
        :return:
        """
        try:
            if ('/chapter/' in url) or ('/article/' in url):
                date = json_data.get('datePublished')
                year = date.split('-')[0]  # get year from date (if date is available)
                return year
            if '/book/' in url:
                year = json_data.get('copyrightYear')
                return year

            return None

        except:
            print("Error: no year found")
            return None

    def get_start_page(self, json_data, url):
        """
        Returns the start page of the publication in the volume/journal/proceeding
        :param json_data: Received json data
        :param url: URL of the publication
        :return: Start page of the publication
        """
        if '/book/' in url:
            return None
        if '/chapter/' in url or '/article/' in url:
            try:
                start_page = json_data.get('pageStart')
                return start_page
            except:
                print("Error: no start page found")
                return None
        return None

    def get_end_page(self, json_data, url):
        """
        Returns the end page of the publication in the volume/journal/proceeding
        :param json_data: Received json data
        :param url: URL of the publication
        :return: End page of the publication
        """
        if '/book/' in url:
            return None
        if '/chapter/' in url or '/article/' in url:
            try:
                end_page = json_data.get('pageEnd')
                return end_page
            except:
                print("Error: no end page found")
                return None
        return None

    def get_publication_type(self, bs, url):
        """
        Returns the publication type of the publication
        :param url: URL of the publication
        :param bs: Received bs of the publication
        :return: String
        """
        try:
            if '/book/' in url:
                publication_type = bs.find('li', {'class': 'c-article-identifiers__item'}).text
            else:
                publication_type = bs.find('li', {'class': 'c-article-identifiers__item',
                                                  'data-test': 'article-category'}).text
            return publication_type
        except:
            print("Error: no publication type found in bs, deriving by url")
            print(url)
            if '/book/' in url:
                return 'Book'
            if '/chapter/' in url:
                return 'Chapter'
            if '/article/' in url:
                return 'Article'
            return None

    def get_full_text(self, bs, url):
        """
        Returns the accessible text of the publication structured in different paragraphs. This may be the total text or only a part of.
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Returns a list of ordered dictionaries. Each dictionary contains the name respectively text of the paragraph.
        """

        def __get_full_text_chapter(bs, text):
            """
            Internal method to extract text from chapter links
            :param bs:
            :param text:
            :return:
            """
            sections = bs.findAll('section')
            len(sections)
            for section in sections:
                chapter_name = section.find('h2',
                                            class_='c-article-section__title js-section-title js-c-reading-companion-sections-item').text
                p_tags = section.find('div', class_='c-article-section__content').findAll('p')
                chapter_text = utils.extract_text_from_p_tags(p_tags)
                text.append({
                    'chapter_name': chapter_name,
                    'chapter_text': chapter_text
                })
                next_sibling_id = section.find_next_sibling().attrs.get('id')

                # breaks loop when text sections are completed
                if next_sibling_id == 'MagazineFulltextChapterBodySuffix':
                    break
            return text

        def __get_full_text_article(bs, text):
            """
            Internal function to extract text from an article
            :param bs:
            :param text:
            :return:
            """
            main_div = bs.find('div', class_='main-content')
            sections = main_div.findAll('section')
            for section in sections:
                chapter_name = section.h2.text
                p_tags = section.findAll('p')
                chapter_text = utils.extract_text_from_p_tags(p_tags)
                text.append({
                    'chapter_name': chapter_name,
                    'chapter_text': chapter_text
                })
            return text

        text = []

        if '/article/' in url:  # article extractions works
            try:
                return __get_full_text_article(bs, text)
            except:
                print("Error try clause")

        if '/chapter/' in url:
            try:
                return __get_full_text_chapter(bs, text)
            except:
                print("Error: try clause in chapter")

        if '/book/' in url:
            return None

    def get_references(self, bs, url):
        """
        Returns the information of the references of the publication
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Returns a list of dictionaries with the reference text and the Google Scholar link (if existing) in th form of
        {'text': 'reference text', 'link': 'link to Google Scholar'}
        """
        if '/book/' in url:
            return None

        references = []
        try:
            reference_items = bs.find_all('li', class_='c-article-references__item')
        except:
            return None  # No references found
        for item in reference_items:
            reference_text = item.find('p', class_='c-article-references__text').text
            try:
                gscholar_link = item.find('a', {'data-track-action': 'google scholar reference'}).get('href')
            except:
                gscholar_link = None
            references.append({
                'reference_text': reference_text,
                'google_scholar_link': gscholar_link
            })
        return references

    def get_journal_name(self, json_data, url):
        """
        Returns the journal name of the publication
        Returns None if publication is not a journal article
        :param json_data: Received json data
        :param url: URL of the publication
        :return: Journal name (String)
        """

        if '/article/' in url:
            journal_name = json_data.get('isPartOf').get('name')
            return journal_name
        else:
            return None

    def get_journal_volume(self, json_data, url):
        """
        Returns the journal volume of the publication
        Returns None if publication is not a journal article
        :param json_data: Received json data
        :param url: URL of the publication
        :return: Journal volume (String)
        """
        if '/article/' in url:
            journal_volume = json_data.get('isPartOf').get('volumeNumber')
            return journal_volume
        else:
            return None

    def get_conference_name(self, bs, url):
        """
        Returns the conference name of the publication
        :param bs: bs object of the publication
        :param url: URL of the publication
        :return: Conference name
        """
        if self.get_publication_type(bs, url) == 'Conference paper':
            conference_name = bs.find('p', class_='c-chapter-info-details u-mb-8').find('a', {
                'data-track': 'click', 'data-track-action': 'open conference'
            }).text
            return conference_name
        else:
            return None

    def get_proceedings(self, bs, json_data, url):
        """
        Returns the title of the conference proceedings or book under which the publication was published.
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Title of the proceedings/book (String)
        """
        if self.get_publication_type(bs, url) == 'Conference paper':
            try:
                proceedings = json_data.get('isPartOf').get('name')
                return proceedings
            except:
                return None
        else:
            return None

    def get_book_title(self, bs, json_data, url):
        """
        Returns the title of the book under which the publication was published.
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Title of the book (String)
        """
        if self.get_publication_type(bs, url) == 'Chapter':
            try:
                book_title = json_data.get('isPartOf').get('name')
                return book_title
            except:
                return None
        else:
            return None

    def get_editors(self, bs, json_data, url):
        """
        Returns the editors of the volume (under which the publication was published)
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: List of Editors : [String]
        """
        if '/chapter/' in url:
            try:
                editor_div = bs.find('div', {'class': 'c-article-section__content', 'id': 'editor-information-content'})
                editors = []
                for editor in editor_div.find_all('p', class_='c-article-author-affiliation__authors-list'):
                    editors.append(editor.text)
                # remove titles since we scrape the names
                # remove Everything including the point from strings in list
                editors = [editor.split('.')[1].strip() for editor in editors]
                return editors
            except:
                return None
        # in books the editors are in the json file
        if '/book/' in url:
            try:
                editors = [editor.get('name') for editor in json_data.get('editor')]
                return editors
            except:
                return None
        else:
            return None

    def get_book_subtitle(self, json_data, url):
        """
        Returns the subtitle of the book (proceedings or editor volume).
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Subtitle of the book (String)
        """
        if '/book/' in url:
            try:
                book_subtitle = json_data.get('alternateName')
                return book_subtitle
            except:
                return None
        return None

    # Springer Metrics

    def get_accesses(self, bs):
        """
        Returns the number of accesses of the publication according to the Springer metric.
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Number of accesses (String) #TODO change to int (check if wanted, old todo note)
        """
        # Navigating with parent because accesses and citations do not have individual features.
        try:
            accesses = bs.find('span', text='Accesses').parent.text.strip().split(' ')[0]  # navigating up in the tree
            return accesses
        except:
            print("error, accesses not found")
            return None

    def get_amount_citations(self, bs):
        """
        Returns the number of citations of the publication according to the Springer metric.
        :param bs: Received bs of the publication
        :param url: URL of the publication
        :return: Number of citations (String) #TODO change to int
        """
        # Navigating with parent because accesses and citations do not have individual features.
        try:
            citations = bs.find('span', text='Citations').parent.text.strip().split(' ')[0]  # navigating up in the tree
            return citations
        except:
            try:
                # Citation
                citations = bs.find('a', class_='c-article-metrics-bar__label',
                                    text='Citations').parent.text.split(' ')[0].strip()
                return citations
            except:
                return None
