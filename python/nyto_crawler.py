# -*- coding: utf-8 -*-

u"""nyto_crawler

New York Times Crawler for searching with a Manticore Database
Excludes Spanish and French pages
compatible with socks5h proxies
"""

__usage__ = u"""Usage: python3 nyto_crawler.py [options] [url]

Options:
  -u ..., --url=...       Website URL to crawl
  -h, --help              show this help
  -d                      show debugging information

Examples:
  python3 nyto_crawler.py --url='https://www.nytimes3xbfgragh.onion/'
  Excludes url/es/ and url/fr/ pages
    crawls the website for searching in a Manticore Database
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/06/01 09:10:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

# https requests
import requests
# html parser
from bs4 import BeautifulSoup
# url parser
from urllib.parse import urljoin

# database
import pymysql.cursors

# Our frontier
from crawl_frontier import CrawlFrontier

from generic_crawler import WebPage, GenericCrawler

class NytPage(WebPage):
    def __init__(self, url=u'', save_dir = u'./'):
        """
        init
        """
        super().__init__(url, save_dir)
        
    def find_links(self):
        """
        Find links in web page
        
        Return a href links that are on the same website 
        only keep links with the same starting url
        starting_url/link...
        Excludes Spanish and French pages
        TODO: add weight/priority to links
        """      
        if self.soup:
            links = self.soup.find_all('a')
            
            # url root (eg.: https://toto.com/)
            url_base = urljoin(self.url, '/')
            # ignore Spanish and French pages
            prefix_es = '/es/'
            url_base_es_ignore = urljoin(self.url, prefix_es)
            prefix_fr = '/fr/'
            url_base_fr_ignore = urljoin(self.url, prefix_fr)
            # nyregion only
            prefix_nyregion = '/section/nyregion'
            url_base_nyregion = urljoin(self.url, prefix_nyregion)
            
            # list comprehension readability/optimization tradeoff
            # absolute links
            links_href_absolute_startswith = [link.get('href') for link in links if link and link.get('href') and link.get('href').startswith(url_base)
                                and not link.get('href').startswith(url_base_es_ignore)
                                and not link.get('href').startswith(url_base_fr_ignore)
                                ]
            # relative links
            links_href_relative = [ urljoin(self.url, link.get('href')) for link in links if link and link.get('href') and link.get('href').startswith('/')
                                and link.get('href') != '/' and not link.get('href').startswith('/#')
                                and not link.get('href').startswith(prefix_es)
                                and not link.get('href').startswith(prefix_fr)
                                ]
                                
            self.links_href = links_href_absolute_startswith + links_href_relative
            print(u'Web Page:',len(links_href_absolute_startswith), u'absolute links and',len(links_href_relative), u'relative links found')

            return self.links_href


class NytCrawler(GenericCrawler):
    def __init__(self, url=u'https://www.nytimes3xbfgragh.onion/section/nyregion',
              proxies = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150'),
              db_host='localhost',
              db_user='',
              db_password='',
              db_port=9306,
              db_cursorclass=pymysql.cursors.DictCursor):
        """
        Init
        """
        super().__init__(url,
              proxies,
              db_host,
              db_user,
              db_password,
              db_port,
              db_cursorclass)
        
    def crawl(self):
        """
        crawl website from url
        
        stores web pages in a manticore DB
        NOTE: could use ABC class for WebPage/NytPage
        """

        self.db_connect()
        self.db_commit()

        self.session_start()

        # crawl from one base url / site root
        seeds = [ self.site_url ]
        self.frontier = CrawlFrontier(seeds)

        while True:
            next_urls = self.frontier.get_next_urls()
            if not next_urls:
                break
            for url in next_urls:
                    try:
                        web_page = NytPage(url, self.frontier.seed_dir)
                        web_page.get(self.session)
                        web_page.db_replace_into(self.connection)
                        links = web_page.find_links()

                        self.frontier.page_crawled(web_page.response)
                        print('Crawled', web_page.response.url, '(found', len(links), 'urls)')
    
                        if links:
                            self.frontier.links_extracted(web_page.response.request, links)
                    except requests.RequestException as e:
                        error_code = type(e).__name__
                        #request_error(request, error_code)
                        #print('Failed to process request', request.url, 'Error:', e)
                        print('Failed to process request - Error:', e)
                        # start new session
                        self.session_start()        
        self.db_close()
        
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
        
def main(argv=None):
    """
    main
    """
    import getopt
    if argv is None:
        argv = sys.argv

    try:
        try:                                
            opts, args = getopt.getopt(argv, "hu:d", ["help", "url="])
        except getopt.error as msg:
             raise Usage(msg)            
        url = 'http://localhost'
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(__usage__)                   
                sys.exit()                  
            elif opt == '-d':
                global _debug               
                _debug = 1                  
            elif opt in ("-u", "--url"):
                url = arg               
    except Usage as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    if len(argv)<1:
        print("Arguments error")
        print(__usage__)
        sys.exit(2)
    
    crawler = NytCrawler(url = url,
              proxies = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150'),
              db_host = 'localhost',
              db_user = '',
              db_password = '',
              db_port = 9306,
              db_cursorclass = pymysql.cursors.DictCursor)
    crawler.crawl()
    
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
    