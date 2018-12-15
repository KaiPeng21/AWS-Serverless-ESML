"""
Example Lambda Function That Interfaces with Amazon Lex
"""

from client_lex import LexResponse, to_validate_text
import json

def validate_slots(slots : dict) -> dict:
    """ Validate slots

    Arguments:
        slots {dict} -- slots dictionary to be validate

    Returns:
        dict -- validated version
    """

    #slots["ESMLFileTypes"] = to_validate_text(slots.get("ESMLFileTypes"), ["text", "image"])

    return slots

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

    if intent_slots.get("ESMLExampleMeetingType") is None:
        return lex_resp.response_elicit_slot(
            slot_to_elicit="ESMLExampleMeetingType",
            message_content="What type of meeting do you want to schedule?",
            generic_attachments=[
                lex_resp.create_generic_attachment(
                    buttons=[
                        lex_resp.create_button("WebEx Conference", "WebEx"),
                        lex_resp.create_button("Book a Media Hub", "Room")
                    ]
                )
            ]
        )

    if intent_slots.get("ESMLExampleMeetingTime") is None:
        return lex_resp.response_elicit_slot(
            slot_to_elicit="ESMLExampleMeetingTime",
            message_content="When do you want to schedule your meeting?"
        )
    
    if intent_slots.get("ESMLExampleMeetingType") == "Room":
        if intent_slots.get("ESMLExampleMeetingRoom") is None:
            return lex_resp.response_elicit_slot(
                slot_to_elicit="ESMLExampleMeetingRoom",
                message_content="Which Room do you want to book?",
                generic_attachments=[
                    lex_resp.create_generic_attachment(
                        buttons=[
                            lex_resp.create_button("Conference 2A", "2a"),
                            lex_resp.create_button("Conference 2B", "2b"),
                            lex_resp.create_button("Conference 4A", "4a")
                        ]
                    )
                ]
            )

    return lex_resp.response_close(
        success=True,
        message_content=f"Your {intent_slots.get('ESMLExampleMeetingType')} has been booked on {intent_slots.get('ESMLExampleMeetingTime')}!"
    )
    

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