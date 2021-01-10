# -*- coding: utf-8 -*-

u"""optimize

Check the .xlsx file
Parse again downloaded wwww/html/www.nytimes3xbfgragh.onion/*.html files
Life Cycle: see main
"""

__usage__ = u"""Usage: python3 optimize.py [options] [url]

Options:
  -u ..., --url=...       Website URL to crawl
  -h, --help              show this help
  -p, --path              www path where files were stored eg. /var/www
  -d                      show debugging information

Examples:
  python3 optimize.py --url='https://www.nytimes3xbfgragh.onion/' --path='/var/www'
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/06/01 09:10:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os

from settings import WORKBOOK
from workbook import CrawlWorkbook 

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
    
    # Get the list of all files and directories 
    # in the root directory
    cw = CrawlWorkbook(path, url)
    cw.wb_open() 
    
    print(len(os.listdir(cw.html_pages_path)), 'files in Html Pages path:', cw.html_pages_path)
    # print the list 
    # print( os.listdir(cw.html_pages_path)) 
    
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
    