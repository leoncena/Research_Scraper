import re
from bs4 import BeautifulSoup
import requests
import time


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
    try:
        r = requests.head(url, allow_redirects=True)
        return r.url
    except requests.exceptions.ConnectionError as e:
        print('[utils.py: get_link] Connection Error')
        return None
