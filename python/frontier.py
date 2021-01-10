# -*- coding: utf-8 -*-

u"""frontier

crawl frontier
Inspired by Frontera Frontier Class
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

from datetime import datetime

# url parser
from urllib.parse import urlsplit

# html parser
from bs4 import BeautifulSoup

from settings import WWW_DIR, SEEDS, WORKBOOK

# Serialize progress
from workbook import CrawlWorkbook

from link import WeightedLink

DEFAULT_LINK_WEIGHT = 1024

class CrawlFrontier():
    # links to crawl
    links = []
    # links crawled
    links_done = []

    # weighted links to crawl
    weighted_links = []
    # weighted links crawled
    weighted_links_done = []
    # weighted    
    ignore_seeds = {}
    # weighted    
    ignored_pages = set()

    crawl_book = None
    
    def __init__(self, seeds=SEEDS):
        """ init with seeds
        
        Init with seeds
        Create/Open a file for storing progress
        """
        self.links = list(seeds)

        self.crawl_book = CrawlWorkbook(path=WWW_DIR, url=self.links[0])
        self.crawl_book.wb_open()

        # retrieve weighted_links, weighted_links_done...
        self.weighted_links = self.crawl_book.weighted_links        
        self.weighted_links_done = self.crawl_book.weighted_links_done       
        self.ignore_seeds =  self.crawl_book.ignore_seeds
        self.ignored_pages =  self.crawl_book.ignored_pages
        
        if self.weighted_links is None:
            # No links or no file
            for link in self.links:
                self.weighted_links.append(WeightedLink(link, '',
                                           '',
                                           DEFAULT_LINK_WEIGHT,
                                           ''))
        else:
            # Maintain links and links_done for now
            for weighted_link in self.weighted_links:
                self.links.append(weighted_link.url) 
        if self.weighted_links_done is not None:
            for weighted_link in self.weighted_links_done:
                self.links_done.append(weighted_link.url) 

    def __unicode__(self):
        # based on the first seed website eg. www.nytimes3xbfgragh.onion
        return urlsplit(self.seeds[0]).netloc
        
    def frontier_start(self):
        pass
      
    def frontier_stop(self):
        pass
      
    def finished(self):
        """
        Quick check if crawling is finished. Called pretty often, please make sure calls are lightweight.
        """
        return False

    def weighted_link_remove(self, weighted_link=None):
        """
        Remove a weighted_link from self.weighted_links
        
        Remove a weighted_link that matches its url value
        """
        if weighted_link is not None:
            for link in self.weighted_links:
                if link.url == weighted_link.url:
                    self.weighted_links.remove(link)
        
    def page_crawled(self, response, weighted_link=None):
        """
        This method is called every time a page has been crawled.
        
        /!\ So you can test without the WeightedLink class
        and only receive the response argument
        """
        if response.url in self.links:
            self.links_done.append(response.url)
            self.links.remove(response.url)

            # update the progress file
            web_page_weight = DEFAULT_LINK_WEIGHT
            
            # Use soup, again...
            html_doc = response.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            title = u''
            if soup is not None:            
                titles = soup.find('title')
                if titles is not None:
                    title = titles.string
            #print('page_crawled: response.url ', response.url)
            # /!\ If you need to test without the WeightedLink class /!\
            if weighted_link is None:
                # remove link before adding title and date as should be in this list
                weighted_link = WeightedLink(response.url, title,
                                             datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                             DEFAULT_LINK_WEIGHT,
                                             '')
                self.weighted_link_remove(weighted_link)
                self.weighted_links_done.append(weighted_link)
                
                #print('page_crawled None: ', weighted_link)
            else:
                self.weighted_links_done.append(weighted_link)
                self.weighted_link_remove(weighted_link)


            self.crawl_book.ws_writeln(WORKBOOK['crawler']['worksheet']['crawledpages']['TITLE'], weighted_link)
            self.crawl_book.wb_save()
            #print('page_crawled: ', weighted_link)

            self.crawl_book.ws_writerows(WORKBOOK['crawler']['worksheet']['ignoredpages']['TITLE'], self.ignored_pages)
        
        print('Frontier: ', len(self.links), 'pages to crawl -', len(self.links_done), 'crawled pages -', len(self.ignored_pages), 'ignored pages')
        
    def get_next_urls(self, max_n_requests=10):
        """
        Returns a list of next urls to be crawled.
        Parameters:	

        max_next_requests (int) – Maximum number of urls to be returned by this method.

        Returns:	

        list of weighted links.
        """
        # return first max_n_requests links
        return self.links[:max_n_requests]
        #return self.weighted_links[:max_n_requests]
        
    def links_extracted(self, reponse, links, weighted_links=None):
        """
        add links to crawl found in response (from request)
        
        /!\ you can test without the weighted links parameter
        """
        for link in links:
            if link and link not in self.links_done and link not in self.links:
                self.links.append(link)
        # print(len(links), "links extracted")
        # At least one new link, update Pages to crawl Worksheet
        # /!\ If you need to test without the WeightedLink class /!\
        if links[0]:
            if weighted_links is None:
                weighted_links = []
                for url in self.links:
                    weighted_link = WeightedLink(url, '',
                                                '',
                                                DEFAULT_LINK_WEIGHT,
                                                '')
                    weighted_links.append(weighted_link)
            # TODO: check for dupes with set before unless checked before the call
            self.weighted_links.extend(weighted_links)

            self.crawl_book.ws_writeln(WORKBOOK['crawler']['worksheet']['crawledpages']['TITLE'], weighted_link)

            # TODO: check for dupes with set before unless checked before the call
            wbwsname = WORKBOOK['crawler']['worksheet']['tocrawlpages']['TITLE']
            self.crawl_book.ws_appendrows(wbwsname, weighted_links)
        
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
                      512,
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
                    
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])

    
    