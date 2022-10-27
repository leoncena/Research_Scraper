import json
import re
import urllib.parse

import pandas as pd
import requests
import cloudscraper


def check_if_doi_link(url):
    """
    Returns true if a passed url is a DOI link \n
    Source: https://www.medra.org/en/DOI.htm
    :param url: url to check
    :return: Bool
    """

    doi_link_regex = re.compile(r'^(https?:\/\/)?'  # A doi links starts with http:// or https://
                                r'(www\.)?'  # or start with www.
                                r'(doi\.org\/)'  # followed by doi.org/
                                r'10\.'  # DOI suffix starts with '10.'
                                r'\d{4,9}'  # followed by 4-9 digits
                                r'\/[-._;()/:a-zA-Z0-9]+'  # suffix: any character, number, - or . or _ any number of times
                                r'$')

    if doi_link_regex.match(url):
        return True
    else:
        return False


def check_if_doi_number(doi_number):
    """
    Returns true if a passed string is a DOI number\n
    Sources: https://www.medra.org/en/DOI.htm, https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    :param doi_number: String
    :return: Bool
    """
    doi_number_regex = re.compile(r'^'  # matching the start
                                  r'10\.'  # DOI suffix starts with '10.'
                                  r'\d{4,9}'  # followed by 4-9 digits
                                  r'\/[-._;()/:a-zA-Z0-9]+'  # followed by suffix: a slash and any number/ character
                                  r'$')

    if doi_number_regex.match(doi_number):
        return True
    else:
        return False


def create_doi_link(doi: str):
    # check first if doi is really doi number
    if check_if_doi_number(doi):
        return 'https://doi.org/' + doi
    else:
        return None


def extract_text_from_p_tags(p_tags):
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


def resolve_url(url):
    """
    Resolve a url to its final destination
    :param url: url
    :return: resolved url
    """
    try:
        r = requests.head(url, allow_redirects=True, timeout=120)
        return r.url
    except requests.exceptions.ConnectionError as e:
        print(f'[utils.py: get_link] Connection Error: {e}')
        return None


def domain(url):
    """
    Returns the domain-part of an url
    :param url:
    :return:
    """
    if url is not None and pd.notna(url):
        return urllib.parse.urlparse(url).netloc  # returns domain
    else:
        return None


def write_results(results, name):
    """
    Writes the results to a json file
    :param name: filename to write
    :param results: Results of scraping,, list of dict
    :return: void, writes to file
    """
    if results is not None:
        with open(f'exports/scrapings/{name}.json', 'w') as f:
            json.dump(results, f, indent=4)
            # print green background black font
            print(f'\033[1;30;42m{len(results)} results written to {name}.json\033[0m')


def download_pdf(url, filename, write_folder_path, method='requests', timeout=30):
    """
    Downloads a pdf from a url and saves it to a folder
    :param timeout: default timeout for requests getting pdfs
    :param url: url of a pdf
    :param filename: name of the file to write
    :param write_folder_path: folder to write to
    :param method: method of getting the pdf, either requests or cloudscraper, default requests
    :return:void, writes to file
    """
    if method == 'requests':
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
        except (
                requests.exceptions.MissingSchema, requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
            # cancel download
            print(f'[utils.py: download_pdf] Connection Error - could not download: error type: {type(e)} -> {e}')
            return
    if method == 'cloudscraper':
        scraper = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )
        try:
            r = scraper.get(url, allow_redirects=True, timeout=timeout)
        except (
                requests.exceptions.MissingSchema, requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema) as e:
            # cancel download
            print(f'[utils.py: download_pdf] Connection Error - could not download: error type: {type(e)} -> {e}')
            return

    pdf_save_path = write_folder_path + '/' + filename + '.pdf'
    if r.status_code == 200:
        with open(pdf_save_path, 'wb') as f:
            f.write(r.content)
            log_1 = 'PDF downloaded'
            log_2 = f' : {filename}.pdf'
            log_3 = f' to {write_folder_path}'

            # print log_1 in green background black font
            print(f'\033[1;30;42m{log_1}\033[0m' + log_2 + log_3)

            # if pdf file smaller than 5 kb, print a warning that it might be corrupted
            if len(r.content) < 5000:
                msg = f'but PDF might be corrupted, file size: {len(r.content)} bytes'
                print(f'\033[1;30;43m{msg}\033[0m')  # orange

    else:
        print(f'[utils.py: download_PDF] PDF Download failed: {r.status_code}')


def load_and_clean_scraping_results(filename, custom_path=None):
    """
    Reads a the json file with scraping results and cleans it by removing None and error rows
    :param custom_path: Specify the custom folder path if you don't want to write it to the default folder
    :param filename: name of file to write
    :return: cleaned results, list of dict
    """
    if custom_path is None:
        path = f'../Application/exports/scrapings/{filename}.json'
    else:
        path = f'{custom_path}/{filename}.json'

    with open(path, 'r') as f:
        scraping_results_imported = json.load(f)

    scraping_results_imported_cleaned = [x for x in scraping_results_imported if
                                         x is not None and x.get('error') is None]

    return scraping_results_imported_cleaned


def load_publications_from_csv():
    """
    Loads the publications from the csv file
    :return: dataframe with publications
    """
    data = 'data/publications_without_abstract.csv'

    with open(data) as f:
        df = pd.read_csv(f, sep=';')
    return df


def get_all_dois(df):
    """
    Gets all the dois from the dataframe and returns them as a list
    :param df:
    :return:
    """
    dois = df['doi']
    # remove NaNs
    dois = dois.dropna()
    dois.tolist()
    return dois
