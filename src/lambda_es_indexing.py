"""
A lambda function that detects S3 put event and index information into elasticsearch
"""
import logging
from fileprocess import get_binary_data_from_file_in_s3, get_file_text_from_binary_data
from client_elasticsearch import get_es_client, TextfileModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

es_client = get_es_client()
supported_textfile_types = set(['docx', 'pdf', 'txt'])
supported_imagefile_types = set(['jpg', 'jpeg', 'png', 'bmp', 'gif'])

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
        # get file extensions
        extension_list = [s3_key.split('.')[-1] for s3_bucket, s3_key, s3_size in textfile_s3_tuple_list]
        # get binary data from file
        binary_data_list = [get_binary_data_from_file_in_s3(bucket=s3_bucket, key=s3_key) for s3_bucket, s3_key, s3_size in textfile_s3_tuple_list]
        # extract text from binary data
        text_list = [get_file_text_from_binary_data(extension, binary_data) for extension, binary_data in zip(extension_list, binary_data_list)]
        
        # create textfile and put mapping if necessary
        textfile_model = TextfileModel()
        textfile_model.put_index(es_client)
        textfile_model.put_mapping(es_client)

        # add document to elasticsearch
        doc_list = [textfile_model.formulate_doc(
            title="",
            extension=s3_tuple[1].split('.')[-1],
            s3_tuple=s3_tuple,
            content=text
        ) for text, s3_tuple in zip(text_list, textfile_s3_tuple_list)]
        textfile_model.put_document_bulk(es_client, doc_list, textfile_s3_tuple_list)

    # TODO: Imagefile

    # TODO: Format HTTP Response
    return {}

def lambda_handler(event : dict, context : dict) -> dict:
    """ Process files uploaded onto s3 bucket and index the content into elasticsearch given SQS events

    Arguments:
        event {dict} -- dictionary of lambda events
        context {dict} -- dictionary of lambda context

    Returns:
        dict -- dictionary of http response
    """

    s3_tuple_list = list(map(lambda x : (x["body"]["Records"][0]["s3"]["bucket"]["name"], \
                                         x["body"]["Records"][0]["s3"]["object"]["key"], \
                                         x["body"]["Records"][0]["s3"]["object"]["size"]), \
                                         event["Records"]))

    print(f"testing - {event}")
    return dispatcher(s3_tuple_list=s3_tuple_list)

if __name__ == "__main__":
    
    import json
    import os

    testfiles_filepath = os.path.dirname(os.path.abspath(__file__))
    with open(testfiles_filepath + "/sqs_event.json") as f:
        put_event = json.loads(f.read())
    
    lambda_handler(put_event,{})