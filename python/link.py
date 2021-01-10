# -*- coding: utf-8 -*-

u"""Weighted Link Class

Weighted Link
"""

__author__ = u"M0t13y"
__version__ = u"$Revision: 0.01 $"
__date__ = u"$Date: 2021/08/01 08:30:00 $"
__copyright__ = u"Copyright [" + __author__ + "]"
__license__ = u"Licensed under the Apache License, Version 2.0"

from datetime import datetime
from dataclasses import dataclass

@dataclass
class WeightedLink():
    """Weighted Link
    
    Life Cycle: see main
    """
    url: str
    title: str
    date: datetime
    weight: int
    notes: str

    def __unicode__(self):
        return url
         
if __name__ == "__main__":
    print("\n" + __doc__ + "\n" + __copyright__ + "\n" + __license__ +"\n" )

    spread_date = '2021-01-08'
    parsed_date = datetime.strptime(spread_date, "%Y-%m-%d")
    link = WeightedLink('https://apple.com/', 'Apple - iMe', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 12, 'Oui oui')

    print(link)
    print(link.url)
    print(link.date)
    date = datetime.strptime('2021-01-08 09:26:59', '%Y-%m-%d %H:%M:%S')
    print(date)
