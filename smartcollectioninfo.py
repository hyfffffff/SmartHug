import sqlite3
from datetime import datetime

class SmartCollectionInfo:
    def __init__(self):
        self.db_path = "SmartbaseInfo/jellycollectioninfo.db"
        # self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                CREATE TABLE IF NOT EXISTS collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    milvus_host TEXT NOT NULL,
                    milvus_port INTEGER NOT NULL,
                    encoder TEXT NOT NULL,
                    answerer TEXT NOT NULL
                )
            '''
            conn.execute(query)
            # conn.commit()
            # conn.close()


    def insert_record(self, name, milvus_host, milvus_port, encoder, answerer):
        # Check if the record already exists with all the parameters
        if not self.record_exists(name, milvus_host, milvus_port, encoder, answerer):
            query = '''
            INSERT INTO collections (name, milvus_host, milvus_port, encoder, answerer)
            VALUES (?, ?, ?, ?, ?)
            '''
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(query, (name, milvus_host, milvus_port, encoder, answerer))
                # conn.commit()
                # conn.close()

    def record_exists(self, name, milvus_host, milvus_port, encoder, answerer):
        query = '''
        SELECT id FROM collections WHERE name = ? AND milvus_host = ? AND milvus_port = ? AND encoder = ? AND answerer = ?
        '''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, (name, milvus_host, milvus_port, encoder, answerer))
            records = cursor.fetchone()
            # conn.close()
        return records is not None
        

    def fetch_records(self):
        query = 'SELECT * FROM collections'
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query)
            records = cursor.fetchall()
            # conn.close()
        return records

    def delete_record(self, name, milvus_host, milvus_port, encoder, answerer):
        query = 'DELETE FROM collections WHERE name = ?, ?, ?, ?, ?'
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, (name, milvus_host, milvus_port, encoder, answerer))
            # conn.commit()
            # conn.close()

    def close(self):
        pass

# Example usage
if __name__ == "__main__":
    db = SmartCollectionInfo()
    db.insert_record("example_collection", "localhost", 19530, "MyEncoder", "MyAnswerer")
    records = db.fetch_records()
    print("Records before deletion:", records)
    
    db.delete_record("example_collection")
    records_after_deletion = db.fetch_records()
    print("Records after deletion:", records_after_deletion)
    
    db.close()
