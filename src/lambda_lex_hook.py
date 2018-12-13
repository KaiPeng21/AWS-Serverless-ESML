from client_lex import LexResponse, to_validate_text
from client_comprehend import detect_keyphrases
from esclient import TextfileDocument, ImagefileDocument

from config import ES_HOST, ES_PORT, AWS_DEFAULT_REGION

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

    keywords = description.split()
    if len(keywords) > 10:
        keywords = detect_keyphrases(description)
    print(f"Getting keywords {keywords}")
    es_tx = TextfileDocument(host=ES_HOST, port=ES_PORT, aws_region=AWS_DEFAULT_REGION)
    response = es_tx.search_and_highlight_document(
        keywords=keywords,
        num_of_docs=3,
        num_of_highlights=1,
        highlight_fragment_size=50
    )
    print(f"search_highlight_doc: {response.json()}")
    if len(response.json()["hits"]["hits"]) == 0:
        return []

    return [
        (hit["_source"]["title"],
        hit["highlight"]["content"][0],
        hit["_source"]["s3_url"])
        for hit in response.json()["hits"]["hits"]
    ]

def get_imagefile_search_message(description : str) -> list:
    """[summary]
    
    Arguments:
        description {str} -- [description]
    
    Returns:
        list -- list in the form
        [
            (tags, s3_url),
            ...
        ]
    """
    print(f"Starting imagefilesearch using description {description}")

    keywords = description.split()
    if len(keywords) > 10:
        keywords = detect_keyphrases(description)
    print(f"Getting keywords {keywords}")
    es_im = ImagefileDocument(host=ES_HOST, port=ES_PORT, aws_region=AWS_DEFAULT_REGION)
    response = es_im.search_document_by_tags(
        tag_list=keywords,
        num_of_docs=3
    )
    if len(response.json()["hits"]["hits"]) == 0:
        return []
    
    return [
        (hit["_source"]["tags"],
        hit["_source"]["s3_url"])
        for hit in response.json()["hits"]["hits"]
    ]


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
            message_content="Here are the search result!" if len(attachments) > 0 else "Sorry, I can't find a matching document.",
            generic_attachments=attachments
        )

    else:
        attachments = [
            lex_resp.create_generic_attachment(
                title="Here is an image with labels:",
                sub_title=", ".join(tag_list[:12])[:75] + "...",
                attachment_link_url=s3_url,
                image_url=s3_url
            )
            for (tag_list, s3_url) in get_imagefile_search_message(description=description)
        ]
        resp = lex_resp.response_close(
            success=True,
            message_content="Here are the search result!" if len(attachments) > 0 else "Sorry, I can't find a matching document.",
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