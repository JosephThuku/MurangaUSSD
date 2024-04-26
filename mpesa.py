from tkinter import *
import requests
from requests.auth import HTTPBasicAuth
import base64
import datetime


def mpay(phone):
    consumer_key = "DLAoWxSG7G7IGqtB29O5VONkXZdKxG9M"  # Consumer Key
    consumer_secret = "HDJOupIf0HCaLGQ0"  # Consumer Secret
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    response = r.json()

    access_token = response['access_token']

    phone = phone
    saa = datetime.datetime.now()
    timestamp_format = saa.strftime("%Y%m%d%H%M%S")

    businessshortcode = "174379"

    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # pass_key

    pd_decode = businessshortcode + passkey + timestamp_format

    ret = base64.b64encode(pd_decode.encode())

    pd = ret.decode('utf-8')

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": businessshortcode,
        "Password": pd,
        "Timestamp": timestamp_format,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "10",
        "PartyA": phone,
        "PartyB": businessshortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://41.139.244.238:80/callback",
        "AccountReference": "MurangaCountyGovernment",
        "TransactionDesc": "fee payment"
    }

    response = requests.post(api_url, json=request, headers=headers)

    print(response.text)

