# -*- coding: utf-8 -*-

u"""optimize

Check the .xlsx file for new seeds for example
Life Cycle: see main
"""

__usage__ = u"""Usage: python3 optimize.py [options]

Options:
  -h, --help              show this help
  -d                      show debugging information

Examples:
  python3 optimize.py
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/06/01 09:10:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os

from settings import SEEDS, WWW_DIR
from settings import WORKBOOK
from workbook import CrawlWorkbook 

class Optimize():
    """
    Optimize

    Rebuild the crawler status aka a Seed Workbook with for example new seeds
    """
    crawl_book = None
    
    url_base = ''

    # weighted links to crawl
    weighted_links = None
    # weighted links crawled
    weighted_links_done = []
    # weighted    
    ignore_seeds = []
    # weighted    
    ignored_pages = []
        
    def __init__(self, url=next(iter(SEEDS)), path=WWW_DIR):
        self.crawl_book = CrawlWorkbook(path=WWW_DIR, url=url)
        self.crawl_book.wb_open()

        # retrieve weighted_links, weighted_links_done...
        self.weighted_links = self.crawl_book.weighted_links        
        self.weighted_links_done = self.crawl_book.weighted_links_done       
        self.ignore_seeds =  self.crawl_book.ignore_seeds
        self.ignored_pages =  self.crawl_book.ignored_pages

    def rewrite_check_seeds(self)
        """
        Rewrite the crawlbook depending on seeds
        """
        pass
        
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

#    if len(argv)<2:
#        print("Arguments error")
#        print(__usage__)
#        sys.exit(2)
    
    # Get the list of all files and directories 
    # in the root directory
    opti = Optimize()
        
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
    