import re
from bs4 import BeautifulSoup
import requests
import time


def check_if_doi_link(url):
    """
    Returns if a passed url is a DOI link
    :param url: url to check
    :return:
    """
    doi_link_regex = re.compile(r'^(https?:\/\/)?'  # A doi links starts with http:// or https://
                                r'(www\.)?'  # or start with www.
                                r'(doi\.org\/)'  # followed by doi.org/
                                r'([a-zA-Z0-9\-\.\_]+'  # prefix: any character, number, - or . or _ any number of times
                                r'\/[a-zA-Z0-9\-\.\_]+)'  # suffix: any character, number, - or . or _ any number of times
                                r'$')

    if doi_link_regex.match(url):
        return True
    else:
        return False


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
        print(f'[utils.py: get_link] Connection Error')

# start = time.time()
# print(resolve_url('https://doi.org/10.1007/s00450-009-0054-z'))
# print(time.time() - start)
