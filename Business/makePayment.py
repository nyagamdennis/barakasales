import requests
from datetime import datetime
from rest_framework.response import Response
import json
from datetime import timedelta
import base64
from dotenv import load_dotenv
import os

load_dotenv()


def authenticate(client_credentisials):
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=client_credentisials)
    if response.status_code == 200:
        json_response = json.loads(response.text)
        access_token = json_response["access_token"]
        return access_token
    else:
        return None



def make_payment(phone_number, amount):
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECREAT')
    client_credentisials = (consumer_key, consumer_secret)
    pass_key = os.getenv('PASS_KEY')
    print('client cledentisl ', client_credentisials)
    print('running pass_key ', pass_key)
    access_token = authenticate(client_credentisials)
    print('running access token ', access_token)

    headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {access_token}'
      
    }

  
    ShortCode = '174379'
    # Generate the timestamp
    timestamp = (datetime.now() + timedelta(hours=3)).strftime("%Y%m%d%H%M%S")
    # Generate the password by combining ShortCode, pass_key, and timestamp, then encoding it in base64
    data_to_encode = ShortCode + pass_key + timestamp
    encoded_password = base64.b64encode(data_to_encode.encode()).decode()
    payload = {
        "BusinessShortCode": 174379,
        "Password": encoded_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": 174379,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://7583-154-159-252-12.ngrok-free.app/business/mpesa-confirm/",
        "AccountReference": "Msoft Ltd",
        "TransactionDesc": "Subscribe to professional plan", 
    }
    # print('payload data ',payload)

    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers = headers, json = payload)
    print('mpesa response ',response.text.encode('utf8'))
    response_data = response.json()
    print("M-PESA response", response_data)

    if response_data.get("ResponseCode") == "0":
        return {
            "success": True,
            "CheckoutRequestID": response_data.get("CheckoutRequestID")
        }
    else:
        return {
            "success": False,
            "error": response_data.get("errorMessage", "Payment failed")
        }