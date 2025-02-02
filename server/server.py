import time
import paho.mqtt.client as mqtt
import json
import consts
import messenger

broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT

client = mqtt.Client()

occupied_spaces = 0

def connect():
    client.connect(broker, broker_port, 60)

    for topic in consts.TOPICS.values():
        print("Subscribing to:", topic)
        client.subscribe(topic)

def process_message(client, userdata, message):
    message_decoded = message.payload.decode("utf8")
    try:
        response_dict = json.loads(message_decoded)
        if response_dict.get('sender') == consts.SENDER_NAME:
            return

        print(response_dict)
        response_controller(recieved_dict=response_dict)
    except Exception as e:
        print("Couldn't process message:", e)


def update_parking_count(action):
    """
    Updates the occupied parking space count based on entry or departure action.
    Sends the updated count to all gates.
    """
    global occupied_spaces

    if action == "entry":
        if occupied_spaces < consts.MAX_PARKING_SPACES:
            occupied_spaces += 1
    elif action == "departure":
        if occupied_spaces > 0:
            occupied_spaces -= 1

    parking_status_message = messenger.build_message('database_occupied', {
        "occupied_number": occupied_spaces,
        "max_spaces": consts.MAX_PARKING_SPACES
    })

    # Notify all gates
    client.publish(consts.TOPICS['entry'], parking_status_message)
    client.publish(consts.TOPICS['departure'], parking_status_message)
    print(f"Updated parking spaces: {occupied_spaces}/{consts.MAX_PARKING_SPACES}")




def response_controller(recieved_dict: dict):    
    header = recieved_dict.get('header')
    body = recieved_dict.get('body', {})

    if header == 'entry':
        register_entry(body)
    elif header == 'departure':
        register_departure(body)
    elif header == 'database_status':
        gate_confirmation(body)

        if body.get('status') is True:
            update_parking_count(body.get('action'))
            inform_ui(body)

    elif header == 'register_card':
        handle_registration(body)
    elif header == 'registration_response':
        handle_registration_response(body)

# DATABASE MESSAGING
def register_entry(recieved_dict):
    print("registering entry")
    database_message = {
        "card_uuid": recieved_dict.get('card_uuid'),
        "timestamp": time.asctime(time.localtime())
    }
    database_message_string = messenger.build_message("entry", database_message)
    client.publish(consts.TOPICS['db'], database_message_string)

def register_departure(recieved_dict):
    database_message = {
        "card_uuid": recieved_dict.get('card_uuid'),
        "timestamp": time.asctime(time.localtime())
    }
    database_message_string = messenger.build_message("departure", database_message)
    client.publish(consts.TOPICS['db'], database_message_string)

# GATE MESSAGING
def gate_confirmation(recieved_dict):
    gate_message_string = messenger.build_message('confirmed', {"status": recieved_dict.get('status')})
    client.publish(consts.TOPICS.get(recieved_dict.get('action')), gate_message_string)

    # Send message to UI after positive confirmation
    if recieved_dict.get('status') == True:
        inform_ui(recieved_dict)

# UI MESSAGING
def inform_ui(recieved_dict):
    global occupied_spaces

    message_dict = {
        "action": recieved_dict.get('action'),
        "user": recieved_dict.get('user'),
        "card_uuid": recieved_dict.get('card_uuid'),
        "max_spaces" : consts.MAX_PARKING_SPACES,
        "occupied_spaces" : occupied_spaces,
        "timestamp": time.asctime(time.localtime())
    }
    ui_message_string = messenger.build_message('parking_update', message_dict)
    client.publish(consts.TOPICS['ui'], ui_message_string)

# REGISTRATION MESSAGING
def handle_registration(body):
    card_uuid = body.get('card_uuid')
    if card_uuid:
        message_dict = {
            "card_uuid": card_uuid
        }
        ui_message = messenger.build_message('registration_prompt', message_dict)
        client.publish(consts.TOPICS['ui'], ui_message)
        print(f"Sent registration prompt to UI for card UUID: {card_uuid}")

def handle_registration_response(body):
    card_uuid = body.get('card_uuid')
    username = body.get('username')
    action = body.get('action')  # add, edit, delete

    if card_uuid and username and action:
        server_message = messenger.build_message('registration_update', {
            "card_uuid": card_uuid,
            "username": username,
            "action": action
        })
        client.publish(consts.TOPICS['db'], server_message)
        print(f"Processed registration response: {action} user {username} for card {card_uuid}")

if __name__ == '__main__':
    print("Starting server...")
    client.on_message = process_message
    connect()
    client.loop_forever()