import paho.mqtt.client as mqtt
import json
import messenger
import consts

broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT
client = mqtt.Client()

def connect():
    client.connect(broker, broker_port, 60)
    client.loop_start()

def send_card_uuid():
    while True:
        card_uuid = input("Enter card UUID: ")
        if card_uuid:
            message = messenger.build_message("register_card", {"card_uuid": card_uuid})
            client.publish(consts.TOPIC, message)
            print(f"Sent card UUID: {card_uuid}")

if __name__ == '__main__':
    print("Starting Register Panel...")
    connect()
    send_card_uuid()
