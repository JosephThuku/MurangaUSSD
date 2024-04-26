import os
import sqlite3
from flask import Flask, request
from mpesa import mpay  # Assuming this module handles M-Pesa transactions

app = Flask(__name__)

DATABASE = 'parking.db'

# Initialize database schema
def init_db():
    """
    Initialize the database schema if it doesn't exist.
    """
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
    """
    Insert a parking reservation into the database.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO parking_reservations (phone_number, location) 
            VALUES (?, ?)
        ''', (phone_number, location))
        conn.commit()

# Function to check if a user has paid within the last 24 hours
def has_paid_within_24_hours(phone_number):
    """
    Check if a user has paid for parking within the last 24 hours.
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM parking_reservations 
            WHERE phone_number = ? AND payment_status = 'PAID'
            AND reservation_time >= datetime('now', '-1 day')
        ''', (phone_number,))
        return cursor.fetchone() is not None

@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    """
    Callback for the USSD service.
    """
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    response = ""

    # Initial prompt to the user after dialing the USSD code
    if text == '':
        response = "CON Welcome to Muranga county. Select a module:\n"
        response += "1. Citizen Self Service\n"
        response += "2. Revenue Officer\n"
        response += "3. Enforcement/Inspectorate\n"
        response += "4. KRA"

    # If user selects the "Citizen Self Service" option
    elif text == '1':
        response = "CON Citizen Self Service. Select a module:\n"
        response += "1. Parking\n"
        response += "2. Cess"

    # If user selects the parking module
    elif text.startswith('1*'):
        if text == '1*1':  # If user selects the "Parking" option
            response = "CON Select a parking module:\n"
            response += "1. Daily Parking\n"
            response += "2. Monthly Parking\n"
            response += "3. Reserved Parking\n"
            response += "4. Private Yearly Parking\n"
            response += "5. Yearly Stickers"

        elif text.startswith('1*1*1'):  # If user selects a specific parking option
            response = "CON Select a parking spot:\n"
            response += "1. A1\n"
            response += "2. A2\n"
            response += "3. A3\n"
            response += "4. A4\n"
            response += "5. A5"

        elif text.startswith('1*1*1*'):  # If user selects a parking spot
            location = text.split('*')[-1]  # Extract the location from the USSD input
            # Check if the user has paid within the last 24 hours
            if has_paid_within_24_hours(phone_number):
                response = "END You have already paid for parking within the last 24 hours."
            else:
                insert_reservation(phone_number, location)  # Insert parking reservation into the database
                response = "CON Select Payment Option:\n"
                response += "1. Pay Now\n"
                response += "2. Pay Later"

        # Add more conditions as needed for subsequent steps in the process

    # Handle payment options
    elif text == '1*1*1*1':  # If user selects "Pay Now"
        response = "CON Enter MPESA Phone Number:\n"
        # Save relevant data for later retrieval (e.g., vehicle registration number)
        # Proceed with payment process using M-Pesa API

    # Handle other options and edge cases

    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))
