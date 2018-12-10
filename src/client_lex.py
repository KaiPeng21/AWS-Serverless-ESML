""" 
A module that interfaces with Amazon Lex
"""

class LexResponse:

    def __init__(self, session_attribute : dict = {}, intent_name : str = "", slots : dict = {}):
        self.session_attribute = session_attribute
        self.intent_name = intent_name
        self.slots = slots

        self._support_content_types = ["PlainText", "SSML", "CustomPayload"]

    def create_button(self, text : str, value : str) -> dict:
        """ Create a chatbot button
        
        Arguments:
            text {str} -- button text label
            value {str} -- value sent to server on button click
        
        Returns:
            dict -- dictionary of button
        """
        return {
            "text" : text,
            "value" : value
        }

    def create_generic_attachment(self, title : str = None, sub_title : str = None, image_url : str = None, attachment_link_url : str = None, buttons : list = None) -> dict:
        """ Create a generic attachment dictionary, an option rendered to the user when a prompt is shown.
        Can be an image, a button, or text.
        
        Keyword Arguments:
            title {str} -- attachment title (default: {None})
            sub_title {str} -- attachment subtitle (default: {None})
            image_url {str} -- image url (default: {None})
            attachment_link_url {str} -- link url (default: {None})
            buttons {list} -- list of buttons (default: {None})
        
        Returns:
            dict -- generic attachment dictionary
        """
        attachment = {}
        if title:
            attachment["title"] = title
        if sub_title:
            attachment["subTitle"] = sub_title
        if image_url:
            attachment["imageUrl"] = image_url
        if attachment_link_url:
            attachment["attachmentLinkUrl"] = attachment_link_url
        if buttons:
            attachment["buttons"] = buttons
        return attachment
    
    def make_options(self, buttons : list) -> dict:
        """ Create a list of bu
        
        Arguments:
            buttons {list} -- list of button dictionaries
        
        Returns:
            dict -- generic attachment dictionary
        """
        return self.create_generic_attachment(
            buttons=buttons
        )

    def response_close(self, success : bool, message_content : str, content_type : str = "PlainText", generic_attachments : list = None) -> dict:
        """ Informs Amazon Lex not to expect a response from the user.
        E.g. Your pizza order has been placed.
        
        Arguments:
            success {bool} -- Fulfilled or Failed
            message_content {str} -- Message to convey to the user

        Keyword Arguments:
            content_type {str} -- PlainText or SSML or CustomPayload (default: {"PlainText"})
            generic_attachments {list} -- Optional list of generic attachment dictionary (default: {None})
        
        Returns:
            dict -- response to lex
        """
        assert content_type in self._support_content_types
        response = {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "Close",
                "fulfillmentState" : "Fulfilled" if success else "Failed",
                "message" : {
                    "contentType" : content_type,
                    "content" : message_content
                }
            }
        }
        if generic_attachments:
            response["dialogAction"]["responseCard"] = {
                "version" : 1,
                "contentType" : "application/vnd.amazonaws.card.generic",
                "genericAttachments" : generic_attachments
            }
        return response

    # TODO: Finish this later when needed
    # 
    # def response_confirm_intent(self):
    #     pass
    
    # def response_delegate(self):
    #     pass

    # def response_elicit_intent(self):
    #     pass
    
    def response_elicit_slot(self, 
        slot_to_elicit : str,
        message_content : str, 
        content_type : str = "PlainText", 
        generic_attachments : list = None
        ) -> dict:
        """ Informs Amazon Lex that the user is expected to provide a slot value in the response.
        
        Arguments:
            slot_to_elicit {str} -- slot to elicit
            message_content {str} -- message
        
        Keyword Arguments:
            content_type {str} -- PlainText or SSML or CustomPayload (default: {"PlainText"})
            generic_attachments {list} -- Optional list of generic attachment dictionary (default: {None})
        
        Returns:
            dict -- response to lex
        """

        assert content_type in self._support_content_types
        assert slot_to_elicit in self.slots.keys()
        response = {
            "sessionAttributes" : self.session_attribute,
            "dialogAction" : {
                "type" : "ElicitSlot",
                "message" : {
                    "contentType" : content_type,
                    "content" : message_content
                },
                "intentName": self.intent_name,
                "slots": self.slots,
                "slotToElicit" : slot_to_elicit
            }
        }
        if generic_attachments:
            response["dialogAction"]["responseCard"] = {
                "version" : 1,
                "contentType" : "application/vnd.amazonaws.card.generic",
                "genericAttachments" : generic_attachments
            }
        return response
