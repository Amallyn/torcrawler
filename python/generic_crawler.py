# -*- coding: utf-8 -*-

u"""generic_crawler

Generic crawler for searching with a Manticore Database
compatible with socks5h proxies
"""

__usage__ = u"""Usage: python3 generic_crawler.py [options] [url]

Options:
  -u ..., --url=...       Website URL to crawl
  -h, --help              show this help
  -d                      show debugging information

Examples:
  python3 generic_crawler.py --url='https://www.nytimes3xbfgragh.onion/'
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

# database
import pymysql.cursors

# crc32
import zlib

# 🗲 sha256  🗲  :)
from hashlib import sha256
#from hashlib import sha1

# Our frontier
from crawl_frontier import CrawlFrontier

class WebPage():
    url = u''
    url_escaped = u''
    title = None
    title_escaped = None
    crc32 = 0
    url_hash = b''
    html_doc = u''
    html_doc_escaped = u''
    
    response = None
    soup = None
    links = {}
    links_href = {} 
    
    # path to save the html page
    save_dir = u'./'
    
    def __init__(self, url=u'', save_dir = u'./'):
        """
        init
        """
        self.url = url
        self.save_dir = save_dir

    def __unicode__(self):
        return self.title

    def get(self, session):
        """
        download and process web page
        
        session: requests.Session()
        """
        if session:
            print(u'Web Page: get', self.url)
            self.response = session.get(self.url)
            self.html_doc = self.response.text
            self.soup = BeautifulSoup(self.html_doc, 'html.parser')
            self.title = self.soup.find('title')
            if self.title is None:
                print(u"Web Page: Ignore page - Title: None")
            else:
                self.url_escaped = pymysql.escape_string(self.url)
                self.title = self.title.string
                self.title_escaped = pymysql.escape_string(self.title.string)
                #self.crc32 = zlib.crc32(self.url.encode('utf-8'))
                # bytes
                self.url_hash = sha256(self.url.encode()).digest()
                self.crc32 = zlib.crc32(self.url_hash)
                self.html_doc_escaped = pymysql.escape_string(self.html_doc)
                self.save_to_file()
                print(u'Web Page: ' + self.title_escaped)
        else:
            print(u'Web Page: Session error')

    def save_to_file(self):
        """
        save page to a #.html file where # is the title crc32
        """
        # eg. /var/www/html/apple.com/256.html
        file_name = os.path.join(self.save_dir, str(self.crc32) + '.html') 
        print(file_name)            
        f = open(file_name, 'w')
        f.write(self.soup.prettify())
        f.close()
        
    def db_replace_into(self, connection):
        """
        Replace Web Page into Database
        
        connection: Manticore Database pymysql connection
        """
        if self.title is None:
            print(u"Web Page: Ignore page - Title: None")
        else:
            try:
                with connection.cursor() as cursor:
                    sql = f'REPLACE INTO rt (id,title,url,body) VALUES({self.crc32},\'{self.title_escaped}\',\'{self.url_escaped}\',\'{self.html_doc_escaped}\')'
                    # print(f'Web Page: ' + sql[:200] + u'...')
                    cursor.execute(sql)
                connection.commit()
                print(u'DB Commit')
                
            except Exception as e:
                print(e.__doc__)
                print(e.message)   
                
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
            print(u'Web Page:',len(links_href_absolute_startswith), u'absolute links and',len(links_href_relative), u'relative links found')

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
    
    db_host = ''
    db_user = '',
    db_password = '',
    db_port = 9306,
    db_cursorclass = pymysql.cursors.DictCursor

    # Manticore Database pymysql connection
    connection = None 
    
    # Requests session for multiple url get
    session = None
    proxies = dict(http='socks5h://localhost:9150', https='socks5h://localhost:9150')

    # frontier
    frontier = None
        
    # Maximum number of urls to crawl per inner loop
    max_n_requests = 10 

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
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port

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
              
    def db_connect(self):
        """
        Connect to the database

        Create table if not exists
        Commit the changes
        """
        self.connection = pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_password,
                                     port=self.db_port, cursorclass=self.db_cursorclass)

        try:
            with self.connection.cursor() as cursor:
                # creating a table "rt" if it doesn't exist with the following settings:
                # - html_strip='1': stripping HTML is on
                # - html_remove_elements='style,script,a': for HTML tags <style>/<script>/<a> we don't need their contents, so we are stripping them completely
                # - morphology='stem_en': we'll use English stemmer as a morphology processor
                # - index_sp='1': we'll also index sentences and paragraphs for more advanced full-text search capabilities and better relevance
                sql = "CREATE TABLE IF NOT EXISTS rt(title text, body text, url text stored) html_strip='1' html_remove_elements='style,script,a' morphology='stem_en' index_sp='1'"
                # print(sql)
                cursor.execute(sql)

        except Exception as e:
            print(e.__doc__)
            print(e.message)   

    def db_commit(self):
        """
        DB commit

        Connection is not autocommit by default. So you must commit to save
        your changes.
        """      
        self.connection.commit()
        print(u'DB Commit')
      
    def db_close(self):
        """
        Close DB connection
        """
        self.connection.close()
        print(u'DB Close connection')
      
    def crawl(self):
        """
        crawl website from url
        
        stores web pages in a manticore DB
        """

        self.db_connect()
        self.db_commit()

        self.session_start()

        # crawl from one ase url / site root
        seeds = [ self.site_url ]
        self.frontier = CrawlFrontier(seeds)

        while True:
            next_urls = self.frontier.get_next_urls()
            if not next_urls:
                break
            for url in next_urls:
                    try:
                        web_page = WebPage(url, self.frontier.seed_dir)
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
    
    crawler = GenericCrawler(url = url,
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
