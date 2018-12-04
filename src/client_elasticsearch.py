"""
A module that interfaces with Elasticsearch
"""
from config import ES_HOST, ES_PORT, ES_INDEX, AWS_DEFAULT_REGION, ES_BATCH_SIZE

import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import ElasticsearchException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_es_client() -> Elasticsearch:
    """ Retrieve the elasticsearch instance
    
    Returns:
        Elasticsearch -- elasticsearch instance
    """
    return Elasticsearch([{"host" : ES_HOST, "port" : ES_PORT}])

class TextfileModel:

    def __init__(self):
        self._index = ES_INDEX
        self._doc_type = self.__class__.__name__.lower()
        self._mapping = {
            "properties" : {
                "title" : {
                    "type" : "text"
                },
                "extension" : {
                    "type" : "keyword"
                },
                "s3_url" : {
                    "type" : "text"
                },
                "filesize" : {
                    "type" : "integer"
                },
                "content" : {
                    "type" : "text"
                },
                "entities" : {
                    "properties" : {
                        "type" : {
                            "type" : "keyword"
                        },
                        "content" : {
                            "type" : "keyword"
                        }
                    }
                },
                "keyphrases" : {
                    "type" : "keyword"
                }
            }
        }

    @property
    def index(self) -> str:
        """ index getter

        Returns:
            str -- elasticsearch index
        """
        return self._index

    @property
    def doc_type(self) -> str:
        """ doc_type getter
        
        Returns:
            str -- elasticsearch doc_type
        """
        return self._doc_type

    @property
    def mapping(self) -> dict:
        """ mapping getter

        Returns:
            dict -- elasticsearch mapping
        """
        return self._mapping

    def _get_id(self, s3_tuple : tuple) -> str:
        """ get the document id from s3 bucket
        
        Arguments:
            s3_tuple {tuple} -- tuple of (s3_bucket_name, s3_object_key, s3_object_size)
        
        Returns:
            [type] -- [description]
        """
        return "--".join(s3_tuple[:2]).replace("/", "-")

    def formulate_doc(self, title : str, extension : str, s3_tuple : tuple, content : str, entities : list = [], key_phrases : list = []) -> dict:
        """ formulate the textfile document

        Arguments:
            title {str} -- file title
            extension {str} -- file extension
            s3_tuple {tuple} -- tuple of (s3_bucket_name, s3_object_key, s3_object_size)
            content {str} -- file content
        
        Keyword Arguments:
            entities {list} -- entities detected by comprehend (default: {[]})
            key_phrases {list} -- key phrases detected by comprehend (default: {[]})
        
        Returns:
            dict -- dictionary of textfile document
        """
        return {
            "title" : title,
            "extension" : extension,
            "filesize" : s3_tuple[2],
            "s3_url" : f"https://s3-{AWS_DEFAULT_REGION}.amazonaws.com/{s3_tuple[0]}/{s3_tuple[1]}",
            "content" : content,
            "entities" : entities,
            "key_phrases" : key_phrases
        }

    def put_index(self, es : Elasticsearch):
        """ Create es index. Ignore HTTP 400 (Index already exist response).
        
        Arguments:
            es {Elasticsearch} -- elasticsearch client
        """
        es.indices.create(index=self._index, ignore=400)

    def delete_index(self, es : Elasticsearch):
        """ Remove es index. Ignore HTTP 400 and 404 (Index not found response).
        
        Arguments:
            es {Elasticsearch} -- elasticsearch client
        """
        es.indices.delete(index=self._index, ignore=[400, 404])

    def put_mapping(self, es : Elasticsearch):
        """ Create elasticsearch mapping
        
        Arguments:
            es {Elasticsearch} -- elasticsearch client
        """
        es.indices.put_mapping(index=self._index, doc_type=self._doc_type, body=self._mapping)

    def put_document(self, es : Elasticsearch, s3_tuple : tuple, document : dict):
        """ Add document
        
        Arguments:
            es {Elasticsearch} -- elasticsearch client
            s3_tuple {tuple} -- tuple of (s3_bucket_name, s3_object_key, s3_object_size)
            document {dict} -- document to be added
        """
        uid = self._get_id(s3_tuple)
        es.create(index=self._index, doc_type=self._doc_type, id=uid, body=document)

    def put_document_bulk(self, es : Elasticsearch, document_list : list, s3_tuple_list : list):
        """ Put documents into elasticsearch
        
        Arguments:
            es {Elasticsearch} -- elasticsearch client
            document_list {list} -- list of document dictionary to be added
            s3_tuple_list {list} -- list of (s3_bucket_name, s3_object_key, s3_file_size)
        """
        bulk_data_list = []
        total_size = 0
        for document, s3_tuple in zip(document_list, s3_tuple_list):
            bulk_data_list.append({
                "_index" : self._index,
                "_type" : self._doc_type,
                "_id" : self._get_id(s3_tuple),
                "_source" : document
            })
            total_size += document["filesize"]
            if total_size >= ES_BATCH_SIZE:
                success, _ = bulk(es, bulk_data_list)
                bulk_data_list = []
                total_size = 0
        if len(bulk_data_list) > 0:
            success, _ = bulk(es, bulk_data_list)

    def delete_document(self, es : Elasticsearch, s3_tuple : tuple):
        """[summary]
        
        Arguments:
            es {Elasticsearch} -- [description]
            s3_tuple {tuple} -- [description]
        """
        uid = self._get_id(s3_tuple)
        es.delete(index=self._index, doc_type=self._doc_type, id=uid)

    def get_document(self, es : Elasticsearch, s3_tuple : tuple):
        """[summary]
        
        Arguments:
            es {Elasticsearch} -- [description]
            s3_tuple {tuple} -- [description]
        """
        uid = self._get_id(s3_tuple)
        return es.get(index=self._index, doc_type=self._doc_type, id=uid)

    def search_document(self, es: Elasticsearch, body : dict) -> dict:
        """ Search document
        
        Arguments:
            es {Elasticsearch} -- elasticsearch client
            body {dict} -- search body dictionary
        
        Returns:
            dict -- dictionary of the searched result
        """
        return es.search(index=self._index, doc_type=self._doc_type, body=body)
        
    def search_document_by_keywords(self, es : Elasticsearch, keywords : list, doc_max_size : int = 3, highlight_fragment_size : int = 3, highlight_fragment_length : int = 50) -> dict:
        """[summary]
        
        Arguments:
            es {Elasticsearch} -- elasticsearch instance
            keywords {list} -- list of search keywords
        
        Keyword Arguments:
            doc_max_size {int} -- number of searched document (default: {3})
            highlight_fragment_size {int} -- number of highlight fragments (default: {3})
            highlight_fragment_length {int} -- length of a highlight fragment (default: {50})
        
        Returns:
            dict -- dictionary of result in the format
            {
                "..." : ...,
                "hits": {
                    "total": n,
                    "max_scoxre": x.xxxxxxx,
                    "hits": [
                        {
                            "_index" : "...",
                            "_type" : "...",
                            "_id" : "...",
                            "_score" : x.xxxxxxx,
                            "_source" : {...mapping...},
                            "highlight" : { 
                                "content" : [...]
                            }
                        },
                    ]
                }
            }
        """
        
        return es.search(index=self._index, doc_type=self._doc_type, body={
            "from" : 0,
            "size" : doc_max_size,
            "query": {
                "multi_match" : {
                    "query" : " ".join(keywords), 
                    "fields": [ "content", "title" ] 
                }
            },
            "highlight" : {
                "number_of_fragments" : highlight_fragment_size,
                "fragment_size" : highlight_fragment_length,
                "fields" : {
                    "content" : {}
                }
            }
        })
