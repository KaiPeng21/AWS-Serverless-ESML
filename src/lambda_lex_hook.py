from client_lex import LexResponse
from client_comprehend import detect_keyphrases
from esclient import TextfileDocument, ImagefileDocument

from config import ES_HOST, ES_PORT, AWS_DEFAULT_REGION
from difflib import SequenceMatcher
import json

def validate_slots(slots : dict) -> dict:
    """ Validate slots
    
    Arguments:
        slots {dict} -- slots dictionary to be validate
    
    Returns:
        dict -- validated version
    """

    slots["ESMLFileTypes"] = to_validate_text(slots.get("ESMLFileTypes"), ["text", "image"])

    return slots

def to_validate_text(a : str, textlist : list) -> str:
    """ Convert text to validate format
    
    Arguments:
        a {str} -- text to validate
        textlist {list} -- list of valid text
    
    Returns:
        str -- valid text
    """

    if a is None:
        return None
    for text in textlist:
        if is_similar(a, text):
            return text
    return None

def is_similar(a : str, b : str, threshold : float = 0.5) -> bool:
    """ Check if two strings are similar enough
    
    Arguments:
        a {str} -- first string
        b {str} -- second string
        threshold {float} -- threshold score between 0 and 1
    
    Returns:
        bool -- is similar enough or not
    """
    if a is None or b is None:
        return False
    a = a.lower()
    b = b.lower()
    if a in b or b in a:
        return True
    return SequenceMatcher(a=a, b=b).ratio() > threshold

def get_textfile_search_message(description : str) -> list:
    """
    
    Arguments:
        description {str} -- [description]
    
    Returns:
        list -- list in the form
        [
            (filename {str}, highlight {str}, link URL {str}),
            ...
        ]
    """
    print(f"Starting textfilesearch using description {description}")

    keywords = detect_keyphrases(description)
    es_tx = TextfileDocument(host=ES_HOST, port=ES_PORT, aws_region=AWS_DEFAULT_REGION)
    response = es_tx.search_and_highlight_document(
        keywords=keywords,
        num_of_docs=3,
        num_of_highlights=1,
        highlight_fragment_size=50
    )
    return [
        (hit["_source"]["doc"]["title"],
        hit["highlight"]["content"][0],
        hit["_source"]["doc"]["s3_url"])
        for hit in response.json()["hits"]["hits"]
    ]

def not_found_response():
    # TODO: Move this to client_lex
    """ get resposne when search result is empty
    
    Returns:
        dict -- [description]
    """
    return LexResponse().response_close(
        success=True,
        message_content=f"Sorry, Nothing was found."
    )


def make_response(event : dict):

    invocation_source = event["invocationSource"]
    assert invocation_source == "DialogCodeHook"

    session_attributes = event["sessionAttributes"]
    bot_name = event["bot"]["name"]
    current_intent = event["currentIntent"]["name"]
    intent_slots = validate_slots(event["currentIntent"]["slots"])

    print(f"Processing bot {bot_name} intent {current_intent}...")
    
    lex_resp = LexResponse(
        session_attribute=session_attributes, 
        intent_name=current_intent, 
        slots=intent_slots
    )

    if intent_slots.get("ESMLFileTypes") is None:
        return lex_resp.response_elicit_slot(
            slot_to_elicit="ESMLFileTypes",
            message_content="What type of file are you looking for?",
            generic_attachments=[
                lex_resp.create_generic_attachment(
                    buttons=[
                        lex_resp.create_button("Text Document", "text"),
                        lex_resp.create_button("Image Document", "image")
                    ]
                )
            ]
        )
    
    if intent_slots.get("ESMLKeywords") is None:
        return lex_resp.response_elicit_slot(
            slot_to_elicit="ESMLKeywords",
            message_content="Can you give me a description about what you are looking for?"
        )
    
    filetype = intent_slots["ESMLFileTypes"]
    description = intent_slots["ESMLKeywords"]

    if filetype == "text":
        attachments = [
            lex_resp.create_generic_attachment(
                title=title,
                sub_title=highlight,
                attachment_link_url=s3_url
            )
            for (title, highlight, s3_url) in get_textfile_search_message(description=description)
        ]
        resp = lex_resp.response_close(
            success=True,
            message_content="",
            generic_attachments=attachments
        )

    else:
        # TODO: change this to bucket

        attachments = [lex_resp.create_generic_attachment(
            title="This is a Test Response",
            sub_title="image response",
            image_url="https://s3.amazonaws.com/example-bucket/test_jpeg.jpg" # TODO: change bucket name
        )]
        resp = lex_resp.response_close(
            success=True, 
            message_content=json.dumps(event),
            generic_attachments=attachments
        )
    
    return resp

def lambda_handler(event : dict, context : dict) -> dict:
    """[summary]
    
    Arguments:
        event {dict} -- [description]
        context {dict} -- [description]
    
    Returns:
        dict -- [description]
    """

    print(f"lex-hook-event: {event}")

    try:
        return make_response(event)
    except Exception as e:
        print(e)
        return LexResponse().response_close(
            success=False,
            message_content=f"Sorry! An error occur {e}"
        )

if __name__=="__main__":
    lambda_handler({}, {})