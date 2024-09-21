from create_tables import create_tables
from parser import LinkParser


class Program:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def start(self):
        create_tables()
        parser = LinkParser(
            base_url=self.base_url
        )
        parser.crawl(self.base_url)


if __name__ == '__main__':
    base_url = input("Enter the URL: ")
    program = Program(
        base_url=base_url
    )
    program.start()
