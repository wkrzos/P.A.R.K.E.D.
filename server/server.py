from asyncio import sleep, wait
import time
import paho.mqtt.client as mqtt


broker = "10.0.2.15"
broker_port = 1883

client = mqtt.Client()

def call(name):
    client.publish("name", name)

def connect():
    client.connect(broker, broker_port, 60)
    client.subscribe('name2')
    client.loop_start()

def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf8")))
    print(message_decoded)


if __name__ == '__main__':
    connect()
    client.on_message = process_message

    while(True):
        message = input("message: ")
        call(message)