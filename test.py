from flask import Flask, request
import os
import sqlite3

app = Flask(__name__)
DATABASE = 'parking.db'

# Initialize database schema
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                location TEXT NOT NULL,
                payment_status TEXT DEFAULT 'PENDING',
                reservation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Function to insert parking reservation into the database
def insert_reservation(phone_number, location):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO parking_reservations (phone_number, location) 
            VALUES (?, ?)
        ''', (phone_number, location))
        conn.commit()

# Function to check if a user has paid for parking within the last 24 hours
def has_paid_within_24_hours(phone_number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM parking_reservations 
            WHERE phone_number = ? , payment_status = 'PAID'
            AND reservation_time >= datetime('now', '-1 day')
        ''', (phone_number,))
        return cursor.fetchone() is not None

@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    response = ""

    if text == '':
        response = "CON Welcome to Nairobi Parking System. Select an option: \n"
        response += "1. Reserve Parking \n"
        response += "2. Check Parking Status"
    elif text == '1':
        response = "CON Choose your location: \n"
        response += "1. Konja\n"
        response += "2. Kileleshwa\n"
        response += "3. Kawangware\n"
        response += "4. Kijabe"
    elif text.startswith('1*'):  # User has chosen a location
        # Extract the chosen location
        location_code = text.split('*')[-1]
        if location_code in ['1', '2', '3', '4']:
            location_mapping = {'1': 'Konja', '2': 'Kileleshwa', '3': 'Kawangware', '4': 'Kijabe'}
            location = location_mapping[location_code]
            # Check if user has paid for parking within the last 24 hours
            if has_paid_within_24_hours(phone_number):
                response = "END You have already paid for parking within the last 24 hours."
            else:
                # ASk user to enter MPESA phone number
                response = "CON Please enter your MPESA phone number to pay for parking"
                # Insert the reservation into the database
                insert_reservation(phone_number, location)

                # Now return a response to the user telling him he will recieve a stk push shortly to enter mpesa pin 
        else:
            response = "END Invalid choice"
    elif text.startswith('1*'):  # User has entered MPESA phone number
        # Here you can implement the logic to handle the payment
        response = "END Parking reservation successful. You will receive a confirmation shortly."
    elif text == '2':
        # Logic to check parking status goes here
        response = "END Parking status: Available"  # Placeholder response
    else:
        response = "END Invalid choice"

    return response

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))
