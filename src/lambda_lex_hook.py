from client_comprehend import detect_keyphrases_batch


def lambda_handler(event : dict, context : dict) -> dict:
    """[summary]
    
    Arguments:
        event {dict} -- [description]
        context {dict} -- [description]
    
    Returns:
        dict -- [description]
    """

    print(f"lex-hook-event: {event}")

    response = { 
        "statusCode" : 200,
        "body" : "testing lambda"
    }
    return response

if __name__=="__main__":
    lambda_handler({}, {})