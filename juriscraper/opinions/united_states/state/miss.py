# Auth: ryee
# Review: mlr
# Date: 2013-04-26
# Court Contact: bkraft@courts.ms.gov (see https://courts.ms.gov/aoc/aoc.php)

from juriscraper.OpinionSite import OpinionSite
import re
import time
from datetime import date
from lxml import html


class Site(OpinionSite):
    def __init__(self, *args, **kwargs):
        super(Site, self).__init__(*args, **kwargs)
        self.court_id = self.__module__
        self.url = 'http://courts.ms.gov/scripts/websiteX_cgi.exe/GetOpinion?Year=%s&Court=Supreme+Court&Submit=Submit' % date.today().year  # noqa: E501
        self.back_scrape_iterable = range(1990, 2019)
        self.base = '//tr[following-sibling::tr[1]/td[2][text()]]'

    def _get_case_names(self):
        # This could be a very simple xpath, but alas, they have missing fields
        # for some cases. As a result, this xpath checks that the fields are
        # valid (following-sibling), and only grabs those cases.
        case_names = []
        for e in self.html.xpath('{base}/td/b/a'.format(base=self.base)):
            s = html.tostring(e, method='text', encoding='unicode')
            case_names.append(s)
        return case_names

    def _get_download_urls(self):
        path = '{base}/td/b/a/@href'.format(base=self.base)
        return list(self.html.xpath(path))

        hrefs = list(self.html.xpath(path))
        good_anchors = list()
        for href in hrefs:
            if '/Imaging\\' in href:
                basename = href.split('\\')[-1]
                href = "http://courts.ms.gov/Images/Opinions/{}"
                href = href.format(basename)
            good_anchors.append(href)
        return good_anchors

    def _get_case_dates(self):
        path = '{base}/following-sibling::tr[1]/td[3]//@href'.format(
            base=self.base)
        dates = []
        date_re = re.compile(r'(\d{2}-\d{2}-\d{4})')
        for href in self.html.xpath(path):
            date_string = date_re.search(href).group(1)
            dates.append(date.fromtimestamp(time.mktime(time.strptime(
                date_string, '%m-%d-%Y'))))
        return dates

    def _get_precedential_statuses(self):
        return ['Published'] * len(self.case_names)

    def _get_docket_numbers(self):
        path = '{base}/following-sibling::tr[1]/td[1]/text()'.format(
            base=self.base)
        return list(self.html.xpath(path))

    def _download_backwards(self, year):
        self.url = 'http://courts.ms.gov/scripts/websiteX_cgi.exe/GetOpinion?Year=%s&Court=Supreme+Court&Submit=Submit' % year  # noqa: E501
        self.html = self._download()
