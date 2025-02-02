from asyncio import sleep, wait
import time
import paho.mqtt.client as mqtt
import json
import consts
import messenger
import board
import neopixel
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331


broker = consts.BROKER_IP
broker_port = consts.BROKER_PORT

client = mqtt.Client()

waiting_for_confirmation = False

# Initialize WS2812 LED strip
NUM_PIXELS = 8
pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=1.0/32, auto_write=False)

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

        print(response_dict)

        response_controller(recieved_dict=response_dict)
    except:
        print("Couldn't process message")


def response_controller(recieved_dict: dict):
    global waiting_for_confirmation

    header = recieved_dict['header']
    body = recieved_dict['body']

    if header == 'entry':
        register_entry(body)
    if header == 'confirmed':
        if waiting_for_confirmation:
            register_confirmation(body)
    if header == 'database_occupied':
        update_parking_status(body)


def register_entry():
    global waiting_for_confirmation
    database_message = {
            "card_uuid" : "CARD789",
    }

    waiting_for_confirmation = True

    print("registering entry")

    database_message_string = messenger.build_message("entry", database_message)

    print(database_message_string)

    client.publish(consts.TOPIC, database_message_string)

def register_confirmation(recieved_dict):
    global waiting_for_confirmation
    waiting_for_confirmation = False
    if recieved_dict['status']:
        print('yippieee')
        light_green_led()
    else:
        print('womp womp')
        light_red_led()


def light_red_led():
    pixels.fill((255, 0, 0))
    pixels.show()

    time.sleep(3)

    pixels.fill((0,0,0))
    pixels.show()


def light_green_led():
    pixels.fill((0, 255, 0))
    pixels.show()

    time.sleep(3)

    pixels.fill((0,0,0))
    pixels.show()

def update_parking_status(received_dict):
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


if __name__ == '__main__':


    print("hi")
    connect()
    client.on_message = process_message

    while(True):
        message = input("message: ")
        register_entry()