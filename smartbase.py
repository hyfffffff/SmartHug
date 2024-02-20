"""
SmartBase: Core component of the application, handling text data management 
and retrieval using Milvus vector database. It connects to Milvus, creates 
collections with schemas for text and embedding storage, processes PDFs into 
searchable chunks, and performs vectorized searches.

Features include:
- Connection setup to a Milvus database.
- Model management for text encoding and query answering.
- Collection creation/check in Milvus with text, page, file name, and embeddings.
- PDF text extraction, chunking, encoding, and storage in Milvus.
- Overwriting, deletion, and existence checks for collection data.
- Vectorized search within collections for query handling.
- Integration with an answer model for query responses.
- Utilities for listing records and data presentation in pandas DataFrame.

"""

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
# from sentence_transformers import SentenceTransformer
from smartgptmodel import SmartGptModel
from pdfsplitor import PDFSplitor
from pdfinfodb import PDFInfoDB
from smartcollectioninfo import SmartCollectionInfo
from pathlib import Path
import pandas as pd

class SmartBase:
    def __init__(self, milvus_host='127.0.0.1', milvus_port='19530', encodemodel=SmartGptModel(), answermodel=SmartGptModel(), collection_name="smartybase", embeddingdim=None):        # Connect to Milvus server
        connections.connect("default", host=milvus_host, port=milvus_port)

        # Initialize sentence transformer model for embeddings
        self.encodemodel = encodemodel
        self.answermodel = answermodel

        exists, dim = self.has_collection(collection_name)
        self.collection_name = collection_name

        if exists:
            self.embeddingdim = dim
        else:
            self.embeddingdim = self.encodemodel.dim
            self.create_collection()

      
        self.collection = Collection(self.collection_name)

        self.pdfinfodb = PDFInfoDB(self.collection_name+'.db')
        self.collectioninfo = SmartCollectionInfo()

        self.collectioninfo.insert_record(self.collection_name, milvus_host, milvus_port, self.encodemodel.name, self.answermodel.name)

    def setanswermodel(self, answermodel):
        self.answermodel = answermodel

    def getanswermodel(self):
        return self.answermodel
    
    def getencodemodel(self):
        return self.encodemodel

    def create_collection(self):
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
                FieldSchema(name="page", dtype=DataType.INT64),
                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=300),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embeddingdim)
            ]
            schema = CollectionSchema(fields, f"Text Collection {self.encodemodel.name}-{self.embeddingdim}")
            self.collection = Collection(self.collection_name, schema)

            index = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": self.embeddingdim},
            }

            self.collection.create_index("embedding", index)

    def delete_collection(self):
        if utility.has_collection(self.collection_name):
            Collection(self.collection_name).drop()


    def save(self, file_name, save_file_name=None, chunksize=200, chunkoverlap=0):
        # collection = Collection(self.collection_name)
        texts = []
        page_nums = []
        file_names = []
        embeddings = []

        if save_file_name == None:
            save_file_name =  Path(file_name).name.split('.')[0]
            # save_file_name = file_name.split('.')[0]

        if self.is_exists(save_file_name):
            print(f"File '{file_name}' already exists in the collection.")
            # Optionally delete the existing data
            # self.delete_pdf_data(pdf_name)
            # Or return to avoid re-inserting
            return 


        pdf = PDFSplitor(file_name)
        if pdf.valid:
            chunks = PDFSplitor(file_name).get_chunk(chunksize, chunkoverlap)
            if len(chunks)==0:
                return False
        
            for page_num, text in chunks:
                embedding = self.encodemodel.encode(text)
                texts.append(text)
                page_nums.append(page_num)
                file_names.append(save_file_name)
                embeddings.append(embedding)

            # Insert data into collection
            self.collection.insert([texts, page_nums, file_names, embeddings])

            self.collection.flush()

            self.pdfinfodb.insert_record(save_file_name, len(chunks), chunksize, chunkoverlap, True)

            return True
        else:
            return False


    def overwrite(self, file_name, save_file_name=None, chunksize=200, chunkoverlap=0):

        if save_file_name == None:
            save_file_name =  Path(file_name).name.split('.')[0]

        if self.is_exists(save_file_name):
            self.delete(save_file_name)
            self.pdfinfodb.delete_record(save_file_name)

        return self.save(file_name, save_file_name, chunksize, chunkoverlap)

    def delete(self, file_name):
        """Delete existing data for a given PDF from the collection."""
        # collection = Collection(self.collection_name)
        # Delete the existing data for the PDF
        self.collection.delete(f"file_name == '{file_name}'")
        self.collection.flush()

    def is_exists(self, file_name):
        """Check if a File with the given name already exists in the collection."""
        self.collection.load()
        # collection = Collection(self.collection_name)
        # search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        query_results = self.collection.query(f"file_name == '{file_name}'", output_fields=["file_name"])
        return len(query_results) > 0
    
    
    def search(self, query_text, file_name=None, top_n=5):
        
        query_embedding = self.encodemodel.encode(query_text)

        # Define the search parameters
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        # Construct the query
        if file_name:
            # Search within documents with the given file name
            search_expression = f"file_name == '{file_name}'"
        else:
            # Search across all documents
            search_expression = ""

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_n,
            expr=search_expression,
            output_fields=["text", "page", "file_name","id"]
        )

        return [(hit.entity.get("text"), hit.entity.get("page"), hit.entity.get("file_name")) for hit in results[0]]
    

    def has_collection(self, collection_name):

        if not utility.has_collection(collection_name):
            return False, 0
        

         # Connect to the Milvus server and retrieve the collection
        collection = Collection(collection_name)
    
        # Retrieve the schema of the collection
        schema = collection.schema

        # Iterate through the fields to find the 'embedding' field and get its dimension
        for field in schema.fields:
            if field.name == 'embedding' and field.dtype == DataType.FLOAT_VECTOR:
                return True, field.params['dim']

        # Return None if 'embedding' field is not found
        return True, 0
    
    def answer(self, question, file_name=None, top_n=5):
        text_group = self.search(question, file_name, top_n)
        return self.answermodel.answer(question, text_group), text_group
    
    def listbaserecords(self):
        return self.pdfinfodb.fetch_records()
    
    def listbasedataframe(self):
        return self.pdfinfodb.fetch_dataframe()



