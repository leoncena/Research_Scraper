import time
from abc import ABC, abstractmethod, abstractproperty

import cloudscraper
import requests
from bs4 import BeautifulSoup
from helium import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ScraperAbstract(ABC):
    """
    Abstract class for all scrapers
    """

    @property
    @abstractmethod
    def domain(self):
        pass

    @property
    @abstractmethod
    def legal_params(self):
        pass

    # @abstractmethod
    # def _set_scraping_parameters(self):
    #     """
    #     Scrapers need to overwrite this method to set the legal scraping parameters \n
    #     """
    #     pass

    @abstractmethod
    def scrape_by_url(self, url, params=None):
        """
        Scrape a publication with a url
        """
        pass

    def get_page_with_requests(self, url):
        """
        Requests a page and returns the response
        :param url: URL of a publication
        :return: Website response
        """

        headers = {  # todo make logic for this
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}
        response = requests.get(url, headers=headers)
        print(response.status_code)
        assert response.status_code == 200
        return response

    def get_page_with_cloudscraper(self, url):
        """
        Requests a page and returns the response
        :param url: URL of a publication
        :return: Website response
        """
        scraper = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )
        response = scraper.get(url)
        print(response.status_code)
        assert response.status_code == 200
        return response

    def get_HTML_helium(self, url):
        """
        Get HTML from a website using helium and ChromeDriver. Helium is a lightweight Selenium adapter. It comes with simple wait and click functions.
        Method runs headless per default and has JS activated. By adding arguments the method mimics a user so that Elesevier returns the full HTML and allows loading.
        Be aware that this method is quite slow and schould only be used if classic requests method cannot access information thus only use that for dynamic data.
        :param url:
        :return: html content of the page
        """
        # helium does not work for science direct, so we use selenium instead => works!
        start = time.time()

        # Tricking Elsevier
        options = Options()
        options.add_argument("--headless=chrome")
        options.add_argument("--enable-javascript")
        # options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_argument("window-size=1920,1080")
        browser = start_chrome(url, options=options)

        # todo maybe move helium to ieer scraper
        wait_until_start = time.time()
        wait_until(lambda: not Text("Loading...").exists(), timeout_secs=10,
                   interval_secs=0.5)  # Experimental: wait until no 'Loading...' text is visible
        wait_until_end = time.time()

        scroll_start = time.time()
        scroll_down(20000)  # scroll down a lot
        print(f'scrolling took {time.time() - scroll_start} seconds')
        html = browser.page_source
        kill_browser()

        end = time.time()

        # todo remove prints
        print(
            f'Browser closed in {end - start} seconds, including '
            f'{wait_until_end - wait_until_start} seconds of waiting, thus '
            f'{end - start - wait_until_end + wait_until_start} seconds of loading.')

        return html

    def get_HTML_selenium(self, url, os):
        """
        Get HTML from a website using Selenium and ChromeDriver. Methods runs headless per default and has JS activated.
        Be aware that this method is quite slow and schould only be used if classic requests method cannot access information thus only use that for dynamic data.
        :param url: URL of a website
        :param os: Operating system of the user (Windows, Linux, Mac)
        :return: HTML with all loaded content
        """
        # todo path logic for other devices
        if os == 'mac':
            PATH_MAC = '../driver/chromedriverMAC'
        options = Options()
        options.add_argument("--headless=chrome")
        options.add_argument("--enable-javascript")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        start = time.time()

        driver = webdriver.Chrome(PATH_MAC, options=options)
        driver.get(url)
        break_time = 5
        time.sleep(break_time)

        # todo if content owned by WWU add sleep to load more content, or not !
        html = driver.page_source
        driver.close()

        end = time.time()

        # todo remove prints
        print(
            f'Browser closed in {end - start} seconds, including {break_time} '
            f'seconds of waiting (hard value), thus {end - start - break_time}'
            f' seconds of loading.')
        return html

    def get_bs(self, url, method='requests'):
        """
        Returns the Beautiful Soup object of a url \n
        It downloads the HTML of the url and parses it with Beautiful Soup
        :param url: URL of a publication
        :param method: Method of HTML download (requests, helium, selenium)
        :return: bs4 object
        """
        try:
            if method == 'requests':
                request = self.get_page_with_requests(url)
                bs = BeautifulSoup(request.content, 'html.parser')
            elif method == 'cloud':
                request = self.get_page_with_cloudscraper(url)
                bs = BeautifulSoup(request.content, 'html.parser')
            # elif method == 'requests_html':
            #     r = get_page_with_requsts_html(url)
            #     bs = BeautifulSoup(r.content, 'html.parser')
            elif method == 'selenium':
                request = self.get_HTML_selenium(url, os='mac')
                bs = BeautifulSoup(request, 'html.parser')  # selenium already returns html
            elif method == 'helium':
                request = self.get_HTML_helium(url)
                bs = BeautifulSoup(request, 'html.parser')  # helium already returns html
            else:
                raise ValueError('Method not supported')

        except Exception as e:  # todo insert specific exception
            print(f'[Error catched- scraper_abstract.py: get_bs] : {e}', url)
            return None
        return bs

    def check_params_legal(self, params):
        """
        Checks if the params are legal and raises error in that case
        :param params:
        :return:
        """
        if params is not None:  # cannot interate over None object
            for param in params:
                if param not in self.legal_params:
                    raise ValueError(f'Param \'{param}\' is not legal. Legal params are: {self.legal_params}')
