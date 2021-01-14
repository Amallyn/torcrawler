# Crawler compatible with socks5h proxy

- Crawls https://www.nytimes3xbfgragh.onion/.
- The search UI will be available at http://localhost:8082.
- A /your_folder_path/html/www.nytimes3xbfgragh.onion.xlsx file is created with analyzed URLs and URLS yet to retrieve (in the defined folder below - /your_folder_path)
- id.html pages are saved in /your_folder_path/html/www.nytimes3xbfgragh.onion/ (their ids are displayed on search UI results pages)
- The website to crawl and the crawler to use are configured in python/Dockerfile and python/settings.py

Start the Search UI, the tor socks proxy and the web crawler:
```
  git clone https://github.com/M0t13y/torcrawler.git torcrawler
  cd torcrawler
  docker-compose up -d
  cd python
  docker build -t nytcrawler .
  docker run -v /your_folder_path:/var/www --network host -it --rm --name crawl-nytonion nytcrawler
```

How to stop the crawler:
```
  ctrl+c
```

How to restart the crawler:
```
  docker run -v /your_folder_path:/var/www --network host -it --rm --name crawl-nytonion nytcrawler
```


How to stop the search UI and the tor socks proxy:
```
  docker-compose down
```

Development stack:
  - docker-compose
  - docker
  - manticore
  - python
  -   requests
  -   beautifulsoup
  -   pymysql

# Life cycle

**Complete rewrite in progress**
- Crawler - FrontierManager in progress
- We'll see for Middleware and backend
- No Frontera integration for now

Most classes and files are documented. Life cycles can also be found in each class __doc__, __usage__ and main()

Classes & files
- python/settings.py
  - [x] All settings like www path and website url to crawl are defined here
  - [x] Add proxies settings
  - [x] Life cycle: see main()
- WeightedLink
  - [x] url, its weight/priority, date and notes
  - [x] link.py
  - [x] Life cycle: see main()
- CrawlWorkbook
  - [x] Excel .xlsx file handling the CrawlFrontier progress
  - [x] workbook.py
  - [x] Life cycle: see main()
- SearchEngine
  - [x] Search Engine handled by a Manticore Database
  - [x] search.py
  - [x] Life cycle: see main()
- CrawlFrontier
  - [ ] Optimize with boost c++ lib 
  - [x] frontier.py
  - [ ] Life cycle: see main()
- Crawler
  - [x] crawler.py
  - [x] Repair auto resume, likely in frontier 
  - [ ] Optimize with boost c++ lib 
  - [ ] Life cycle: see main()
- NytPage(WebPage)
  - [x] New York Times Crawler
  - [x] nytcrawler.py
  - [ ] Refactor/include in Frontier or later in Middleware or Backend
  - [ ] Life cycle: see main()
- NytCrawler(GenericCrawler)
  - [x] nytcrawler.py
  - [ ] Refactor/include in Frontier or later in Middleware or Backend
  - [ ] Life cycle: see main()
- optimize.py
  - [ ] optimize results
  - [ ] Check the .xlsx file
  - [ ] Parse again downloaded wwww/html/www.nytimes3xbfgragh.onion/*.html files
  - [ ] Life cycle: see main()

# Notes
- Auto resume if file .xlsx is present
- crc32 replaced by crc32(sha256(url))

# To do
- Lifecycle graph documentation
- Use boost C++ library optimization
- [x] Ignore lists
- [ ] regexp to Ignore pages
- weight/Priority urls supported, not in full effect
- Use Dockerfile from https://github.com/dperson/torproxy
- Auto change IP inspired by https://github.com/FrackingAnalysis/PyTorStemPrivoxy
- Check for DNS Leaks / Add Pihole or a DNS mirror
- Code cleanup, variable checks
- Refactor as needed for specific crawling
- Python tests
- Documentation
- Tor v3 urls

# Tested on:
- Debian

# Alternatives:
- Rewrite wget using socks5
- Crawling using socks5 could be done by using curl instead of wget.
eg: curl --socks5 127.0.0.1:9050 https://www.nytimes3xbfgragh.onion/
- Rewrite scrapy to support socks5h
- Use Frontera as crawler frontier (cf. Frontera Request example)
