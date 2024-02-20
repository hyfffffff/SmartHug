"""
PDFInfoDB manages records of articles within a knowledge base, with each
article represented by a record. It emphasizes tracking article information
like file name, chunk count, chunk size, and overlap for sentence vector
encoding in the knowledge base.
"""

import sqlite3
from datetime import datetime
import pandas as pd

class PDFInfoDB:
    def __init__(self, db_path):
        self.db_path = "SmartbaseInfo/" + db_path
        # self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                CREATE TABLE IF NOT EXISTS jellypdf_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    chunks_count INTEGER,
                    chunksize INTEGER,
                    chunkoverlap INTEGER,
                    split_time TEXT,
                    success BOOLEAN
                )
            '''
            conn.execute(query)

    def insert_record(self, file_name, chunks_count, chunksize, chunkoverlap, success):
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                INSERT INTO jellypdf_info (file_name, chunks_count, chunksize, chunkoverlap, split_time, success)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            conn.execute(query, (file_name, chunks_count, chunksize, chunkoverlap, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), success))

    def delete_record(self, file_name):
        with sqlite3.connect(self.db_path) as conn:
            query = 'DELETE FROM jellypdf_info WHERE file_name = ?'
            conn.execute(query, (file_name,))

    def fetch_records(self):
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT * FROM jellypdf_info order by split_time desc'
            cursor = conn.execute(query)
            records = cursor.fetchall()
            
        return records
    
    def fetch_dataframe(self):
        records = self.fetch_records()

        columns = ['id', 'file_name', 'chunks_count', 'chunksize', 'chunkoverlap', 'split_time', 'success']
        dataframe = pd.DataFrame(records, columns=columns)
    
        return dataframe
