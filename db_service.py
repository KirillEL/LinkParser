import sqlite3 as sql


class DBService:
    def __init__(self, file: str):
        self.file = file

    def __enter__(self):
        self.conn = sql.connect(self.file)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Error occurred: {exc_val}")
        self.conn.close()

    def execute(self, sql_request: str, params=None):
        if params is None:
            params = ()
        try:
            self.cursor.execute(sql_request, params)
        except sql.Error as e:
            print(f"Error executing query: {e}")
            return None

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def commit(self):
        self.conn.commit()
