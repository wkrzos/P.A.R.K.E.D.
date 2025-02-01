import json
import time
import paho.mqtt.client as mqtt
import psycopg2
from messenger import build_message
from consts import DB_CONFIG, BROKER_IP, BROKER_PORT

# Added ai generated comments since i was getting lost in the code myself

def get_db_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(**DB_CONFIG)

# --- MQTT ---

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker, rc:", rc)
    client.subscribe("/entries")
    client.subscribe("/departures")
    client.subscribe("/database")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        message = json.loads(msg.payload.decode())
        header = message.get("header")
        body = message.get("body", {})
        sender = message.get("sender")
        
        if topic == "/entries":
            if header == "entry":
                handle_entry(client, body)
            elif header == "confirmed":
                print("Entry confirmation:", body)
            else:
                print("Unknown header on /entries:", header)
        elif topic == "/departures":
            if header == "departure":
                handle_departure(client, body)
            else:
                print("Unknown header on /departures:", header)
        elif topic == "/database":
            if header == "database_status":
                handle_database_status(client, body)
            elif header == "database_occupied":
                handle_database_occupied(client, body)
            else:
                print("Unknown header on /database:", header)
        else:
            print("Unknown topic:", topic)
    except Exception as e:
        print("Error processing message:", e)

# --- Gate Handlers ---

def handle_entry(client, body):
    """
    Processes an entry event from an entry gate.
    Expected message body:
      {
          "card_uuid": <card_uuid>
      }
    """
    card_uuid = body.get("card_uuid")
    if not card_uuid:
        print("Entry message missing card_uuid")
        return

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Look up card based on card_uuid. Assume card_code in the DB matches card_uuid.
        cur.execute("SELECT id, user_id FROM card WHERE card_code = %s", (card_uuid,))
        card_row = cur.fetchone()
        if not card_row:
            print("Card not found:", card_uuid)
            confirmed = build_message("confirmed", {"status": False})
            client.publish("/entries", confirmed)
            return

        card_id, user_id = card_row
        # Retrieve the gate ID for the entry gate (implement mapping as needed)
        entry_gate_id = get_gate_id("entry_gate")
        
        # Insert an entry record into the gate_log table.
        cur.execute(
            "INSERT INTO gate_log (gate_id, card_id, is_entry, status) VALUES (%s, %s, %s, %s)",
            (entry_gate_id, card_id, True, "SUCCESS")
        )
        conn.commit()
        print("Entry logged for card:", card_uuid)
        
        # Send a confirmation back to the gate.
        confirmed = build_message("confirmed", {"status": True})
        client.publish("/entries", confirmed)
        
        # Publish an "entry" message to the /database topic with a timestamp.
        timestamp = time.asctime()
        entry_msg = build_message("entry", {"card_uuid": card_uuid, "timestamp": timestamp})
        client.publish("/database", entry_msg)
    except Exception as e:
        print("Error in handle_entry:", e)
        confirmed = build_message("confirmed", {"status": False})
        client.publish("/entries", confirmed)
    finally:
        if conn:
            conn.close()

def handle_departure(client, body):
    """
    Processes a departure event from a departure gate.
    Expected message body:
      {
          "card_uuid": <card_uuid>
      }
    """
    card_uuid = body.get("card_uuid")
    if not card_uuid:
        print("Departure message missing card_uuid")
        return

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, user_id FROM card WHERE card_code = %s", (card_uuid,))
        card_row = cur.fetchone()
        if not card_row:
            print("Card not found:", card_uuid)
            confirmed = build_message("confirmed", {"status": False})
            client.publish("/departures", confirmed)
            return

        card_id, user_id = card_row
        departure_gate_id = get_gate_id("departure_gate")
        cur.execute(
            "INSERT INTO gate_log (gate_id, card_id, is_entry, status) VALUES (%s, %s, %s, %s)",
            (departure_gate_id, card_id, False, "SUCCESS")
        )
        conn.commit()
        print("Departure logged for card:", card_uuid)
        
        confirmed = build_message("confirmed", {"status": True})
        client.publish("/departures", confirmed)
        
        # Publish a "departure" message to /database with a timestamp.
        timestamp = time.asctime()
        departure_msg = build_message("departure", {"card_uuid": card_uuid, "timestamp": timestamp})
        client.publish("/database", departure_msg)
    except Exception as e:
        print("Error in handle_departure:", e)
        confirmed = build_message("confirmed", {"status": False})
        client.publish("/departures", confirmed)
    finally:
        if conn:
            conn.close()

# --- Database Message Handlers ---

def handle_database_status(client, body):
    """
    Processes a "database_status" message from the database.
    Expected body content:
      {
          "action": "entry" or "departure",
          "status": True/False,
          "card_uuid": <card_uuid>,
          "user": "<name> <surname>"
      }
    """
    action = body.get("action")
    status = body.get("status")
    card_uuid = body.get("card_uuid")
    user = body.get("user")
    print(f"Database status update - Action: {action}, Status: {status}, Card: {card_uuid}, User: {user}")

def handle_database_occupied(client, body):
    """
    Processes a "database_occupied" message from the database.
    Expected body content:
      {
          "occupied_number": <number>
      }
    """
    occupied_number = body.get("occupied_number")
    print("Current parking occupancy:", occupied_number)

# --- Helpers ---

def get_gate_id(gate_code):
    """
    Given a gate_code (e.g., "entry_gate" or "departure_gate"), return the corresponding database ID.
    This implementation uses a simple mapping. You may choose to query the database instead.
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
