# Conventional messages (recieved)

## database (/database)

### "database_status"
    {
        "header" : "database_status",
        "sender" : "database" (or other sender name),
        "body" : {
            "action" : "entry" / "departure",
            "status" : True / False (true means its ok and we can send info to gate, false means something failed)
            "card_uuid" : card_uuid,
            "user" : name and surmane of user
        }

    }

### "database_occupied"
    {
        "header" : "database_occupied",
        "sender" : "database" (or other sender name),
        "body" : {
            "occupied_number" : number of cars on parking rn
        }

    }

## gate (/entries, /departures)
### "entry"
    {
        "header" : "entry",
        "sender" : "entry_gate",
        "body" : {
            "card_uuid" : card_uuid
        }

    }

### "departure"
    {
        "header" : "departure",
        "sender" : "departure_gate",
        "body" : {
            "card_uuid" : card_uuid
        }

    }

## ui (/ui)

### "registration_prompt

    {
    "header": "registration_prompt",
    "sender": "parking_server",
    "body": {
        "card_uuid": "ABC123XYZ"
        }
    }


## "register_panel" (/register)
### "register_card"

    {
    "header": "register_card",
    "sender": "register_panel",
    "body": {
        "card_uuid": "ABC123XYZ"
        }
    }



## "ui" (/ui)
### "registration_response"

    {
    "header": "registration_response",
    "sender": "ui",
    "body": {
        "card_uuid": "UUID_HERE",
        "username": "Name Surname",
        "action": "add" / "edit" / "delete"
        }
    }


# Conventional messages (sent)

## gate (/entries, /departures)

### "confirmed"

    {
        "header" : "confirmed",
        "sender" : "parking_server",
        "body" : {
            "status" : True / False
        }

    }

## database (/database)

### "departure"

    {
        "header" : "departure",
        "sender" : "parking_server",
        "body" : {
            "card_uuid" : card_uuid,
            "timestamp" : time.asctime()
        }

    }


### "entry"

    {
        "header" : "entry",
        "sender" : "parking_server",
        "body" : {
            "card_uuid" : card_uuid,
            "timestamp" : time.asctime()
        }

    }