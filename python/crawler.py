# -*- coding: utf-8 -*-

u"""Generic Crawler

Generic crawler for searching with a Manticore Database
compatible with socks5h proxies
"""

__usage__ = u"""Usage: python3 crawler.py [options] [url]

Options:
  -u ..., --url=...       Website URL to crawl
  -h, --help              show this help
  -p, --path              www path where files are stored eg. /var/www
  -d                      show debugging information
  
Examples:
  python3 crawler.py --url='https://www.nytimes3xbfgragh.onion/' --path='/var/www'
  crawls the website for searching in a Manticore Database
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/04/01 19:05:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os

# https requests
import requests
# html parser
from bs4 import BeautifulSoup
# url parser
from urllib.parse import urljoin, urlsplit

from settings import WWW_DIR
from search import SearchEngine

# Our frontier
from frontier import CrawlFrontier

# Just for path for now
from workbook import CrawlWorkbook

class WebPage():
    url = u''
    title = None
    html_doc = u''
    
    response = None
    soup = None
    links = {}
    links_href = {}
    ignored_links = set()
    
    # path to save the html page
    save_dir = u'./'
    
    def __init__(self, url=u''):
        """
        init
        """
        self.url = url
        self.save_dir = CrawlWorkbook.wb_html_pages_path(url=url, path=WWW_DIR)

    def __unicode__(self):
        return self.title

    def response_check(self):
        """
        Check if response is different than requested url
        
        Modify response url when irrelevant differences found
        eg. url#...
        """
        if self.url != self.response.url:
            if self.url == self.response.url + '/' or self.response.url.startswith(self.url+'#'):
                self.response.url = self.url
            else:
                print('!!! different !!!')
                print('url: ', self.url)
                print('response url: ', self.response.url)

    def get(self, session):
        """
        download and process web page
        
        session: requests.Session()
        """
        if session:
            print(u'----------------')
            print(u'Web Page: get', self.url)
            self.response = session.get(self.url)
            self.html_doc = self.response.text
            self.soup = BeautifulSoup(self.html_doc, 'html.parser')
            self.title = self.soup.find('title')
            #if self.title is None:
            #    #print(u"Web Page: Ignore page - Title: None")
            #    self.title = u''
            #else:
            self.response_check()
            self.title = self.title.string
            self.save_to_file()
            print(u'Web Page: ' + self.title)
        else:
            print(u'Web Page: Session error')

    def save_to_file(self):
        """
        save page to a #.html file where # is the title crc32
        """
        # eg. /var/www/html/apple.com/256.html
        url_hash = SearchEngine.hash_url(self.url)
        file_name = os.path.join(self.save_dir, str(url_hash) + '.html') 
        print(file_name)            
        f = open(file_name, 'w')
        f.write(self.soup.prettify())
        f.close()
        
    def find_links(self):
        """
        Find links in web page
        
        Return a href links that are on the same website 
        only keep links with the same starting url
        starting_url/link...
        """      
        if self.soup:
            links = self.soup.find_all('a')
            
            # url root (eg.: https://toto.com/)
            url_base = urljoin(self.url, '/')
            
            # list comprehension readability/optimization tradeoff
            # absolute links
            links_href_absolute_startswith = [link.get('href') for link in links if link and link.get('href') and link.get('href').startswith(url_base)]
            # relative links
            links_href_relative = [ urljoin(self.url, link.get('href')) for link in links if link and link.get('href') and link.get('href').startswith('/')
                                and link.get('href') != '/' and not link.get('href').startswith('/#')
                                ]
                               
            self.links_href = links_href_absolute_startswith + links_href_relative
            print(u'Web Page:',len(links_href_absolute_startswith), u'absolute links, ', len(links_href_relative), u'relative links found, ',
                  len(self.ignored_links), u'ignored links.')

            return self.links_href
            
# web_page_list
class GenericCrawler():
    """
    Generic class for Web page Crawlers

    crawls a website for web pages
    sends all data to a manticore database
    NOTE: could use ABC class for WebPage
    """
    web_page_list = None
    web_page_done_list = None
    
    site_url = u''
    site_cat_urls = {}

    searchengine = None
        
    # Requests session for multiple url get
    session = None
    proxies = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150')

    # frontier
    frontier = None
        
    # Maximum number of urls to crawl per inner loop
    max_n_requests = 10 

    def __init__(self, url=u'https://www.nytimes3xbfgragh.onion/section/nyregion',
              proxies = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150')):
        """
        Init
        """
        self.searchengine = SearchEngine()
        # work from the base url / site root
        self.site_url = urljoin(url, '/')
        self.proxies = proxies

    def __unicode__(self):
        return self.site_url

    def session_start(self):
        """
        Start the session to handle HTTPS requests

        Session stays on for multiple url get
        """
        self.session = requests.Session()
        self.session.proxies.update(self.proxies)
              
    def crawl(self):
        """
        crawl website from url
        
        stores web pages in a manticore DB
        """

        self.searchengine.db_connect()

        self.session_start()

        self.frontier = CrawlFrontier()
        while True:
            next_urls = self.frontier.get_next_urls()
            if not next_urls:
                break
            for url in next_urls:
                    try:
                        web_page = WebPage(url)
                        web_page.get(self.session)
                        self.searchengine.db_replace_into(title=web_page.title, url=web_page.url,body=web_page.html_doc)
                        links = web_page.find_links()

                        self.frontier.page_crawled(web_page.response)
                        print('Crawled', web_page.response.url, '(found', len(links), 'urls)')
                        if web_page.url != web_page.response.url:
                            # store redirected url in notes
                            web_page.notes = web_page.response.url
                            print('!!! Different response !!!')
                            print('url: ', web_page.url)
                            print('response url: ', web_page.response.url)
                        
                        if links:
                            self.frontier.links_extracted(web_page.response.request, links)
                        if web_page.ignored_links:
                            # TODO: check for dupes or use set
                            self.frontier.ignored_pages.extend(web_page.ignored_links)

                    except requests.RequestException as e:
                        error_code = type(e).__name__
                        #request_error(request, error_code)
                        #print('Failed to process request', request.url, 'Error:', e)
                        print('Failed to process request - Error:', e)
                        # start new session
                        self.session_start()
        
        self.searchengine.db_close()
       
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
            opts, args = getopt.getopt(argv, "hup:d", ["help", "url=", "path="])
        except getopt.error as msg:
             raise Usage(msg)            
        url = u'http://localhost'
        path = u'/var/www'
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(__usage__)                   
                sys.exit()                  
            elif opt == '-d':
                global _debug               
                _debug = 1                  
            elif opt in ("-u", "--url"):
                url = arg               
            elif opt in ("-p", "--path"):
                path = arg               
    except Usage as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    #if len(argv)<2:
    #    print("Arguments error")
    #    print(__usage__)
    #    sys.exit(2)
    
    crawler = GenericCrawler(url = url,
              proxies = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150'))
    crawler.crawl()
        
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
