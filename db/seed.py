import psycopg2
from consts import DB_CONFIG

def seed_parking_users(conn):
    """Insert sample users into the parking_user table."""
    users = [
        # (username, password, email)
        ("johndoe", "password1", "john@example.com"),
        ("janesmith", "password2", "jane@example.com"),
        ("bobjohnson", "password3", "bob@example.com")
    ]
    with conn.cursor() as cur:
        for username, password, email in users:
            cur.execute(
                """
                INSERT INTO parking_user (username, password, email)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (username, password, email)
            )
            user_id = cur.fetchone()[0]
            print(f"Inserted user '{username}' with id {user_id}")
        conn.commit()

def seed_cards(conn):
    """Insert sample cards into the card table (each linked to a user)."""
    # Map emails to card codes
    cards = [
        ("CARD123", "john@example.com"),
        ("CARD456", "jane@example.com"),
        ("CARD789", "bob@example.com")
    ]
    with conn.cursor() as cur:
        for card_code, user_email in cards:
            # Retrieve the user_id for the given email.
            cur.execute("SELECT id FROM parking_user WHERE email = %s", (user_email,))
            result = cur.fetchone()
            if result:
                user_id = result[0]
                cur.execute(
                    """
                    INSERT INTO card (card_code, user_id)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (card_code, user_id)
                )
                card_id = cur.fetchone()[0]
                print(f"Inserted card '{card_code}' for user '{user_email}' with card id {card_id}")
            else:
                print(f"User with email '{user_email}' not found. Skipping card '{card_code}'.")
        conn.commit()

def seed_parking_gates(conn):
    """Insert sample parking gates into the parking_gate table."""
    gates = [
        "ENTRY_GATE_1",
        "DEPARTURE_GATE_1"
    ]
    with conn.cursor() as cur:
        for gate_code in gates:
            cur.execute(
                """
                INSERT INTO parking_gate (gate_code)
                VALUES (%s)
                RETURNING id
                """,
                (gate_code,)
            )
            gate_id = cur.fetchone()[0]
            print(f"Inserted parking gate '{gate_code}' with id {gate_id}")
        conn.commit()

def seed_gate_logs(conn):
    """
    Optionally, insert sample gate logs into the gate_log table.
    This simulates a record of an entry action.
    """
    with conn.cursor() as cur:
        # Retrieve card id for a known card code.
        cur.execute("SELECT id FROM card WHERE card_code = %s", ("CARD123",))
        card_result = cur.fetchone()
        # Retrieve gate id for the entry gate.
        cur.execute("SELECT id FROM parking_gate WHERE gate_code = %s", ("ENTRY_GATE_1",))
        gate_result = cur.fetchone()
        if card_result and gate_result:
            card_id = card_result[0]
            gate_id = gate_result[0]
            cur.execute(
                """
                INSERT INTO gate_log (gate_id, card_id, is_entry, status)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (gate_id, card_id, True, "SUCCESS")
            )
            log_id = cur.fetchone()[0]
            print(f"Inserted sample gate log with id {log_id}")
        else:
            print("Could not find matching card or gate for gate_log seeding.")
        conn.commit()

def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected to the database successfully.")

        print("\nSeeding parking users...")
        seed_parking_users(conn)

        print("\nSeeding cards...")
        seed_cards(conn)

        print("\nSeeding parking gates...")
        seed_parking_gates(conn)

        print("\nSeeding gate logs...")
        seed_gate_logs(conn)

        print("\nDatabase seeding completed.")
    except Exception as e:
        print("Error during seeding:", e)
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
