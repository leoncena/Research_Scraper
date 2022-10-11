from scraper_abstract import ScraperAbstract
import json


class ScraperSpringer(ScraperAbstract):
    """
    Class for the specific Springer Scraper
    """

    # init domain name
    def _set_domain(self):
        self.domain = 'link.springer.com'

    def scrape_by_url(self, url, params=None):
        """
        Scrape a publication with a url \n
        You will get by default the main data (xxxx todo ergänzen) \n
        You can scrape everything with params=['full']
        You can also choose what you want to scrape with e.g. params=['authors', 'title']

        :param url: URL of a publication
        :param params: What data do you want to scrape? ([str])
        :return: Dictionary with scraped data
        """
        # todo check if links resolved
        # todo check if url is correct

        # create empty dictionary
        scrape_result = {}
        if params is None:
            params = ['main']

        if params == ['main']:
            params = ['title', 'authors']  # todo finalize at the end

        if params == ['full']:
            params = ['title', 'authors', 'xxx']  # todo finalize

        bs = self.get_bs(url)
        json_data = self.get_json_data(bs)

        if 'title for helium' in params:
            bs_full = self.get_bs(url, method='cloud')  # only example, springer does not need cloudscraper

        # get title
        if 'title' in params:
            scrape_result['title'] = self.get_title(bs)

        # get authors
        if 'authors' in params:
            scrape_result['authors'] = self.get_authors(json_data)

        # get keywords
        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(json_data)

        # get abstract
        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(url, json_data)

        # get pdf
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

        return scrape_result

    def get_json_data(self, bs):  # todo save json data for method and let other functions take it as input
        json_string = bs.find('script', {'type': 'application/ld+json'}).text
        json_data = json.loads(json_string)

        if '{"mainEntity":' in json_string:
            return json_data['mainEntity']
        else:
            return json_data

    def get_title(self, bs):
        """
        Returns title of a publication
        :return: Title
        """
        try:
            title = bs.find('h1', {'class': 'c-article-title'}).text
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

        """
        Return list of keywords in the format:
        [keyword1, keyword2, ...]
        :param bs: Received bs of the publication
        :return: list: String
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
                else:
                    return f'https://link.springer.com{pdf}'
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

    def get_publication_type(self, bs, url):
        """
        Returns the publication type of the publication
        :param url: URL of the publication
        :param bs: Received bs of the publication
        :return: String
        """
        try:
            if '/book/' in url:
                type = bs.find('li', {'class': 'c-article-identifiers__item'}).text
            else:
                type = bs.find('li', {'class': 'c-article-identifiers__item', 'data-test': 'article-category'}).text
            return type
        except:
            print("Error: no publication type found in bs, deriving by url")
            if '/book/' in url:
                return 'Book'
            elif '/chapter/' in url:
                return 'Chapter'
            elif '/article/' in url:
                return 'Article'
            # return None

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
            body = bs.find('div', class_='c-article-body')  # Body contains all sections
            sections = bs.findAll('section')
            len(sections)
            text_section = ''
            for section in sections:
                chapter_name = section.find('h2',
                                            class_='c-article-section__title js-section-title js-c-reading-companion-sections-item').text
                p_tags = section.find('div', class_='c-article-section__content').findAll('p')
                chapter_text = self.extract_text_from_p_tags(p_tags)
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
                chapter_text = self.extract_text_from_p_tags(p_tags)
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

    #
    # continue after journal volume later
    #

    # todo:  move to utils later
    def extract_text_from_p_tags(self, p_tags):
        """
        Help method to extract text from multiple p-tags
        :param p_tags: List of p-tags as result of a bs search : bs4.element.ResultSet
        :return: String with total text
        """
        result_text = ''
        for p in p_tags:
            if result_text == '':
                result_text += p.text  # No break for first paragraph
            else:
                result_text += f'\n\n{p.text}'  # Break for paragraph
        return result_text


test = ScraperSpringer()
print(test.domain)
x = test.scrape_by_url('https://link.springer.com/article/10.1007/s12525-020-00445-0', params=['journal_volume'])
print(x)
