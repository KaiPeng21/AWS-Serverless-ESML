import requests
from http import HTTPStatus
import json

class ESClientBase:

    def __init__(self, host : str, port : int, index : str, doc_type : str, mapping : dict):
        self._host = host
        self._port = port
        self._es_endpoint = f"{host}:{port}"
        self._index = index
        self._doc_type = doc_type
        self._mapping = mapping

        if self._es_endpoint[:4] != "http":
            if self._port == 443:
                self._es_endpoint = f"https://{self._es_endpoint}" 
            else:
                self._es_endpoint = f"http://{self._es_endpoint}"

    @property
    def index(self):
        return self._index
    
    @property
    def doc_type(self):
        return self._doc_type

    @property
    def mapping(self):
        return self._mapping

    def put_index(self, ignore_exist_error=True) -> requests.Response:
        """ Add an elasticsearch index by sending a put request
        
        Keyword Arguments:
            ignore_exist_error {bool} -- ignore index exist error (default: {True})
        
        Returns:
            requests.Response -- put index http response
        """

        res = requests.put(url=f"{self._es_endpoint}/{self._index}")
        if ignore_exist_error:
            assert res.status_code in [HTTPStatus.OK, HTTPStatus.BAD_REQUEST]
        else:
            assert HTTPStatus.OK == res.status_code
        return res
    
    def delete_index(self, ignore_nonexist_error=True) -> requests.Response:
        """ Delete an elasticsearch index by sending a delete request
        
        Keyword Arguments:
            ignore_nonexist_error {bool} -- ignore index not found error (default: {True})
        
        Returns:
            requests.Response -- delete index http response
        """

        res = requests.delete(url=f"{self._es_endpoint}/{self._index}")
        if ignore_nonexist_error:
            assert res.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        else:
            assert HTTPStatus.OK == res.status_code
        return res

    def put_mapping(self) -> requests.Response:
        """ Add an elasticsearch mapping by sending a put request
        
        Returns:
            requests.Response -- put mapping http response
        """

        res = requests.put(url=f"{self._es_endpoint}/{self._index}/_mapping/{self._doc_type}", json=self._mapping)
        assert HTTPStatus.OK == res.status_code
        return res

    def get_document(self, pid : str) -> requests.Response:
        """ Retrieve document by sending a get request
        
        Arguments:
            pid {str} -- primary id
        
        Returns:
            requests.Response -- get document http response
        """

        res = requests.get(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/{pid}")
        assert HTTPStatus.OK == res.status_code
        return res

    def put_document(self, pid : str, document : dict) -> requests.Response:
        """ Add document by sending a put request
        
        Arguments:
            pid {str} -- primary id
            document {dict} -- document
        
        Returns:
            requests.Response -- put document http response
        """

        res = requests.put(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/{pid}", json=document)
        assert HTTPStatus.CREATED == res.status_code
        return res

    def put_document_bulk(self, pid_list : list, document_list : list) -> requests.Response:
        """ Put multiple documents using batching
        
        Arguments:
            pid_list {list} -- list of primary ids
            document_list {list} -- list of documents
        
        Returns:
            requests.Response -- put request http response
        """

        assert len(pid_list) == len(document_list)
        data_list = [
            "\n".join([
                json.dumps({ "create" : {"_id" : pid, "_type" : self._doc_type, "_index" : self._index} }),
                json.dumps(document)
            ]) for pid, document in zip(pid_list, document_list)
        ]
        data = "\n".join(data_list) + "\n"
        headers = {"Content-Type": "application/x-ndjson"}
        res = requests.post(url=f"{self._es_endpoint}/_bulk?pretty", data=data, headers=headers)
        assert HTTPStatus.OK == res.status_code
        return res

    def delete_document(self, pid : str, ignore_nonexist_error=True) -> requests.Response:
        """ Delete document by sending a delete request
        
        Arguments:
            pid {str} -- Primary id
        
        Keyword Arguments:
            ignore_nonexist_error {bool} -- ignore document not found error (default: {True})
        
        Returns:
            requests.Response -- delete request http response
        """

        res = requests.delete(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/{pid}")
        if ignore_nonexist_error:
            assert res.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]
        else:
            assert HTTPStatus.OK == res.status_code
        return res

    def delete_document_bulk(self, pid_list : list) -> requests.Response:
        """ Delete multiple documents using batching
        
        Arguments:
            pid_list {list} -- list of primary ids
        
        Returns:
            requests.Response -- post request http response
        """
        # TODO: Need Unittest to Verify If Functionalities are achieved

        data_list = [
            json.dumps({ "delete" : {"_id" : pid, "_type" : self._doc_type, "_index" : self._index} })
            for pid in pid_list
        ]
        data = "\n".join(data_list) + "\n"
        headers = {"Content-Type": "application/x-ndjson"}
        res = requests.post(url=f"{self._es_endpoint}/_bulk?pretty", data=data, headers=headers)
        assert HTTPStatus.OK == res.status_code
        return res

    
    def delete_document_by_query(self, body : dict) -> requests.Response:
        """ Delete queried document
        
        Arguments:
            body {dict} -- query body
        
        Returns:
            requests.Response -- http response
        """

        res = self.search_document(body=body)
        data = res.json()
        if data["hits"]["total"] > 0:
            pid_list = [document["_id"] for document in data["hits"]["hits"]]
            return self.delete_document_bulk(pid_list=pid_list)
        return res

    def search_document(self, body : dict) -> requests.Response:
        """ Search document in elasticsearch
        
        Arguments:
            body {dict} -- query body
        
        Returns:
            requests.Response -- search document http response
        """

        res = requests.get(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/_search", json=body)
        return res
    
    def query_all(self) -> requests.Response:
        """ Select all elements in the index
        
        Returns:
            requests.Response -- search document http response
        """

        query_param = {
            "query" : {
                "match_all" : {}
            }
        }
        res = requests.get(url=f"{self._es_endpoint}/{self._index}/{self._doc_type}/_search", json=query_param)
        assert HTTPStatus.OK == res.status_code
        return res

class TextfileDocument(ESClientBase):

    def __init__(self, host : str = "http://localhost", port : int = 9200, aws_region : str = "us-east-1"):
        
        self.aws_region = aws_region

        index = "textfilesearch"
        doc_type = "textfile"
        mapping = {
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
                }
            }
        }
        return super().__init__(host, port, index, doc_type, mapping)

    def create_pid(self, s3_tuple : tuple) -> str:
        """ Get primary id from s3 bucket and object name
        
        Arguments:
            s3_tuple {tuple} -- tuple of (s3 bucket, object key, object size)
        
        Returns:
            str -- primary id
        """

        return "-".join(s3_tuple[:2])

    def create_doc_entry(self, title : str, extension : str, s3_tuple : tuple, content : str) -> dict:
        """ Create document entry
        
        Arguments:
            title {str} -- file title
            extension {str} -- file extension
            s3_tuple {tuple} -- tuple of (s3 bucket, object key, object size)
            content {str} -- document body
        
        Returns:
            dict -- textfile document
        """
        return {
            "title" : title,
            "extension" : extension,
            "filesize" : s3_tuple[2],
            "s3_url" : f"https://s3.amazonaws.com/{s3_tuple[0]}/{s3_tuple[1]}",
            "content" : content
        }
    
    def search_and_highlight_document(self, keywords : list, num_of_docs : int = 3, num_of_highlights : int = 3, highlight_fragment_size : int = 100) -> dict:
        """ Search document by keywords and returns searched highlights
        
        Arguments:
            keywords {list} -- list of strings to be searched
        
        Keyword Arguments:
            num_of_docs {int} -- max number of searched document (default: {3})
            num_of_highlights {int} -- number of highlight fragments (default: {3})
            highlight_fragment_size {int} -- chars display per highlight fragment (default: {100})
        
        Returns:
            dict -- textfile document in the form of 
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
                                "content" : [xxx , xxx , xxx]
                            }
                        },
                    ]
                }
            }
        """

        body = {
            "from" : 0,
            "size" : num_of_docs,
            "query" : {
                "multi_match" : {
                    "query" : " ".join(keywords),
                    "fields" : ["content", "title"]
                }
            },
            "highlight" : {
                "number_of_fragments" : num_of_highlights,
                "fragment_size" : highlight_fragment_size,
                "fields" : {
                    "content" : {}
                }
            }
        }

        print(f"search and highlight using body: {body}")
        res = self.search_document(body=body)
        return res

class ImagefileDocument(ESClientBase):

    def __init__(self, host : str = "http://localhost", port : int = 9200, aws_region : str = "us-east-1"):
        self.aws_region = aws_region

        index = "imagefilesearch"
        doc_type = "imagefile"
        mapping = {
            "properties" : {
                "extension" : {
                    "type" : "keyword"
                },
                "s3_url" : {
                    "type" : "text"
                },
                "filesize" : {
                    "type" : "integer"
                },
                "tags" : {
                    "type" : "text"
                }
            }
        }
        return super().__init__(host, port, index, doc_type, mapping)

    def create_pid(self, s3_tuple : tuple) -> str:
        """ Get primary id from s3 bucket and object name
        
        Arguments:
            s3_tuple {tuple} -- tuple of (s3 bucket, object key, object size)
        
        Returns:
            str -- primary id
        """

        return "-".join(s3_tuple[:2])

    def create_doc_entry(self, extension : str, s3_tuple : tuple, image_labels : list, image_texts : list, celebrities : list) -> dict:
        """ Create document entry
        
        Arguments:
            extension {str} -- file extension
            s3_tuple {tuple} -- tuple of (s3 bucket, object key, object size)
            image_labels {list} -- list of image labels
            image_texts {list} -- list of image texts
            celebrities {list} -- list of celebrities in image
        
        Returns:
            dict -- document entry
        """
        tags = image_labels
        tags[0:0] = image_texts
        tags[0:0] = celebrities

        return {
            "extension" : extension,
            "filesize" : s3_tuple[2],
            "s3_url" : f"https://s3.amazonaws.com/{s3_tuple[0]}/{s3_tuple[1]}",
            "tags" : tags
        }

    def search_document_by_tags(self, tag_list : list, num_of_docs : int = 3) -> dict:
        """ Search document by image tags (labels, text, celebrities)
        
        Arguments:
            tag_list {list} -- list of tags
        
        Keyword Arguments:
            num_of_docs {int} -- max number of searched document (default: {3})
        
        Returns:
            dict -- imagefile document in the form of
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
                            "_source" : {...mapping...}
                        },
                    ]
                }
            }
        """

        res = self.search_document(body={
            "from" : 0,
            "size" : num_of_docs,
            "query" : {
                "bool" : {
                    "should" : [
                        {
                            "match": {
                                "tags": tag
                            }
                        }
                        for tag in tag_list
                    ]
                }
            }
        })
        return res

if __name__ == "__main__":
    tx = TextfileDocument()
    tx.put_index()
    tx.put_mapping()
    im = ImagefileDocument()
    im.put_index()
    im.put_mapping()
    
    pid_list = range(3)
    document_list = [
        tx.create_doc_entry(
            title="test_pdf.pdf",
            extension="pdf",
            s3_tuple=("bucket", "test_pdf.pdf", 1024),
            content="This is a dummy PDF"
        ),
        tx.create_doc_entry(
            title="amazon.pdf",
            extension="pdf",
            s3_tuple=("bucket", "amazon.pdf", 2048),
            content="Amazon.com, Inc. is located in Seattle, WA and was founded July 5th, 1994 by Jeff Bezos, allowing customers to buy everything from books to blenders. Seattle is north of Portland and south of Vancouver, BC. Other notable Seattle - based companies are Starbucks and Boeing."
        ),
        tx.create_doc_entry(
            title="test_hello.pdf",
            extension="pdf",
            s3_tuple=("bucket", "test_hello.pdf", 100),
            content="Hello world"
        )
    ]
    tx.put_document_bulk([1, 2, 3], document_list)


