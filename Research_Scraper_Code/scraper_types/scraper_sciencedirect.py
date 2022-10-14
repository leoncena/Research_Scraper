import re
import time

from bs4 import BeautifulSoup

from Research_Scraper_Code.scraper_types.scraper_abstract import ScraperAbstract
from Research_Scraper_Code import utils


class ScraperScienceDirect(ScraperAbstract):
    """
    Class for the specific ScienceDirect Scraper
    """

    @property
    def domain(self):
        return 'www.sciencedirect.com'

    @property
    def legal_params(self):
        legal_params = [
            'full',
            'main',
            'title',
            'doi',
            'authors',
            'keywords',
            'abstract',
            'start_page',
            'end_page',
            'full_text',
            'references',
            'journal_name',
            'journal_volume',
            'publication_type',
            'publication_date',
            'amount_citations',
            'author_highlights',
            'editor_highlights',
        ]
        return legal_params

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

        # ETL process
        # 1. Extract: Get the data from the website and create soup object
        # 2. Transform: Extract the data from the soup object
        # 3. Load: Write the data into the dict and return the result

        # check if scraper can scrape this url (defined in super method)
        # raise error if not
        super(ScraperScienceDirect, self).scrape_by_url(url, params)

        scrape_result = {}

        # params logic

        # check if params are legal otherwise raise error
        self.check_params_legal(params)

        if params is None:
            params = ['main']

        if params == ['main']:
            params = ['title', 'authors']  # todo finalize at the end: define what counts as main

        if params == ['full']:
            params = self.legal_params  # full = all legal params

        # get soup for subsequent parsing, for ScienceDirect we use cloudscraper to bypass cloudflare
        bs = self.get_bs(url, method='cloud')

        if 'full_text' in params or 'references' in params or 'amount_citations' in params:
            bs_full = self.get_bs(url, method='helium')  # only example, springer does not need cloudscraper
            bs_full_is_created = True

        # get title
        if 'title' in params:
            scrape_result['title'] = self.get_title(bs)

        if 'doi' in params:
            scrape_result['doi'] = self.get_doi(bs)

        # get authors
        if 'authors' in params:
            scrape_result['authors'] = self.get_authors(bs)

        # get keywords
        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(bs)

        # get abstract
        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(bs)

        if 'full_text' in params:
            if bs_full_is_created is False:
                raise Exception('bs_full is not created')
            scrape_result['full_text'] = self.get_full_text(bs_full)  # helium needed for full texts

        if 'start_page' in params:
            scrape_result['start_page'] = self.get_start_page(bs)

        if 'end_page' in params:
            scrape_result['end_page'] = self.get_end_page(bs)

        if 'references' in params:
            if bs_full_is_created is False:
                raise Exception('bs_full is not created')
            scrape_result['references'] = self.get_references(bs_full)  # helium needed for references

        if 'journal_name' in params:
            scrape_result['journal_name'] = self.get_journal_name(bs)
        #
        if 'journal_volume' in params:
            scrape_result['journal_volume'] = self.get_journal_volume(bs)

        if 'publication_date' in params:
            scrape_result['release_date'] = self.get_publication_date(bs)

        if 'amount_citations' in params:
            if bs_full_is_created is False:
                raise Exception('bs_full is not created')
            scrape_result['amount_citations'] = self.get_amount_citations(bs_full)  # helium needed for references

        if 'author_highlights' in params:
            scrape_result['author_highlights'] = self.get_author_highlights(bs)

        if 'editor_highlights' in params:
            scrape_result['editor_highlights'] = self.get_editor_highlights(bs)

        # remove None values from result dict
        scrape_result = {key: value for key, value in scrape_result.items() if value is not None}

        # todo elsevier only papers? -> publication type should give maybe straight paper

        # todo implement
        # if 'year' in params:
        #     scrape_result['year'] = self.get_year(json_data, url)

        return scrape_result

    def get_title(self, bs):
        """
        Get title of a publication
        :param bs: Bs4 object
        :return:
        """
        title = bs.find('span', class_='title-text').text.strip()
        return title

    def get_doi(self, bs, doi_type='doi_number'):
        """
        Gets the doi_number of a publication
        :param bs: Bs4 object
        :return:
        """
        regex_doi = re.compile(r'http(s?)://doi.org/.*')
        doi_link = bs.find('a', class_='doi').text.strip()

        if doi_type == 'doi_number':
            # control and clean doi
            if regex_doi.match(doi_link):
                doi = re.sub(r'http(s?)://doi.org/', '', doi_link)
                return doi
            else:
                return None
        if doi_type == 'doi_link':
            if regex_doi.match(doi_link):
                return doi_link
            else:
                return None
        return None

    def get_authors(self, bs):
        """
        Get authors of a publication
        :param bs:
        :return: Author names as list
        """
        authors = []
        try:
            author_boxes = bs.find('div', {'class': 'author-group', 'id': 'author-group'}).find_all('a')

            for box in author_boxes:
                first_name = box.find('span', class_='text given-name').text.strip()
                last_name = box.find('span', class_='text surname').text.strip()
                authors.append(f'{first_name} {last_name}')
            return authors
        except:
            return None

    def get_keywords(self, bs):
        """
        Get list of keywords
        :param bs: Received bs of the publication
        :return: List of strings
        """
        keywords = []
        try:
            kwds = bs.find('div', class_='keywords-section').find_all('div', class_='keyword')
            for kwd in kwds:
                keyword = kwd.text.strip()
                keywords.append(keyword)
            return keywords
        except:
            return None

    def get_abstract(self, bs):
        """
        Get abstract of a publication
        :param bs: Received bs of the publication
        :return: Abstract : String
        """
        try:
            abstract = bs.find('div', class_='abstract author').div.text.strip()
            return abstract
        except:
            return None

    def get_full_text(self, bs):
        # todo can be easy rewritten to produce markdown files
        """
        Get full text of a publication if online available
        :param bs: Received bs of the publication (HTML must be accessed with Selenium or Helium, does not work otherwise)
        :return: Full text : String with little formatting (new-lines for headings)
        """
        if not self._check_text_available(bs):
            return None

        try:
            text = []
            body = bs.find('div', {'class': 'Body u-font-serif', 'id': 'body'})
            body_sections = body.div.findAll('section', recursive=False)  # sections of body -> h2 level
            for section in body_sections:
                chapter_name = section.h2.text
                chapter_text = self._process_text_recursive(section)
                text.append({
                    'chapter_name': chapter_name,
                    'chapter_text': chapter_text
                })
            return text
        except:
            return None

    def get_journal_name(self, bs):
        """
        Get the journal name where the paper has been published
        :param bs: Received bs of the publication
        :return: String
        """
        # Some Journals have their name as text and logo, other have their name as text only and a dedicated logo
        # We have to differentiate between both cases
        journal_bar = bs.find('div', {'id': 'publication'})
        if journal_bar.attrs['class'] == ['Publication', 'wordmark-layout']:
            journal_name = journal_bar.find('h2', class_=lambda c: 'publication-title-link' in c).text.strip()
        else:
            journal_name = journal_bar.find('a', class_='publication-title-link').text.strip()
        return journal_name

    def get_journal_volume(self, bs):
        """
        Returns the information about the volume of a jourmal in which the publication has been published
        :param bs: bs4 object
        :return: String
        """
        try:
            return self.get_journal_information(bs)['volume']
        except:
            return None

    def get_publication_date(self, bs):
        """
        Returns the information about the release of a jourmal in which the publication has been published
        :param bs: bs4 object
        :return: String
        """
        try:
            return self.get_journal_information(bs)['release']
        except:
            return None

    def get_start_page(self, bs):
        """
        Returns the start page of a publication in a journal
        :param bs: bs4 object
        :return: String
        """
        try:
            return self.get_journal_information(bs)['start_page']
        except:
            return None

    def get_end_page(self, bs):
        """
        Returns the end page of a publication in a journal
        :param bs: bs4 object
        :return: String
        """
        try:
            return self.get_journal_information(bs)['end_page']
        except:
            return None

    def get_author_highlights(self, bs):
        """
        Returns the author highlights of a publication in bullet points
        :param bs: bs4 object
        :return: [String] containing bulletpoints
        """
        try:
            highlight_box = bs.find('div', class_='abstract author-highlights')
            bullet_points = [x.text.strip() for x in highlight_box.find_all('dd', class_='list-description')]
            return bullet_points
        except:
            return None

    def get_editor_highlights(self, bs):
        """
        Returns the editor highlights of a publication in bullet points
        :param bs: bs4 object
        :return: String
        """
        try:
            highlight_box = bs.find('div', class_='abstract editor-highlights')
            title = ''
            try:
                title = highlight_box.h2.text.strip()
            except:
                pass
            try:
                text = highlight_box.find('p').text.strip()
            except:
                return None
            if title == '':
                return text
            return f'{title}: {text}'
        except:
            return None

    def get_references(self, bs):
        """
        Returns a list of references and their links, if available. \n
        Basic extraction of meta data, though not the focus since we can scrape in detail with doi numbers.
        :param bs: bs4 object
        :return:
        """

        if not self._check_references_available(bs):
            return None
        try:
            references_result = []
            ref_list = bs.find('dl', {'class': 'references', 'id': re.compile(r'reference-links-.*')})
            found_references = ref_list.find_all('dd', class_='reference')
            for ref in found_references:

                authors = None
                title = None
                source = None
                article_link = None
                doi_link = None
                google_scholar_link = None

                try:
                    authors = ref.find('div', class_='contribution').contents[0].strip().split(',')
                except:
                    pass
                try:
                    title = ref.find('div', class_='contribution').contents[1].text.strip()
                except:
                    pass
                try:
                    source = ref.find('div', class_='host').text.strip()
                except:
                    pass

                link_box = ref.find('div', class_='ReferenceLinks u-font-sans')

                try:
                    article_link = link_box.find('a', text='Article').get('href')
                    if 'http' not in article_link:
                        article_link = 'https://www.sciencedirect.com' + article_link
                except:
                    pass
                try:
                    doi_link = link_box.find('a', text='CrossRef').get('href')
                except:
                    pass
                try:
                    google_scholar_link = link_box.find('a', text='Google Scholar').get('href')
                except:
                    pass

                references_result.append({
                    'authors': authors,
                    'title': title,
                    'source': source,
                    'article_link': article_link,
                    'doi_link': doi_link,
                    'google_scholar_link': google_scholar_link
                })
            return references_result

        except:
            print("Error in get_references")
            return None

    def get_amount_citations(self, bs):
        """
        Retuns the amount of citations according to ScienceDirect metric
        :param bs: bs4 object
        :return: # Citations
        """
        try:
            amount_citations = bs.find('li', class_='plx-citation').find('span', class_='pps-count').text.strip()
            return amount_citations
        except:
            return None

    def get_journal_information(self, bs):
        """
        Returns the journal information of a publication
        :param bs: bs4 object
        :return: Dictionary with journal information: Volume, Release, Start page, End page
        """
        try:
            journal_info = bs.find('div', {'class': 'Publication', 'id': 'publication'}).find('div',
                                                                                              class_='text-xs')
            # dummy comment to identify type
            comment_markup = "<b><!--I am an comment--></b>"
            _x = BeautifulSoup(comment_markup, "html.parser")
            _comment = _x.b.string

            counter = 0  # count HTML comments
            result = ['Volume', 'Year', 'PageRange']  # create list of results
            # iterate over sub-content of textbox
            for x in journal_info.contents:
                if x.text.strip() == ',':  # skip when comma is found
                    continue
                # increment counter if comment is found
                if isinstance(x, type(_comment)):
                    counter += 1
                    continue
                # add text to result list if no special case  (comment, comma
                result[counter] = x.text.strip()

            # clean page range
            result[2] = result[2].removeprefix(', Pages ')
            volume, release, page_range = result
            # Split by hyphen to get start and end_page
            start_page = page_range.split('-', maxsplit=1)[0]
            end_page = page_range.split('-', maxsplit=1)[1]

            return {
                'volume': volume, 'release': release, 'start_page': start_page, 'end_page': end_page
            }
        except:
            return None

    def _process_text_recursive(self, section):
        """
        his helper methods takes a HTML sections from ScienceDirect and extracts the text from it while regarding (
        sub-)headings.\n
        You can use that function to apply it to the found h1-sections so the function can
        take care of the potential subsections in the passed section. \n
        Headings are recognized by the function and printed as new lines. \n
        The function is recursive and calls itself for sub-sections.
        :params section: HTML section as bs4.element.Tag
        :return: Text as string with new lines for headings
        """
        # extracts the texts of given section including sub headings
        # todo question: Filter out mathemtical formulas?
        children = section.findAll(recursive=False)
        t = ''
        for child in children:
            p_tags = []
            if child.name == 'h3' or child.name == 'h4':
                t += f'{child.text}\n'
            if child.name == 'div':
                p_new = child.findAll('p')
                p_tags.extend(p_new)
            if child.name == 'section':
                t += utils.extract_text_from_p_tags(p_tags)
                p_tags = []
                t += self._process_text_recursive(child)
            if child.name == 'p':
                p_tags.append(child)
            t += utils.extract_text_from_p_tags(p_tags) + '\n'
        return t

    def _check_text_available(self, bs):
        """
        Check if test is available for a Sciendedirect publication
        :param bs: Received bs of the publication (HTML must be accessed with Selenium or Helium, does not work otherwise)
        :return: Boolean
        """
        try:
            body = bs.find('div', {'class': 'Body u-font-serif', 'id': 'body'})
        except:
            pass
        if body is not None:
            return True
        return False

    def _check_references_available(self, bs):
        """
        Check if test is available for a ScienceDirect publication
        :param bs: Received bs of the publication (HTML must be accessed with Selenium or Helium, does not work otherwise)
        :return: Boolean
        """
        try:
            body = bs.find('dl', class_='references')
        except:
            pass
        if body is not None:
            return True
        return False
