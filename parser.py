import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from db_service import DBService
import re


class LinkParser:
    def __init__(self, base_url, max_depth=2):
        self.base_url = base_url
        self.visited = set()
        self.max_depth = max_depth

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

    def get_words(self, url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ')
            words = re.findall(r'\b\w+\b', text)
            return words
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

    def store_words(self, words, url_id):
        word_ids = {}
        with DBService('crawler.db') as db:
            for word in set(words):
                db.execute('INSERT OR IGNORE INTO wordList (word, isFiltered) VALUES (?, ?)', (word, 0))
                db.execute('SELECT rowId FROM wordList WHERE word = ?', (word,))
                word_id = db.fetchone()[0]
                word_ids[word] = word_id

                db.execute('INSERT INTO wordLocation (fk_wordId, fk_URLId, location) VALUES (?, ?, ?)',
                           (word_id, url_id, words.index(word)))
            db.commit()
        return word_ids

    def monitoring(self):
        with DBService('crawler.db') as db:
            db.execute('SELECT COUNT(*) FROM URLList')
            url_count = db.fetchone()[0]

            db.execute('SELECT COUNT(*) FROM linkBetweenURL')
            link_count = db.fetchone()[0]
            print("Total URLs: {}, Total Links: {}".format(url_count, link_count))

    def crawl(self, url, depth=0):
        if depth >= self.max_depth:
            return
        if url in self.visited:
            return
        self.visited.add(url)
        self.monitoring()

        with DBService('crawler.db') as db:
            db.execute('INSERT OR IGNORE INTO URLList (URL) VALUES (?)', (url,))
            db.commit()
            db.execute('SELECT rowId FROM URLList WHERE URL = ?', (url,))
            url_id = db.fetchone()[0]

        links = self.get_links(url)
        words = self.get_words(url)
        word_ids = self.store_words(words, url_id)

        for link in links:
            if link not in self.visited:
                with DBService('crawler.db') as db:
                    db.execute('INSERT OR IGNORE INTO URLList (URL) VALUES (?)', (link,))
                    db.commit()
                    db.execute('SELECT rowId FROM URLList WHERE URL = ?', (link,))
                    link_id = db.fetchone()[0]

                    db.execute('INSERT INTO linkBetweenURL (fk_FromURL_Id, fk_ToURL_Id) VALUES (?, ?)',
                               (url_id, link_id))
                    db.commit()

                    for word, word_id in word_ids.items():
                        db.execute('INSERT INTO linkWord (fk_wordId, fk_linkId) VALUES (?, ?)',
                                   (word_id, link_id))
                    db.commit()

                return self.crawl(link, depth + 1)
