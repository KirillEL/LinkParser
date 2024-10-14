import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from db_service import DBService
import re
import matplotlib.pyplot as plt
import networkx as nx


class LinkParser:
    def __init__(self, base_url, max_depth=15):
        self.base_url = base_url
        self.visited = set()
        self.max_depth = max_depth
        self.iteration = 0
        self.count_words = 0
        self.page_word_counts = []
        self.page_link_counts = []
        self.page_urls = []
        self.main_count_links = 0  # общее кол-во найденных ссылок

    @staticmethod
    def get_links(url):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(url, href)
                links.append(full_url)
            return links
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

    @staticmethod
    def get_words(url: str):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.content, 'html.parser')
            text: str = soup.get_text(separator=' ')
            words: list[str] = re.findall(r'\b\w+\b', text)
            filtered_words: list[str] = []
            for word in words:
                if word.isalpha() and len(word) > 1:
                    filtered_words.append(word.lower())

            return filtered_words
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []

    @staticmethod
    def store_words(words, url_id):
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
            self.iteration += 1
            with open('info.txt', 'a') as f:
                f.write("URL count: {}, link bw count: {}\n".format(url_count, link_count))
            # print("Total URLs: {}, Total Links: {}".format(url_count, link_count))

    def crawl(self, url: str, depth=0):
        if depth >= self.max_depth:
            return
        if url in self.visited:
            return

        self.visited.add(url)

        with DBService('crawler.db') as db:

            db.execute('INSERT OR IGNORE INTO URLList (URL) VALUES (?)', (url,))
            db.commit()
            db.execute('SELECT rowId FROM URLList WHERE URL = ?', (url,))
            url_id = db.fetchone()[0]

        links = self.get_links(url)
        words = self.get_words(url)
        self.main_count_links += len(links)
        self.page_link_counts.append(self.main_count_links)
        self.page_urls.append(url_id)

        with open('info.txt', 'a') as f:
            f.write("count words: {} count links: {}\n".format(len(words), len(links)))
        word_ids = self.store_words(words, url_id)
        with DBService('crawler.db') as db:
            db.execute('SELECT COUNT(*) FROM wordList')
            words = db.fetchone()[0]
            self.page_word_counts.append(words)

        for link in links:
            if link not in self.visited:
                with DBService('crawler.db') as db:
                    db.execute('INSERT OR IGNORE INTO URLList (URL) VALUES (?)', (link,))
                    db.execute('SELECT rowId FROM URLList WHERE URL = ?', (link,))
                    link_id = db.fetchone()[0]

                    db.execute('INSERT INTO linkBetweenURL (fk_FromURL_Id, fk_ToURL_Id) VALUES (?, ?)',
                               (url_id, link_id))

                    for word, word_id in word_ids.items():
                        db.execute('INSERT INTO linkWord (fk_wordId, fk_linkId) VALUES (?, ?)',
                                   (word_id, link_id))
                    db.commit()
                return self.crawl(link, depth + 1)

    def plot_results(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.page_urls, self.page_word_counts, marker='o', label='Word Count')
        plt.xlabel('Page Number')
        plt.ylabel('Word Count')
        plt.title('Word Count per Page')
        plt.legend()
        plt.show()

        plt.figure(figsize=(10, 5))
        plt.plot(self.page_urls, self.page_link_counts, marker='o', label='Link Count')
        plt.xlabel('Page Number')
        plt.ylabel('Link Count')
        plt.title('Link Count per Page')
        plt.legend()
        plt.show()

    def plot_link_graph(self):
        G = nx.DiGraph()

        with DBService('crawler.db') as db:
            db.execute('SELECT fk_FromURL_Id, fk_ToURL_Id FROM linkBetweenURL')
            links = db.fetchall()

            # Извлекаем URL для каждого ID
            for from_id, to_id in links:
                db.execute('SELECT URL FROM URLList WHERE rowId = ?', (from_id,))
                from_url = db.fetchone()[0]
                db.execute('SELECT URL FROM URLList WHERE rowId = ?', (to_id,))
                to_url = db.fetchone()[0]

                G.add_edge(from_url, to_url)

        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=8, font_weight='bold',
                arrows=True)
        plt.title("Link Graph between URLs")
        plt.show()
