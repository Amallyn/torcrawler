# -*- coding: utf-8 -*-

u"""Frontier Manager

Inspired by Frontera Frontier
"""

__usage__ = u"""TODO - Usage: python3 frontier.py [options] [url]

Options:
  -u ..., --url=...       Website URL to crawl
  -h, --help              show this help
  -p, --path              www path where files were stored eg. /var/www
  -d                      show debugging information

Examples:
  python3 frontier.py --url='https://www.nytimes3xbfgragh.onion/' --path='/var/www'
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/05/01 11:45:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os
import requests    
from datetime import datetime
# url parser
from urllib.parse import urlsplit
# html parser
from bs4 import BeautifulSoup

from settings import WWW_DIR, WORKBOOK, MAX_N_REQUESTS, SEEDS
from workbook import CrawlWorkbook
from link import WeightedLink
from search import SearchEngine

class FrontierManager():
    """
    Frontier Manager
    
    seeds in request form
    """
    # seeds to start crawling
    seeds = []
    # links to crawl
    links = []
    # links crawled
    links_done = []

    # /! Will have to go in a Frontera Middleware at some point
    # weighted links to crawl
    weighted_links = None
    # weighted links crawled
    weighted_links_done = []
    # weighted    
    ignore_seeds = {}
    # weighted    
    ignored_pages = set()

    requests = []
    requests_done = []
        
    max_n_requests = 10

    searchengine = None
        
    crawl_book = None
    
    # /! def __init__(self, settings=SETTINGS, seeds=SETTINGS['SEEDS']):
    def __init__(self, seeds=[]):
        """ init with seeds
        
        Init with seeds
        Create/Open a file for storing progress
        """
        #self.settings = settings

        self.searchengine = SearchEngine()
        self.searchengine.db_connect()

        self.crawl_book = CrawlWorkbook(path=WWW_DIR, url=seeds[0].url)
        self.crawl_book.wb_open()

        # /! Will have to go in a Frontera Middleware at some point
        # retrieve weighted_links, weighted_links_done...
        self.weighted_links = self.crawl_book.weighted_links        
        self.weighted_links_done = self.crawl_book.weighted_links_done       
        self.ignore_seeds =  self.crawl_book.ignore_seeds
        self.ignored_pages =  self.crawl_book.ignored_pages
      
        self.add_seeds(seeds)

        # build requests from weighted_links
        for wl in self.weighted_links:
            self.requests.append(requests.Request(url=wl.url))
        for wl in self.weighted_links_done:
            self.requests_done.append(requests.Request(url=wl.url))
 
    def add_seeds(self, seeds):
        """
        add seeds
        
        /! not append
        """
        self.seeds = seeds
        if self.weighted_links is None:
            self.weighted_links = [WeightedLink(url=seed.url) for seed in self.seeds]
        if self.weighted_links is not None and len(self.weighted_links) == 0:
            self.weighted_links = [WeightedLink(url=seed.url) for seed in self.seeds]
        
    def request_error(request, error_code):
        """
        TODO
        """
        pass
                
    def start(self):
        # should open workbook as well
        self.searchengine.db_connect()

    def stop(self):
        # should save workbook, maybe init values with as well
        self.searchengine.db_close()
      
    def finished(self):
        """
        Quick check if crawling is finished. Called pretty often, please make sure calls are lightweight.
        """
        return not self.weighted_links

    def page_crawled(self, response):
        """
        This method is called every time a page has been crawled.
        """
#        print('Frontier: page_crawled')
#        print(response.url)
#        print(len(self.requests_done))
#        print(len(self.requests))
        self.requests_done.append(response.request)
        self.requests = [req for req in self.requests if req.url != response.request.url]
#        print(len(self.requests_done))
#        print(len(self.requests))

        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        title = u''
        if soup is not None:            
            titles = soup.find('title')
            if titles is not None:
                title = titles.string
        
        # extract first weighted link matchinq response.request.url
        wl = next((x for x in self.weighted_links if x.url == response.request.url), None)
        if wl:
            self.crawl_book.ws_writeln(WORKBOOK['crawler']['worksheet']['crawledpages']['TITLE'], wl)
            self.crawl_book.wb_save()
            
        # update weighted_links from resquests
        self.weighted_links = [wl for wl in self.weighted_links if wl.url != response.request.url]
        
        self.crawl_book.ws_writerows(WORKBOOK['crawler']['worksheet']['tocrawlpages']['TITLE'], self.weighted_links)
        
        print('Frontier: ', len(self.requests), 'pages to crawl -', len(self.requests_done), 'crawled pages -', len(self.ignored_pages), 'ignored pages')
        
    def get_next_requests(self, max_n_requests=MAX_N_REQUESTS):
        """
        Returns a list of next urls to be crawled.
        Parameters:	

        max_next_requests (int) – Maximum number of urls to be returned by this method.

        Returns:	

        list of weighted links.
        """
        # return first max_n_requests links
        return self.requests[:max_n_requests]
        #return self.weighted_links[:max_n_requests]
        
    def links_extracted(self, request, links):
        """
        add links to crawl found in response (from request)
        """
        print('Frontier: links_extracted')
        for req in links:
            already_there = False
            # extract first request matchinq request.url
            inreqs = next((x for x in self.requests if x.url == req.url), None)
            if not inreqs:
                # extract first request matchinq request.url
                inreqsdone = next((x for x in self.requests_done if x.url == req.url), None)
                if not inreqsdone:
                    self.requests.append(req)
                    self.weighted_links.append(WeightedLink(url=req.url))

            wbwsname = WORKBOOK['crawler']['worksheet']['tocrawlpages']['TITLE']
            self.crawl_book.ws_writerows(wbwsname, self.weighted_links)
            
            
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

    if len(argv)<2:
        print("Arguments error")
        print(__usage__)
        sys.exit(2)

    w_l_00 = WeightedLink(u'https://www.apple.xlsx/',
                      u'New York Times',
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      1024,
                      u'bla bla')
                      
    w_l_01 = WeightedLink(u'https://www.apple.xlsx/mehpage',
                      u'New York Times - Meh',
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      0.1,
                      u'meh')
                      
    w_l_02 = WeightedLink(u'https://www.apple.xlsx/megapage',
                      u'New York Times - mega',
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      2048,
                      u'mega bla bla')
    w_l_03 = WeightedLink(u'https://www.apple.xlsx/useless',
                      u'New York Times - useless',
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      2048,
                      u'mega no no')
    w_l_04 = WeightedLink(u'https://www.apple.xlsx/nopage',
                      u'New York Times - mega',
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      2048,
                      u'no no')
    
    cwb = CrawlWorkbook(path, url)
    cwb.wb_open()

    wbwsname = WORKBOOK['crawler']['worksheet']['crawledpages']['TITLE']
    cwb.ws_writeln(wbwsname, w_l_00)
    cwb.wb_save()

    wbwsname = WORKBOOK['crawler']['worksheet']['tocrawlpages']['TITLE']
    cwb.ws_appendrows(wbwsname, [ w_l_01, w_l_02 ])

    wbwsname = WORKBOOK['crawler']['worksheet']['ignoredpages']['TITLE']
    cwb.ws_writerows(wbwsname, [ w_l_03, w_l_04 ])

    from settings import SEEDS
    frontier = FrontierManager(seeds=[requests.Request(url=url) for url in SEEDS])
    print('--- Tests ---')
    print('------')
    print(frontier.seeds[0].url)
    print('------')
    print(frontier.requests[0].url)
    print(len(frontier.requests))
    print(len(frontier.requests_done))

    print('------')
    print(frontier.weighted_links)
    wl = next((x for x in frontier.weighted_links if x.url == 'https://www.apple.xlsx/mehpage'), None)
    print('------')
    print(wl)
    frontier.weighted_links = [wl for wl in frontier.weighted_links if wl.url != 'https://www.apple.xlsx/mehpage']
    print('------')
    print(frontier.weighted_links)
    print('--- End Tests ---')
    
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])

    
    