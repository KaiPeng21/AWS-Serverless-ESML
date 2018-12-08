# from config import AWS_DEFAULT_REGION
# from client_elasticsearch import get_es_client, TextfileModel
# import pytest
# import json
# import time

# @pytest.fixture
# def es_client():
#     es = get_es_client()
#     return es

# @pytest.fixture
# def textfile_model(request, es_client):
#     textfile_model = TextfileModel()

#     textfile_model.put_index(es_client)
#     textfile_model.put_mapping(es_client)

#     def cleanup():
#         textfile_model.delete_index(es_client)

#     request.addfinalizer(cleanup)
#     return textfile_model

# @pytest.fixture
# def textfile_inputs():
#     return [
#         {
#             "title" : "test1",
#             "extension" : "pdf", 
#             "s3_tuple" : ("bucketname", "test1.pdf", 3000000), 
#             "content" : "This is a dummy test.\nI am testing using pytest. Search dummy \ntest to find this document.\n Assume this pdf file is 3 MB large.",
#             "entities" : [],
#             "key_phrases" : []
#         },
#         {
#             "title" : "test2",
#             "extension" : "txt", 
#             "s3_tuple" : ("bucketname", "test2.txt", 4000000), 
#             "content" : "This is a second dummy test.\nI am testing using pytest. Search dummy \ntest to find this document.\n Assume this pdf file is 4 MB large.",
#             "entities" : [],
#             "key_phrases" : []
#         },
#         {
#             "title" : "test3",
#             "extension" : "pdf", 
#             "s3_tuple" : ("bucketname", "test1.docx", 2000000), 
#             "content" : "The Amazon.com website started as an online bookstore and later diversified to sell video downloads/streaming, MP3 downloads/streaming, audiobook downloads/streaming, software, video games, electronics, apparel, furniture, food, toys, and jewelry. The company also owns a publishing arm, Amazon Publishing, a film and television studio, Amazon Studios, produces consumer electronics lines including Kindle e-readers, Fire tablets, Fire TV, and Echo devices, and is the world's largest provider of cloud infrastructure services (IaaS and PaaS) through its AWS subsidiary.[7] Amazon also sells certain low-end products under its in-house brand AmazonBasics.",
#             "entities" : [],
#             "key_phrases" : []
#         },
#         {
#             "title" : "test4",
#             "extension" : "pdf", 
#             "s3_tuple" : ("bucketname", "pdf/test4.pdf", 3000000), 
#             "content" : "ECE477 is an embedded systems senior design course for students in the Purdue School of Electrical and Computer Engineering. \n\n\n\t\tThe course centers around providing students with practical, real-world experience with embedded hardware, to help simulate what students will encounter in a professional setting. To do this, students form teams of 4 to propose an embedded systems project and develop said project.\n\n\n\n\n Over the course of the semester, students will be exposed to all aspects of the design phase including documentation, requirements definition, parts selection, embedded software design and creation, hardware prototyping, printed circuit board layout, and physical prototype construction.",
#             "entities" : [],
#             "key_phrases" : []
#         },
#         {
#             "title" : "test5",
#             "extension" : "txt", 
#             "s3_tuple" : ("bucketname", "docx/test5.docx", 1000000), 
#             "content" : "This is a second dummy test.\nI am testing using pytest. Search dummy \ntest to find this document.\n Assume this pdf file is 4 MB large.",
#             "entities" : [],
#             "key_phrases" : []
#         }
#     ]

# @pytest.fixture
# def textfile_document_list(textfile_inputs):
#     return [
#         {
#             "title" : textfile["title"],
#             "extension" : textfile["extension"],
#             "filesize" : textfile["s3_tuple"][2],
#             "s3_url" : f"http://s3-{AWS_DEFAULT_REGION}.amazonaws.com/{textfile['s3_tuple'][0]}/{textfile['s3_tuple'][1]}",
#             "content" : textfile["content"],
#             "entities" : textfile["entities"],
#             "key_phrases" : textfile["key_phrases"]
#         }
#         for textfile in textfile_inputs
#     ]

# def test_textfile_model_formulate_doc(logger, textfile_model, textfile_inputs, textfile_document_list):
#     expected_document_list = textfile_document_list
#     document_list = [
#         textfile_model.formulate_doc(textfile_input["title"], textfile_input["extension"], textfile_input["s3_tuple"], textfile_input["content"], textfile_input["entities"], textfile_input["key_phrases"])
#         for textfile_input in textfile_inputs
#     ]
#     for expected_document, document in zip(expected_document_list, document_list):
#         assert json.dumps(expected_document) == json.dumps(document)

# def test_textfile_model_put_document(logger, es_client, textfile_model, textfile_inputs):
#     for textfile_input in textfile_inputs:
#         document = textfile_model.formulate_doc(textfile_input["title"], textfile_input["extension"], textfile_input["s3_tuple"], textfile_input["content"], textfile_input["entities"], textfile_input["key_phrases"])
#         textfile_model.put_document(es_client, textfile_input["s3_tuple"], document)

#         result = textfile_model.get_document(es_client, textfile_input["s3_tuple"])["_source"]
#         assert json.dumps(document) == json.dumps(result)

# def test_textfile_model_search_document(logger, es_client, textfile_model, textfile_inputs):
#     for textfile_input in textfile_inputs:
#         document = textfile_model.formulate_doc(textfile_input["title"], textfile_input["extension"], textfile_input["s3_tuple"], textfile_input["content"], textfile_input["entities"], textfile_input["key_phrases"])
#         textfile_model.put_document(es_client, textfile_input["s3_tuple"], document)

#     # Wait for Eventual Consistency
#     time.sleep(1)
#     result = textfile_model.search_document(es_client, body={
#         "query" : {
#             "match_all" : {}
#         }
#     })
#     assert len(textfile_inputs) == result["hits"]["total"]

# def test_textfile_model_search_document_by_keywords(logger, es_client, textfile_model, textfile_inputs):
#     for textfile_input in textfile_inputs:
#         document = textfile_model.formulate_doc(textfile_input["title"], textfile_input["extension"], textfile_input["s3_tuple"], textfile_input["content"], textfile_input["entities"], textfile_input["key_phrases"])
#         textfile_model.put_document(es_client, textfile_input["s3_tuple"], document)

#     # Wait for Eventual Consistency
#     time.sleep(1)
#     result = textfile_model.search_document_by_keywords(es_client, ["dummy", "pytest"])
#     assert 3 >= len(result["hits"]["hits"])
#     assert 3 == len(result["hits"]["hits"][0]["highlight"]["content"])

# def test_textfile_model_put_document_bulk(logger, es_client, textfile_model, textfile_inputs):
#     document_list = [textfile_model.formulate_doc(textfile_input["title"], textfile_input["extension"], textfile_input["s3_tuple"], textfile_input["content"], textfile_input["entities"], textfile_input["key_phrases"])
#         for textfile_input in textfile_inputs
#     ]
#     s3_tuple_list = [textfile_input["s3_tuple"] for textfile_input in textfile_inputs]
#     textfile_model.put_document_bulk(es_client, document_list, s3_tuple_list)

#     # Wait for Eventual Consistency
#     time.sleep(1)
#     result = textfile_model.search_document(es_client, body={
#         "query" : {
#             "match_all" : {}
#         }
#     })
#     assert len(textfile_inputs) == result["hits"]["total"]
    
    
