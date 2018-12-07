import pytest
import time

from esclient import TextfileDocument

@pytest.fixture
def textfile_document(request):
    textfile_document = TextfileDocument(host="https://search-test-k4lwj4dbdk6y5c3uto7o6umrg4.us-east-1.es.amazonaws.com", port=443)
    textfile_document.delete_index()
    textfile_document.put_index()
    textfile_document.put_mapping()

    def clean_up():
        textfile_document.delete_index()

    request.addfinalizer(clean_up)  
    return textfile_document

@pytest.fixture
def s3_tuple_list():
    return [
        ("bucket", "key", 1024),
        ("bucket", "key2", 1028)
    ]

@pytest.fixture
def example_textfile_data_list(s3_tuple_list):
    data_list = [
        {
            "title" : "test title",
            "extension" : "pdf",
            "s3_tuple" : s3_tuple_list[0],
            "content" : "this is a pdf document"
        },
        {
            "title" : "test title 2",
            "extension" : "docx",
            "s3_tuple" : s3_tuple_list[1],
            "content" : "this is a docx file"
        }
    ]
    return data_list

def test_create_document(textfile_document, s3_tuple_list, example_textfile_data_list):
    tx = textfile_document
    for s3_tuple, example_textfile in zip(s3_tuple_list, example_textfile_data_list):
        pid = tx.create_pid(s3_tuple)
        document = tx.create_doc_entry(**example_textfile)
        response = tx.put_document(pid, document)

        response = tx.get_document(pid)
        assert example_textfile["title"] == response.json()["_source"]["title"]
        assert example_textfile["content"] == response.json()["_source"]["content"]
    
    # Wait for eventual consistency
    time.sleep(1)

    response = tx.query_all()
    assert len(example_textfile_data_list) == response.json()["hits"]["total"]

def test_create_document_bulk(textfile_document, s3_tuple_list, example_textfile_data_list):
    tx = textfile_document

    pid_list = [tx.create_pid(s3_tuple) for s3_tuple in s3_tuple_list]
    document_list = [tx.create_doc_entry(**example_textfile) for example_textfile in example_textfile_data_list]

    response = tx.put_document_bulk(pid_list, document_list)

    # Wait for eventual consistency
    time.sleep(1)

    response = tx.query_all()
    assert len(example_textfile_data_list) == response.json()["hits"]["total"]
    
    