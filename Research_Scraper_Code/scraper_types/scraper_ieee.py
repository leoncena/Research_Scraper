from scraper_abstract import ScraperAbstract


class ScraperIEEE(ScraperAbstract):
    """
    Class for the specific IEEE Scraper
    """

    def _set_domain(self):
        self.domain = 'ieeexplore.ieee.org'

    def scrape_by_url(self, url, params=None):
        pass
