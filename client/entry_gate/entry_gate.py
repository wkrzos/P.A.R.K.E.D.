from asyncio import sleep, wait
import time
import paho.mqtt.client as mqtt

import json
import consts
import messenger


broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT

client = mqtt.Client()

waiting_for_confirmation = False

def connect():
    client.connect(broker, broker_port, 60)
    
    client.subscribe(consts.TOPIC)

    client.loop_start()

def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf8")))
    try:
        response_dict = json.loads(message_decoded)
        if response_dict['sender'] == consts.SENDER_NAME:
            return

        response_controller(recieved_dict=response_dict)
    except:
        print("Couldn't process message")


def response_controller(recieved_dict: dict):
    header = recieved_dict['header']
    body = recieved_dict['body']

    if header == 'entry':
        register_entry(body)
    if header == 'confirmed':
        register_confirmation(body)


def register_entry(recieved_dict):
    database_message = {
            "card_uuid" : "ABC123",
    }

    waiting_for_confirmation = True

    database_message_string = messenger.build_message("entry", database_message)
    client.publish(consts.TOPIC, database_message_string)

def register_confirmation(recieved_dict):
    if recieved_dict['status']:
        print('yippieee')
        light_green_led
    else:
        print('womp womp')
        light_red_led


def light_red_led():
    pass


def light_green_led():
    pass

if __name__ == '__main__':


    print("hi")
    connect()
    client.on_message = process_message

    while(True):
        message = input("message: ")
        register_entry