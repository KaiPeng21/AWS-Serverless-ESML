

import logging
from client_comprehend import detect_keyphrases_batch
from client_elasticsearch import get_es_client, TextfileModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

es_client = get_es_client()

def lambda_handler(event : dict, context : dict) -> dict:
    """[summary]
    
    Arguments:
        event {dict} -- [description]
        context {dict} -- [description]
    
    Returns:
        dict -- [description]
    """

    textfile_model = TextfileModel()
    result = textfile_model.search_document_by_keywords(es_client, ["dummy", "test"])

    print(result)

    response = { 
        "statusCode" : 200,
        "body" : "testing lambda"
    }
    return response

if __name__=="__main__":
    lambda_handler({}, {})