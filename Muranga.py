import os
import sqlite3
from flask import Flask, request
from mpesa import mpay

app = Flask(__name__)

DATABASE = 'parking.db'

# Initialize database schema
def init_db():
    """
    this method initializes the database schema
    args: None
    returns: None
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

#execute the init_db function
init_db()

# Function to insert parking reservation into the database
def insert_reservation(phone_number, location):
    """
    this method inserts a parking reservation into the database
    args:
        phone_number: the phone number of the user
        location: the location of the parking spot

    returns: None
    """
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO parking_reservations (phone_number, location) 
            VALUES (?, ?)
        ''', (phone_number, location))
        conn.commit()


def has_paid_within_24_hours(phone_number):
    """
    this method checks if a user has paid for parking within the last 24 hours
    args:
        phone_number: the phone number of the user
    
    returns:
            boolean: True if the user has paid for parking within the last 24 hours, False otherwise
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
    this method is the callback for the ussd service
    its responsible for handling the ussd requests from the user
    acts as the logic for the ussd service
    args: None
    returns: response: the response to be sent back to the user from africastalking


    """
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    response = ""

    #first prompt to the user after dialing the ussd code
    if text == '':
        response = "CON Welcome to Muranga county select a module\n"
        response += "1. Citizen Self Service \n"
        response += "2. Revenue Officer \n"
        response += "3 Enforcement/ Inpectorate\n"
        response += "4. KRA"

    #if user selects the first option(citizen self service)
    elif text == '1':
        response = "CON Citizen Selft Sevice select a module\n"
        response += "1. Parking\n"
        response += "2. Cess\n"
    
    #if user selects the parking module
    elif text.startswith('1*'):
        print("user asked to select parking module")
        response = "CON select a module\n"
        response += "1. Pay Parking\n"
        response += "2. Check Status\n"

        #if user selects the pay parking module
        if text == '1*1':

            #check if user has paid for parking within the last 24 hours
            if has_paid_within_24_hours(phone_number):
                response = "END You have already paid for parking within the last 24 hours."
            

            #check if user has paid for parking within the last 24 hours
            # if has_paid_within_24_hours(phone_number):
            #     response = "END You have already paid for parking within the last 24 hours."
            # else:
            response = "CON select a parking module\n"
            response += "1. Daily Parking\n"
            response += "2. Monthly Parking\n"
            response += "3. Reserved Parking\n"
            response += "4. Private Yearly Parking\n"
            response += "5. Yearly Stickers\n"
        
        # if any of above parking module then prompt user to select vehicle option
        elif text=='1*1*1' or text=='1*1*2' or text=='1*1*3' or text=='1*1*4' or text=='1*1*5':
            response = "CON Select Vehicle Option\n"
            response += "1. Motorbike\n"
            response += "2. TukTuk\n"
            response += "3. Saloon\n"
            response += "4. Van\n"
            response += "5. Lorry\n"
            response += "6. Trailer\n"
            response += "7. Bus\n"
            response += "8. Tractor\n"
            response += "9. Other\n"

        #prompt user to select a zone if he has selected a vehicle option
        elif text=='1*1*1*1' or text=='1*1*1*2' or text=='1*1*1*3' or text=='1*1*1*4' or text=='1*1*1*5' or text=='1*1*1*6' or text=='1*1*1*7' or text=='1*1*1*8' or text=='1*1*1*9':
            response = "CON Select a Zone\n"
            response += "1. Muranga Town A\n"
            response += "2. Maragwa A\n"
            response += "3. Kandara A\n"
            response += "4. Kigumo A\n"
            response += "5. Kangema A\n"
            response += "6. Gatanga A\n"
            response += "7. Mathioya A\n"
            response += "8. Kiharu A\n"
            response += "9. Kigumo B\n"
        
        #prompt user to enter vehicle registration number
        elif text=='1*1*1*1*1' or text=='1*1*1*1*2' or text=='1*1*1*1*3' or text=='1*1*1*1*4' or text=='1*1*1*1*5' or text=='1*1*1*1*6' or text=='1*1*1*1*7' or text=='1*1*1*1*8' or text=='1*1*1*1*9':
            response = "CON SELECT A parking spot\n"
            response += "1. A1\n"
            response += "2. A2\n"
            response += "3. A3\n"
            response += "4. A4\n"
            response += "5. A5\n"
            response += "6. A6\n"

        #prompt user to enter vehicle registration number
        elif text=='1*1*1*1*1*1' or text=='1*1*1*1*2*2' or text=='1*1*1*1*3*3' or text=='1*1*1*1*4*4' or text=='1*1*1*1*5*5' or text=='1*1*1*1*6*6':
            response = "CON Enter Vehicle Registration Number\n"

        #if user has enterd re no
        elif text:
            #insert reservation
            location = text.split('*')[-1]
            insert_reservation(phone_number, location)
            response = "CON Selcet Payment "
            response += "1. Pay Now\n"
            response += "2. Pay Later\n"
        
            if text:
                
                # insert_reservation(phone_number, location)
                response = "END You will receive a STK push shortly to enter your MPESA pin"
               #remove + in phone number
                phone = phone_number.replace("+", "")
                print(f"Your phone number is: {phone}")
                mpesa= mpay(phone)
                print(f"mpesa response: {mpesa}")
                
    else:
        response = "END Invalid choice"
    return response
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT'))