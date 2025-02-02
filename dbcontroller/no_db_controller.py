import json
import paho.mqtt.client as mqtt
import messenger
import consts

broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT
client = mqtt.Client()

def connect():
    client.connect(broker, broker_port, 60)
    client.subscribe(consts.TOPIC)
    print(f"Subscribed to topic: {consts.TOPIC}")

def on_message(client, userdata, message):
    try:
        message_decoded = message.payload.decode("utf8")
        recieved_dict = json.loads(message_decoded)
        
        if recieved_dict.get('sender') == consts.SENDER_NAME:
            return

        print(f"Received message: {recieved_dict}")

        # Simulate positive confirmation
        confirmation = {
            "action": recieved_dict.get('header'),
            "status": True,
            "card_uuid": recieved_dict.get('body', {}).get('card_uuid', 'TEST_CARD'),
            "user": "Test User"
        }

        confirmation_message = messenger.build_message("database_status", confirmation)
        client.publish(consts.TOPIC, confirmation_message)
        print(f"Sent confirmation: {confirmation}")
    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == '__main__':
    print("Starting Test Controller...")
    client.on_message = on_message
    connect()
    client.loop_forever()
