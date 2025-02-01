from asyncio import sleep, wait
import time
import paho.mqtt.client as mqtt

import json
import consts
import messenger


broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT

client = mqtt.Client()


def connect():
    client.connect(broker, broker_port, 60)
    
    for topic in consts.TOPICS.values():
        client.subscribe(topic)

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
    if header == 'departure':
        register_departure(body)
    if header == 'database_status':
        gate_confirmation(body)
        if body['status'] == True:
            inform_ui(body)



# DATABASE MESSAGING
def register_entry(recieved_dict):
    database_message = {
        "card_uuid" : recieved_dict['card_uuid'],
        "timestamp" : time.asctime(time.localtime())
    }

    database_message_string = messenger.build_message("entry", database_message)
    client.publish(consts.TOPICS['db'], database_message_string)



def register_departure(recieved_dict):
    database_message = {
        "card_uuid" : recieved_dict['card_uuid'],
        "timestamp" : time.asctime(time.localtime())
    }

    database_message_string = messenger.build_message("departure", database_message)
    client.publish(consts.TOPICS['db'], database_message_string)



# GATE MESSAGING
def gate_confirmation(recieved_dict):
    gate_message_string = messenger.build_message('confirmed', {"status" : recieved_dict['status']})

    client.publish(consts.TOPICS[recieved_dict['action']], gate_message_string)



# UI MESSAGING
def inform_ui(recieved_dict):
    message_dict = {
        "action" : recieved_dict['action'],
        "user" : recieved_dict['user'],
        "card_uuid" : recieved_dict['card_uuid']
    }

    ui_message_string = messenger.build_message('parking_update', message_dict)

    client.publish(consts.TOPICS['ui'], ui_message_string)



if __name__ == '__main__':


    print("hi")
    connect()
    client.on_message = process_message

    client.loop_forever()

    #while(True):
    #    message = input("message: ")
        #   call(message)