from db_service import DBService


def create_tables():
    with DBService('crawler.db') as db:
        db.execute('''
                    CREATE TABLE IF NOT EXISTS wordList (
                        rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                        word TEXT NOT NULL,
                        isFiltered INTEGER
                    )
                ''')

        db.execute('''
                    CREATE TABLE IF NOT EXISTS URLList (
                        rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                        URL TEXT NOT NULL
                    )
                ''')

        db.execute('''
                    CREATE TABLE IF NOT EXISTS wordLocation (
                        rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                        fk_wordId INTEGER NOT NULL,
                        fk_URLId INTEGER NOT NULL,
                        location INTEGER,
                        FOREIGN KEY (fk_wordId) REFERENCES wordList(rowId),
                        FOREIGN KEY (fk_URLId) REFERENCES URLList(rowId)
                    )
                ''')

        db.execute('''
                    CREATE TABLE IF NOT EXISTS linkBetweenURL (
                        rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                        fk_FromURL_Id INTEGER NOT NULL,
                        fk_ToURL_Id INTEGER NOT NULL,
                        FOREIGN KEY (fk_FromURL_Id) REFERENCES URLList(rowId),
                        FOREIGN KEY (fk_ToURL_Id) REFERENCES URLList(rowId)
                    )
                ''')
        db.execute('''
                    CREATE TABLE IF NOT EXISTS linkWord (
                        rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                        fk_wordId INTEGER NOT NULL,
                        fk_linkId INTEGER NOT NULL,
                        FOREIGN KEY (fk_wordId) REFERENCES wordList(rowId),
                        FOREIGN KEY (fk_linkId) REFERENCES linkBetweenURL(rowId)
                    )
                ''')

        db.commit()
