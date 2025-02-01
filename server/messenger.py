import json
import consts

def build_message(header: str, message_dict: dict) -> str:
    response_dict = {
        "header": header,
        "sender": consts.SENDER_NAME,

        "body": message_dict        
    }

    response_string = json.dumps(response_dict)
    return response_string