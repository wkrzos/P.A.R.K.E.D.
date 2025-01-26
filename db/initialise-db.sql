-- 1. User table (inherits from Base)
CREATE TABLE parking_user (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email    VARCHAR(255) NOT NULL
)

ALTER TABLE parking_user ADD CONSTRAINT unique_email UNIQUE (email);

-- 2. Card table (inherits from Base)
CREATE TABLE card (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    card_code VARCHAR(255) NOT NULL,
    user_id   INT NOT NULL,

    FOREIGN KEY (user_id) REFERENCES parking_user(id)
)

CREATE INDEX idx_card_userid ON card (user_id);

-- 3. ParkingGate table (inherits from Base)
CREATE TABLE parking_gate (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    gate_code VARCHAR(255) NOT NULL
)

CREATE INDEX idx_parking_gatecode ON parking_gate (gate_code);

-- 4. GateLog table (inherits from Base)
CREATE TABLE gate_log (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    gate_id           INT NOT NULL,
    card_id           INT NOT NULL,
    gate_accessed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_entry          BOOLEAN NOT NULL,
    status            VARCHAR(10) NOT NULL CHECK (status IN ('SUCCESS', 'DENIED')),

    FOREIGN KEY (gate_id) REFERENCES parking_gate(id),
    FOREIGN KEY (card_id) REFERENCES card(id)
)

-- 6. Indexes for GateLog
CREATE INDEX idx_gateuse_gateid     ON gate_log (gate_id);
CREATE INDEX idx_gateuse_cardid     ON gate_log (card_id);
CREATE INDEX idx_gateuse_accessedat ON gate_log (gate_accessed_at);
CREATE INDEX idx_gate_log_status    ON gate_log (status);

-- 7. Update_at trigger
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_trigger
  BEFORE UPDATE ON base
  FOR EACH ROW
  EXECUTE PROCEDURE set_updated_at();
