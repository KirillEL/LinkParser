import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from db_service import DBService
import re


class LinkParser:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()

    def get_links(self, url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                if not re.search(r'\d', full_url):
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        links.append(full_url)
            return links
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

    def crawl(self, url):
        if url in self.visited:
            return
        self.visited.add(url)

        with DBService('crawler.db') as db:
            db.execute('INSERT OR IGNORE INTO URLList (URL) VALUES (?)', (url,))
            db.commit()

            db.execute('SELECT rowId FROM URLList WHERE URL = ?', (url,))
            from_url_id = db.fetchone()[0]

        links = self.get_links(url)

        for link in links:
            if link not in self.visited:
                with DBService('crawler.db') as db:
                    db.execute('INSERT OR IGNORE INTO URLList (URL) VALUES (?)', (link,))
                    db.commit()

                    db.execute('SELECT rowId FROM URLList WHERE URL = ?', (link,))
                    to_url_id = db.fetchone()[0]

                    db.execute('INSERT INTO linkBetweenURL (fk_FromURL_Id, fk_ToURL_Id) VALUES (?, ?)',
                               (from_url_id, to_url_id))
                    db.commit()

                self.crawl(link)
