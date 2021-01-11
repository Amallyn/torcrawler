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
from frontier import CrawlFrontier

from crawler import WebPage, GenericCrawler

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
            # ignores ugly, but faster this way
            # ignore Spanish and French pages
            prefix_es = '/es/'
            url_base_es_ignore = urljoin(self.url, prefix_es)
            prefix_fr = '/fr/'
            url_base_fr_ignore = urljoin(self.url, prefix_fr)
            prefix_newsletters = '/newsletters'
            url_base_newsletters = urljoin(self.url, prefix_newsletters)
            prefix_ca = '/ca/'
            url_base_ca = urljoin(self.url, prefix_ca)
            prefix_2021 = '/2021/'
            url_base_2021 = urljoin(self.url, prefix_2021)
            prefix_world = '/section/world'
            url_base_world = urljoin(self.url, prefix_world)
            prefix_videoworld = '/video/world'
            url_base_videoworld = urljoin(self.url, prefix_videoworld)
            prefix_food = '/section/food'
            url_base_food = urljoin(self.url, prefix_food)
            prefix_arts = '/section/arts'
            url_base_arts = urljoin(self.url, prefix_arts)
            prefix_sports = '/section/sports'
            url_base_sports = urljoin(self.url, prefix_sports)
            prefix_science = '/section/science'
            url_base_science = urljoin(self.url, prefix_science)
            prefix_books = '/section/books'
            url_base_books = urljoin(self.url, prefix_books)
            prefix_dealbook = '/section/business/dealbook'
            url_base_dealbook = urljoin(self.url, prefix_dealbook)
            prefix_pagesdealbook = '/pages/business/dealbook'
            url_base_pagesdealbook = urljoin(self.url, prefix_pagesdealbook)
            # nyregion only
            prefix_nyregion = '/section/nyregion'
            url_base_nyregion = urljoin(self.url, prefix_nyregion)

            # ignore list
            ignore_suffixes = ['/es/', '/fr/', '/ca/', '/newsletters', '/2021/',
                            '/2020/01/', '/2020/02/', '/2020/03/', '/2020/04/', '/2020/05/', '/2020/06/',
                            '/2020/07/', '/2020/08/', '/2020/09/', '/2020/10/',
                            '/2019/', '/2018/', '/2017/', '/2016/', '/2015/', '/2014/',
                            '/section/world', '/video/world', '/section/food', '/section/arts',
                            '/section/sports', '/section/science', '/section/books', '/section/travel', 
                            '/section/realestate', '/section/fashion', '/section/technology',
                            '/section/politics', '/section/business', '/section/style',
                            '/section/style/love', '/section/us', '/section/video', '/section/interactive',
                            '/section/t-magazine',
                            'section/fashion', '/issue/fashion',
                            '/section/business/dealbook', '/pages/business/dealbook',
                            '/privacy'
                            ]
            ignore_urls = [urljoin(self.url, suffix) for suffix in ignore_suffixes]
            
            links_href_absolute = []
            links_href_relative = []
            for link in links:
                if link and link.get('href'):
                    link_href = link.get('href')
                    ignore_link = False
                    # only keep website links, drop the rest
                    # absolute url
                    if link_href.startswith(url_base):
                        for ignore_url in ignore_urls:
                            if link_href.startswith(ignore_url):
                                self.ignored_links.add(link_href)
                                ignore_link = True
                                break
                        if ignore_link:
                            ignore_link = False
                        else:
                            links_href_absolute.append(link_href)
                    # relative link
                    elif link_href.startswith('/') and link_href != '/' and not link_href.startswith('/#'): 
                        for ignore_suffix in ignore_suffixes:
                            if link_href.startswith(ignore_suffix):
                                link_href = urljoin(self.url, link_href)
                                self.ignored_links.add(link_href)
                                ignore_link = True
                                break
                        if ignore_link:
                            ignore_link = False
                        else:
                            link_href = urljoin(self.url, link_href)
                            links_href_relative.append(link_href)
            self.links_href = links_href_absolute + links_href_relative
            print(u'Web Page:',len(links_href_absolute), u'absolute links and',len(links_href_relative), u'relative links found')
                    

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
                        if web_page.url != web_page.response.url:
                            print('!!! Different response !!!')
                            print('url: ', web_page.url)
                            print('response url: ', web_page.response.url)
    
                        if links:
                            self.frontier.links_extracted(web_page.response.request, links)

                        if web_page.ignored_links:
                            self.frontier.ignored_pages.update(web_page.ignored_links)
                            
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
    