# Simple crawler compatible with socks5h proxy

- Crawls https://www.nytimes3xbfgragh.onion/.
- The search UI will be available at http://localhost:8082.
- A /your_folder_path/html/www.nytimes3xbfgragh.onion.xlsx file is created with analyzed URLs and URLS yet to retrieve (in the defined folder below - /your_folder_path)
- id.html pages are saved in */your_folder_path/html/www.nytimes3xbfgragh.onion/ (their ids are displayed on search UI results pages)
- The website to crawl and the crawler to use are configured in demos/crawler/python/Dockerfile

Start the Search UI, the tor socks proxy and the web crawler:
```
  git clone https://github.com/M0t13y/demos.git demos
  cd demos/crawler
  docker-compose up -d
  cd python
  docker build -t nyto_crawler .
  docker run -v /your_folder_path:/var/www --network host -it --rm --name crawl-nytonion nyto_crawler
```

How to stop the crawler:
```
  ctrl+c
```

How to restart the crawler:
```
  docker run -v /your_folder_path:/var/www --network host -it --rm --name crawl-nytonion nyto_crawler
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

# Notes/To do:
- WIP weight/Priority urls supported, not in full effect
- Auto resume if file .xlsx is present
- Use Dockerfile instead of image for tor-socks-proxy
- Proper git instead of fork
- Check for DNS Leaks / Add Pihole or a DNS mirror
- Code cleanup, variable checks
- Refactor as needed for specific crawling
- Python tests
- Documentation with sphinx for example
- crc32 replaced by crc32(sha256(url))
- Tor v3 urls

# Tested on:
- Debian

# Alternatives:
- Rewrite wget using socks5
- Crawling using socks5 could be done by using curl instead of wget.
eg: curl --socks5 127.0.0.1:9050 https://www.nytimes3xbfgragh.onion/
- Rewrite scrapy to support socks5h
- Use Frontera as crawler frontier (cf. Frontera Request example)
