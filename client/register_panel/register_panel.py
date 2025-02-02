import paho.mqtt.client as mqtt
import json
import messenger
import consts
import time
from mfrc522 import MFRC522

broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT
client = mqtt.Client()

def connect():
    client.connect(broker, broker_port, 60)
    client.loop_start()

def send_card_uuid():
    MIFAREReader = MFRC522()
    print("Place your card near the RFID reader...")
    
    while True:
        # Request card (idle state)
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                # Format the UID as a hex string
                card_uuid = "".join([f"{byte:02X}" for byte in uid])
                # Build and send the MQTT message
                message = messenger.build_message("register_card", {"card_uuid": card_uuid})
                client.publish(consts.TOPIC, message)
                print(f"Sent card UUID: {card_uuid}")
                time.sleep(3)
        time.sleep(0.1)

if __name__ == '__main__':
    print("Starting Register Panel...")
    connect()
    send_card_uuid()
