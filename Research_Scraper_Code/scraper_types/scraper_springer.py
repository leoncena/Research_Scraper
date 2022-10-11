from scraper_abstract import ScraperAbstract


class ScraperSpringer(ScraperAbstract):
    """
    Class for the specific Springer Scraper
    """

    # init domain name
    def _set_domain(self):
        self.domain = 'link.springer.com'

    def scrape_by_url(self, url, params=None):
        pass


