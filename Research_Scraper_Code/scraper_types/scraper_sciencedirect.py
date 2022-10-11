from scraper_abstract import ScraperAbstract


class ScraperScienceDirect(ScraperAbstract):
    """
    Class for the specific ScienceDirect Scraper
    """

    def _set_domain(self):
        self.domain = 'www.sciencedirect.com'

    def scrape_by_url(self, url, params=None):
        pass
