# -*- coding: utf-8 -*-

u"""Search Engine

Search Engine handled by a Manticore Database
Life Cycle: see main
"""

__usage__ = u"""Usage: python3 search.py

Examples:
  python3 search.py
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/10/01 09:30:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

import os

# database
import pymysql.cursors

# crc32
from zlib import crc32

# 🗲  sha256  🗲 
from hashlib import sha256
#from hashlib import sha1

from settings import DATABASES

from settings import WORKBOOK
from workbook import CrawlWorkbook 

class SearchEngine():
    """Search Engine

    Search Engine handled by a Manticore Database
    Life Cycle: see main
    """

    # Manticore Database pymysql connection
    connection = None 

    db_host = ''
    db_user = '',
    db_password = '',
    db_port = 9306,
    db_cursorclass = pymysql.cursors.DictCursor

    def __init__(self):
        self.db_host = DATABASES['manticore']['HOST']
        self.db_user = DATABASES['manticore']['USER']
        self.db_password = DATABASES['manticore']['PASSWORD']
        self.db_port = DATABASES['manticore']['PORT']

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
                self.connection.commit()

        except Exception as e:
            print(e.__doc__)
            print(e.message)   

    @staticmethod  
    def hash_url(url=u'https://www.apple.onion'):
        """
        Return an unique ID Hash from Url 
        """
        url_hash = sha256(url.encode()).digest()
        id = crc32(url_hash)
        return(id)
        

    def db_replace_into(self, title, url, body):
        """
        Replace Web Page into Database

        !!! Storing the html body might be enough, not the full html sent by crawler         
        """
        if title is None:
            title = u''
        if url is None:
            url = u''
        if body is None:
            body = u''

        id = SearchEngine.hash_url(url)
        title = pymysql.escape_string(title)
        url = pymysql.escape_string(url)
        body = pymysql.escape_string(body)
        
        try:
            with self.connection.cursor() as cursor:
                sql = f'REPLACE INTO rt (id,title,url,body) VALUES({id},\'{title}\',\'{url}\',\'{body}\')'
                #print(f'Web Page: ' + sql[:400] + u'...')
                cursor.execute(sql)
                self.connection.commit()
                #print(u'DB Commit')
                
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
        #print(u'DB Commit')
      
    def db_close(self):
        """
        Close DB connection
        """
        self.connection.close()
        print(u'DB Close connection')


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
    
    se = SearchEngine()
    se.db_connect()

    title = u'test title'
    url = u'https://testurl.onion/test/test01.html'
    body = u"""<!DOCTYPE html>
                <html>
                    <head>
                        <title>test title</title>
                    </head>
                    <body>
                        <p>Hello test</p>
                        <p>"test", 'test', https://toto.com/</p>
                    </body>
                </html>
            """
    se.db_replace_into(title=title, url=url, body=body)

    se.db_close()

if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])
    