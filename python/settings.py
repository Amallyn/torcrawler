# -*- coding: utf-8 -*-

u"""settings

Project settings
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/10/01 09:30:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os

# Websites to crawl
SEEDS = {'https://www.nytimes3xbfgragh.onion/'}
 
# paths
#   Workbook is stored in HTML_DIR
#     eg. /var/www/html/www.apple.com.xlsx
#   Download pages are stored in HTML_DIR/url.netloc
#     eg. /var/www/html/www.apple.com/id.html

PROXIES = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150')

WWW_DIR = u'/var/www'
HTML_SUBDIR = u'html'

# html path eg. /var/www/html
#   workbooks and downloaded pages path
HTML_DIR = os.path.join(WWW_DIR, HTML_SUBDIR)

MAX_N_REQUESTS = 10

DATABASES = {
    'manticore': {
        'ENGINE': 'mysql',
        'NAME': 'mydatabase',
        #'USER': 'mydatabaseuser',
        #'PASSWORD': 'mypassword',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 9306,
    } # end manticore
} # end DATABASES

WORKBOOK = {
    # workbook file extension: .xlsx
    'FILE_EXT': u'.xlsx',
    'crawler': {
        # worksheet names and index
        'worksheet': {
            'crawledpages': {
                'TITLE': u'Crawled pages',
                'INDEX': 0
            }, # end crawled pages
            'tocrawlpages': {
                'TITLE': u'Pages to crawl',
                'INDEX': 1
            }, # end to crawl pages
            'ignoreseeds': {
                'TITLE': u'Ignore seeds',
                'INDEX': 2
            }, # end ignore seeds
            'ignoredpages': {
                'TITLE': u'Ignored pages',
                'INDEX': 3
            }, # end ignore pages

            'weightedlink': {
                # WeightedLink fields columns in a Worksheet 
                'URL_COL': 1,
                'TITLE_COL': 2,
                'DATE_COL': 3,
                'WEIGHT_COL': 4,
                'NOTES_COL': 5,
                # Starting row for weighted links values
                'STARTING_ROW': 4,
            } # end weightedlink
        } # end worksheet
    } # end crawler
} # end workbook

DEFAULT_WEIGHT = 0.1

        
def main(argv=None):
    """
    main
    """
    print(HTML_DIR)
    print(DATABASES['manticore']['NAME'])
    print(WORKBOOK['FILE_EXT'])
    print(WORKBOOK['crawler']['worksheet']['ignoredpages']['TITLE'])
    print(WORKBOOK['crawler']['worksheet']['ignoredpages']['INDEX'])
    print(WORKBOOK['crawler']['worksheet']['weightedlink']['WEIGHT_COL'])
    
if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
    