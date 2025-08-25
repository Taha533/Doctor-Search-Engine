import scrapy
from urllib.parse import urljoin

class SiteSpider(scrapy.Spider):
    # name = "site_spider"
    # allowed_domains = ["doctorbangladesh.com"]   # Replace with target domain
    # start_urls = ["https://www.doctorbangladesh.com/"]


    name = "site_spider"
    allowed_domains = ["doctorbangladesh.com"]
    start_urls = ["https://www.doctorbangladesh.com/"]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False  # disable robots.txt if it blocks everything
    }

    # custom_settings = {
    # 'DEFAULT_REQUEST_HEADERS': {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'Referer': 'https://www.google.com/'
    #     }
    # }


    def parse(self, response):
        # Save or process page content
        page_url = response.url
        page_title = response.css("title::text").get()
        page_text = " ".join(response.css("::text").getall()).strip()

        yield {
            'url': page_url,
            'title': page_title,
            'content': page_text
        }

        # Extract and follow all internal links
        for href in response.css("a::attr(href)").getall():
            url = urljoin(response.url, href)
            if self.allowed_domains[0] in url:
                yield response.follow(url, self.parse)
