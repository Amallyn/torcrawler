# -*- coding: utf-8 -*-

u"""Backend

Inspired by Frontera Backend
"""

__usage__ = u"""TODO - Usage: python3 backend.py [options] [url]

Options:
  -h, --help              show this help
  -d                      show debugging information

Examples:
  python3 backend.py
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/14/01 06:15:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

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
    except Usage as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    import sys
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )
    main(sys.argv[1:])

