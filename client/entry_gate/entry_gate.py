import time
import json
import board
import neopixel
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# Import your custom libraries
import consts
import messenger
import lib.oled.SSD1331 as SSD1331

# Import the RFID library
from mfrc522 import MFRC522

# MQTT settings
broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT
client = mqtt.Client()

# Global flag used to avoid duplicate entry messages
waiting_for_confirmation = False

# Initialize WS2812 LED strip
NUM_PIXELS = 8
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=1.0/32, auto_write=False)

def connect():
    """Connect to the MQTT broker and subscribe to topics."""
    client.connect(broker, broker_port, 60)
    client.subscribe(consts.TOPIC)
    client.loop_start()

def process_message(client, userdata, message):
    """Handle incoming MQTT messages."""
    try:
        message_decoded = message.payload.decode("utf8")
        response_dict = json.loads(message_decoded)
        # Optionally ignore messages sent by this device
        if response_dict.get('sender') == consts.SENDER_NAME:
            return

        print("Received message:", response_dict)
        response_controller(response_dict)
    except Exception as e:
        print("Couldn't process message:", e)

def response_controller(received_dict: dict):
    """Route incoming messages based on their header."""
    header = received_dict.get('header')
    body = received_dict.get('body')
    
    # We now expect a confirmation and a status update only.
    if header == 'confirmed':
        if waiting_for_confirmation:
            register_confirmation(body)
    elif header == 'database_occupied':
        update_parking_status(body)
    else:
        print("Received unhandled header:", header)

def register_entry(card_uuid: str):
    """
    Called when an RFID card is scanned.
    Sends an MQTT message (with header "entry") that registers the entry.
    """
    global waiting_for_confirmation
    waiting_for_confirmation = True

    database_message = {
        "card_uuid": card_uuid,
    }
    message_string = messenger.build_message("entry", database_message)
    print("Registering entry with card UUID:", card_uuid)
    client.publish(consts.TOPIC, message_string)

def register_confirmation(received_dict: dict):
    """Handle the confirmation response from the server."""
    global waiting_for_confirmation
    waiting_for_confirmation = False
    if received_dict.get('status'):
        print("Entry confirmed!")
        light_green_led()
    else:
        print("Entry denied.")
        light_red_led()

def light_red_led():
    """Light up the red LED for 3 seconds."""
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(3)
    pixels.fill((0, 0, 0))
    pixels.show()

def light_green_led():
    """Light up the green LED for 3 seconds."""
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(3)
    pixels.fill((0, 0, 0))
    pixels.show()

def update_parking_status(received_dict: dict):
    """Update the OLED display with the parking status."""
    occupied_spaces = received_dict.get('occupied_number', 0)
    max_spaces = received_dict.get('max_spaces', consts.MAX_PARKING_SPACES)
    empty_spaces = max_spaces - occupied_spaces

    print(f"Parking Status: {occupied_spaces}/{max_spaces} occupied, {empty_spaces} empty")

    disp = SSD1331.SSD1331()
    disp.Init()
    disp.clear()

    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("./lib/oled/Font.ttf", 16)
    except Exception as e:
        print("Could not load custom font, using default.", e)
        font = ImageFont.load_default()

    draw.rectangle((0, 0, disp.width, disp.height), fill="BLACK")
    status_text = f"Empty: {empty_spaces}"
    text_width, text_height = draw.textsize(status_text, font=font)
    x = (disp.width - text_width) // 2
    y = (disp.height - text_height) // 2
    draw.text((x, y), status_text, font=font, fill="WHITE")
    disp.ShowImage(image, 0, 0)

def poll_rfid():
    """
    Continuously polls for an RFID card.
    When a card is detected, its UID is read, formatted, and sent via MQTT.
    """
    MIFAREReader = MFRC522()
    print("Place your card near the RFID reader...")

    while True:
        # Check for a card in the idle state.
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            # If a card is found, attempt to read its UID.
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                # Format the UID as a hexadecimal string.
                card_uuid = "".join([f"{byte:02X}" for byte in uid])
                print("RFID card detected:", card_uuid)
                register_entry(card_uuid)
                # Wait a few seconds to avoid reading the same card repeatedly.
                time.sleep(3)
        time.sleep(0.1)

if __name__ == '__main__':
    print("Starting Register Panel with RFID")
    connect()
    client.on_message = process_message

    # Instead of using a blocking input() loop, we start the RFID polling loop.
    poll_rfid()
