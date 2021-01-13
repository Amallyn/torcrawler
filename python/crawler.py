# -*- coding: utf-8 -*-

u"""Crawler

crawls a website for web pages
sends all data to a manticore database via a frontier
compatible with socks5h proxies
"""

__usage__ = u"""Usage: python3 crawler.py [options]

Options:
  -h, --help              show this help
  -d                      show debugging information
  
Examples:
  python3 crawler.py
  crawls from the seeds for searching in a Manticore Database
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/04/01 19:05:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os
import re
# https requests
import requests
# url parser
from urllib.parse import urljoin, urlparse, urlsplit
# html parser
from bs4 import BeautifulSoup

from settings import SEEDS, PROXIES
from frontier import FrontierManager

# web_page_list
class Crawler():
    """
    Crawler

    crawls a website for web pages
    sends all data to a manticore database via a frontier
    TODO: from PyTorStemPrivoxy.py
    with cookie for session
    """
    
    # Requests session for multiple url get
    session = None
    proxies = PROXIES
    # frontier
    frontier = None

    # will be handled by a Middleware
    # initialize some HTTP headers
    # for later usage in URL requests
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent}

    url_base = ''
    # LINK_RE = re.compile(r'href="(.*?)"')
    
    def __init__(self):
        """
        Init
        """
        pass

    def session_start(self):
        """
        Start the session to handle HTTPS requests

        Session stays on for multiple url get
        """
        self.session = requests.Session()
        self.session.proxies.update(self.proxies)

    def extract_page_links(self, response):
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        links = soup.find_all('a')
        # absolute links
        links_href_absolute = [link.get('href') for link in links if link and link.get('href') and link.get('href').startswith(self.url_base)]
        # relative links
        links_href_relative = [ urljoin(self.url_base, link.get('href')) for link in links if link and link.get('href') and link.get('href').startswith('/')
                                and link.get('href') != '/' and not link.get('href').startswith('/#')
                                ]
        print(u'Web Page:',len(links_href_absolute), u'absolute links, ', len(links_href_relative), u'relative links found, ')        
        return links_href_absolute + links_href_relative
        # only interested in links, not assets... so soup is better
        # return [urljoin(response.url, link) for link in self.LINK_RE.findall(response.text)]
                      
    def crawl(self):
        """
        crawl website from url
        
        stores web pages in a manticore DB
        """

        self.session_start()

        # settings can be directly loaded by the frontier
        # constructor handling the seeds
        self.frontier = FrontierManager(seeds=[requests.Request(url=url) for url in SEEDS])
        
        # url root (eg.: https://toto.com/)
        # work with only one seed for now
        url = next(iter(SEEDS))
        parsed_uri = urlparse(url)
        self.url_base = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        #self.frontier.add_seeds(requests=[requests.Request(url=url) for url in settings.SEEDS])
        while True:
            next_requests = self.frontier.get_next_requests()
            if not next_requests:
                break
            for request in next_requests:
                    try:
                        if self.session:
                            print(u'----------------')
                            print(u'Web Page: get', request.url)
                            response = self.session.get(request.url)
                            #req1 = urllib2.Request(url1)
                            #response = urllib2.urlopen(req1)
                            #cookie = response.headers.get('Set-Cookie')
                            
                            ## Use the cookie is subsequent requests
                            #req2 = urllib2.Request(url2)
                            #req2.add_header('cookie', cookie)
                            #response = urllib2.urlopen(req2)            
                            links = [
                                requests.Request(url=url)
                                for url in self.extract_page_links(response)
                            ] # end links                
                            print(len(links), 'links found')
                            self.frontier.page_crawled(response)
                            if links:
                                self.frontier.links_extracted(request=response.request, links=links)

                    except requests.RequestException as e:
                        error_code = type(e).__name__
                        #frontier.request_error(request, error_code)
                        print('Failed to process request', request.url, 'Error:', e)                        # start new session

                        self.session_start()
      
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
            opts, args = getopt.getopt(argv, "h:d", ["help"])
        except getopt.error as msg:
             raise Usage(msg)            
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(__usage__)                   
                sys.exit()                  
            elif opt == '-d':
                global _debug               
                _debug = 1                  
    except Usage as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    #if len(argv)<2:
    #    print("Arguments error")
    #    print(__usage__)
    #    sys.exit(2)
    
    crawler = Crawler()
    crawler.crawl()
#    print('---  Crawl tests ---')
#    seeds=[requests.Request(url=url) for url in SEEDS]
#    print(seeds, len(seeds), [req.url for req in seeds])
#    crawler.frontier = FrontierManager(seeds=[requests.Request(url=url) for url in SEEDS])
#    print(seeds, len(seeds), [req.url for req in crawler.frontier.seeds])
#    print([req.url for req in crawler.frontier.requests])
#    next_reqs = crawler.frontier.get_next_requests()
#    print('next_reqs', len(next_reqs))
#    for req in next_reqs:
#        print(req.url)
#    print(crawler.proxies)
#    crawler.session_start()
#    # ok below
#    response = crawler.session.get(next_reqs[0].url)
#    print(response.text)
#    crawler.frontier.page_crawled(response)        
#    print('---  End Crawl tests ---')
    
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
