# -*- coding: utf-8 -*-

u"""frontier

crawl frontier
Inspired by Frontera Frontier Class
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

# Serialize progress
from crawl_serialize import CrawlWorkbook, WORKSHEET_CRAWLED_PAGES, WORKSHEET_PAGES_TO_CRAWL

from weighted_link import WeightedLink

DEFAULT_LINK_WEIGHT = 1024

class CrawlFrontier():
    # starting urls
    seeds = {} 
    # links to crawl
    links = []
    # links crawled
    links_done = []

    # weighted links to crawl
    weighted_links = []
    # weighted links crawled
    weighted_links_done = []

    # storage path
    www_dir = u'/var/www'
    # eg. /var/www/html
    html_dir = os.path.join(www_dir, u'html')
    # eg. /var/www/html/www.nytimes3xbfgragh.onion/
    seed_dir = html_dir
    
    # progress saved in a file
    file_name = u''
    crawl_book = None
    
    def __init__(self, seeds=['https://apple.com']):
        """ init with seeds
        
        Init with seeds
        Create/Open a file for storing progress
        """
        self.seeds = seeds
        self.links = seeds
            
        # progress file name
        # based on the first website eg. www.nytimes3xbfgragh.onion
        # eg. self.seed_dir /var/www/html/www.nytimes3xbfgragh.onion/
        #     self.file_name /var/www/html/www.nytimes3xbfgragh.onion.xlsx
        self.seed_dir = os.path.join(self.html_dir, urlsplit(self.seeds[0]).netloc)
        if not os.path.exists(self.seed_dir):
            os.makedirs(self.seed_dir)
        self.file_name = os.path.join(self.html_dir, urlsplit(self.seeds[0]).netloc + '.xlsx')
        # progress serialize
        self.crawl_book = CrawlWorkbook(self.file_name)
        # retrieve weighted_links and weighted_links_done 
        weighted_links = self.crawl_book.wb_open()
        if weighted_links is None:
            # No links or no file
            for link in self.links:
                self.weighted_links.append(WeightedLink(link, '',
                                           '',
                                           DEFAULT_LINK_WEIGHT,
                                           ''))
        else:
            self.weighted_links_done = weighted_links[0]
            self.weighted_links = weighted_links[1]
            # Maintain links and links_done for now
            for weighted_link in self.weighted_links:
                self.links.append(weighted_link.url) 
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
                
                self.crawl_book.ws_writeln(WORKSHEET_CRAWLED_PAGES, weighted_link)
                #print('page_crawled None: ', weighted_link)
            else:
                self.weighted_links_done.append(weighted_link)
                self.weighted_link_remove(weighted_link)

                self.crawl_book.ws_writeln(WORKSHEET_CRAWLED_PAGES, weighted_link)

                #print('page_crawled: ', weighted_link)
            self.crawl_book.wb_save()
        
        print('Frontier: ', len(self.links), 'pages to crawl and', len(self.links_done), 'crawled pages')
        
    def get_next_urls(self, max_n_requests=10):
        """
        Returns a list of next urls to be crawled.
        Parameters:	

        max_next_requests (int) – Maximum number of urls to be returned by this method.
        kwargs (dict) – A parameters from downloader component.

        Returns:	

        list of urls.
        """
        # return first max_n_requests links
        return self.links[:max_n_requests]
        #return self.weigthed_links[:max_n_requests]
        
    def add_seeds(self, seeds=['https://apple.com']):
        """
        add seed urls to crawl
        
        eg. seeds=['https://site01.com/', 'https://site02.com/']
        TO DELETE - useless method
        """
        self.seeds = seeds
        self.links = seeds

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
            self.crawl_book.ws_reset(WORKSHEET_PAGES_TO_CRAWL)
            if weighted_links is None:
                for url in self.links:
                    weighted_link = WeightedLink(url, '',
                                                '',
                                                DEFAULT_LINK_WEIGHT,
                                                '')
                    self.weighted_links.append(weighted_link)
                    self.crawl_book.ws_writeln(WORKSHEET_PAGES_TO_CRAWL, weighted_link)

                self.crawl_book.wb_save()
            else:
                # append weighted_links
                pass
        
if __name__ == "__main__":
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    
    