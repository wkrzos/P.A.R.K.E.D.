import json
import paho.mqtt.client as mqtt
import psycopg2
from messenger import build_message
from consts import DB_CONFIG, BROKER_IP, BROKER_PORT, SENDER_NAME

# Added comment with GPT o3 since I was getting lost in the code, so it should help you too.

def get_db_connection():
    """Establish and return a new PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)

# --- MQTT Callbacks ---

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker, rc:", rc)
    client.subscribe("/database")

def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        header = message.get("header")
        body = message.get("body", {})
        sender = message.get("sender")

        if sender == SENDER_NAME:
            return

        if msg.topic == "/database":
            if header == "entry":
                handle_entry(client, body)
            elif header == "departure":
                handle_departure(client, body)
            else:
                print("Unknown header on /database:", header)
        else:
            print("Received message on an unexpected topic:", msg.topic)
    except Exception as e:
        print("Error processing message:", e)

# --- Database Handlers ---

def handle_entry(client, body):
    """
    Processes an "entry" message coming from the server.
    The expected message body:
      { "card_uuid": <card_uuid> }
    It attempts to log an entry in the DB and then publishes a
    "database_status" message with details.
    """
    card_uuid = body.get("card_uuid")
    if not card_uuid:
        print("Entry message missing card_uuid")
        return

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Look up the card in the DB (assume card_code matches card_uuid).
        cur.execute("SELECT id, user_id FROM card WHERE card_code = %s", (card_uuid,))
        card_row = cur.fetchone()
        if not card_row:
            print("Card not found:", card_uuid)
            status = False
            username = ""
        else:
            card_id, user_id = card_row
            # Get the user's name (using the 'username' field).
            cur.execute("SELECT username FROM parking_user WHERE id = %s", (user_id,))
            user_row = cur.fetchone()
            username = user_row[0] if user_row else ""
            # Determine the entry gate ID (via a simple mapping here).
            entry_gate_id = get_gate_id("entry_gate")
            # Insert a new record into the gate_log table.
            cur.execute(
                "INSERT INTO gate_log (gate_id, card_id, is_entry, status) VALUES (%s, %s, %s, %s)",
                (entry_gate_id, card_id, True, "SUCCESS")
            )
            conn.commit()
            print("Entry logged for card:", card_uuid)
            status = True
    except Exception as e:
        print("Error in handle_entry:", e)
        status = False
        username = ""
    finally:
        if conn:
            conn.close()

    # Publish a "database_status" message back to the server.
    message_body = {
        "action": "entry",
        "status": status,
        "card_uuid": card_uuid,
        "user": username
    }
    db_status_message = build_message("database_status", message_body)
    client.publish("/database", db_status_message)

def handle_departure(client, body):
    """
    Processes a "departure" message coming from the server.
    The expected message body:
      { "card_uuid": <card_uuid> }
    It attempts to log a departure in the DB and then publishes a
    "database_status" message with details.
    """
    card_uuid = body.get("card_uuid")
    if not card_uuid:
        print("Departure message missing card_uuid")
        return

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Look up the card based on card_uuid.
        cur.execute("SELECT id, user_id FROM card WHERE card_code = %s", (card_uuid,))
        card_row = cur.fetchone()
        if not card_row:
            print("Card not found:", card_uuid)
            status = False
            username = ""
        else:
            card_id, user_id = card_row
            cur.execute("SELECT username FROM parking_user WHERE id = %s", (user_id,))
            user_row = cur.fetchone()
            username = user_row[0] if user_row else ""
            # Determine the departure gate ID.
            departure_gate_id = get_gate_id("departure_gate")
            # Insert a departure record into gate_log.
            cur.execute(
                "INSERT INTO gate_log (gate_id, card_id, is_entry, status) VALUES (%s, %s, %s, %s)",
                (departure_gate_id, card_id, False, "SUCCESS")
            )
            conn.commit()
            print("Departure logged for card:", card_uuid)
            status = True
    except Exception as e:
        print("Error in handle_departure:", e)
        status = False
        username = ""
    finally:
        if conn:
            conn.close()

    # Publish a "database_status" message back to the server.
    message_body = {
        "action": "departure",
        "status": status,
        "card_uuid": card_uuid,
        "user": username
    }
    db_status_message = build_message("database_status", message_body)
    client.publish("/database", db_status_message)

# --- Helpers ---

def get_gate_id(gate_code):
    """
    Returns the database ID for a given gate code.
    Hard coded for now.
    """
    gate_mapping = {
        "entry_gate": 1,
        "departure_gate": 2
    }
    return gate_mapping.get(gate_code, 0)

# --- Main ---

def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(BROKER_IP, BROKER_PORT, 60)
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
