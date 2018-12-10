"""
A lambda function that detects S3 put event and index information into elasticsearch
"""
from decoder import deserialize_to_dict
from fileprocess import get_binary_data_from_file_in_s3, get_file_text_from_binary_data
from esclient import TextfileDocument, ImagefileDocument
from client_rekognition import detect_labels, detect_text, recognize_celebrities

from config import ES_HOST, ES_PORT, AWS_DEFAULT_REGION
from http import HTTPStatus

supported_textfile_types = set(['pdf', 'txt'])
supported_imagefile_types = set(['jpg', 'jpeg', 'png', 'bmp', 'gif'])

es_tx = TextfileDocument(host=ES_HOST, port=ES_PORT, aws_region=AWS_DEFAULT_REGION)
es_im = ImagefileDocument(host=ES_HOST, port=ES_PORT, aws_region=AWS_DEFAULT_REGION)

def dispatcher(s3_tuple_list : list) -> dict:
    """ Dispatch the lambda handler
    
    Arguments:
        s3_tuple_list {list} -- list of tuples of in the form (s3_bucket_name, s3_key_name, s3_object_size)
    
    Returns:
        dict -- dictionary of http response
    """

    # filter out non-supporting textfile types
    textfile_s3_tuple_list = list(filter(lambda x: x[1].split('.')[-1] in supported_textfile_types, s3_tuple_list))
    num_of_textfiles = len(textfile_s3_tuple_list)

    if num_of_textfiles > 0:

        # get file extensions, binary data, and text in file
        # TODO: replace this with Amazon Textract
        extension_list = [s3_key.split('.')[-1] for s3_bucket, s3_key, s3_size in textfile_s3_tuple_list]
        binary_data_list = [get_binary_data_from_file_in_s3(bucket=s3_bucket, key=s3_key) for s3_bucket, s3_key, s3_size in textfile_s3_tuple_list]
        text_list = [get_file_text_from_binary_data(extension, binary_data) for extension, binary_data in zip(extension_list, binary_data_list)]
        
        # create and put textfile document
        es_tx.put_index()
        es_tx.put_mapping()
        pid_list = [es_tx.create_pid(s3_tuple=s3_tuple) for s3_tuple in textfile_s3_tuple_list]
        doc_list = [es_tx.create_doc_entry(
            title=s3_tuple[1],
            extension=extension,
            s3_tuple=s3_tuple,
            content=text_data
        ) for extension, s3_tuple, text_data in zip(extension_list, textfile_s3_tuple_list, text_list)]
        es_tx.put_document_bulk(pid_list=pid_list, document_list=doc_list)

    imagefile_s3_tuple_list = list(filter(lambda x: x[1].split('.')[-1] in supported_imagefile_types, s3_tuple_list))
    num_of_imagefiles = len(imagefile_s3_tuple_list)

    if num_of_imagefiles > 0:

        extension_list = [s3_key.split('.')[-1] for s3_bucket, s3_key, s3_size in imagefile_s3_tuple_list]
        es_im.put_index()
        es_im.put_mapping()
        pid_list = [es_im.create_pid(s3_tuple=s3_tuple) for s3_tuple in imagefile_s3_tuple_list]
        doc_list = [es_im.create_doc_entry(
            extension=extension,
            s3_tuple=s3_tuple,
            image_labels=detect_labels(s3_tuple),
            image_texts=detect_text(s3_tuple),
            celebrities=recognize_celebrities(s3_tuple)
        ) for extension, s3_tuple in zip(extension_list, imagefile_s3_tuple_list)]
        es_im.put_document_bulk(pid_list=pid_list, document_list=doc_list)

    # TODO: Handle Delete file requests

    return { 
        "statusCode" : HTTPStatus.OK,
        "body" : "Putting documents into elasticsearch successfully."
    }

def lambda_handler(event : dict, context : dict) -> dict:
    """ Process files uploaded onto s3 bucket and index the content into elasticsearch given SQS events

    Arguments:
        event {dict} -- dictionary of lambda events
        context {dict} -- dictionary of lambda context

    Returns:
        dict -- dictionary of http response
    """

    event = deserialize_to_dict(event)

    print(f"testing - {event}")

    s3_tuple_list = list(map(lambda x : (x["body"]["Records"][0]["s3"]["bucket"]["name"], \
                                         x["body"]["Records"][0]["s3"]["object"]["key"], \
                                         x["body"]["Records"][0]["s3"]["object"]["size"]), \
                                         event["Records"]))

    try:
        return dispatcher(s3_tuple_list=s3_tuple_list)
    except:
        return { 
            "statusCode" : HTTPStatus.INTERNAL_SERVER_ERROR,
            "body" : "Putting documents into elasticsearch FAILED."
        }

if __name__ == "__main__":
    
    import json
    import os

    testfiles_filepath = os.path.dirname(os.path.abspath(__file__))
    with open(testfiles_filepath + "/private-sqs_event.json") as f:
        put_event = json.loads(f.read())
    
    lambda_handler(put_event,{})