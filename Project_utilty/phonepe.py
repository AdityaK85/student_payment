import datetime
import json
import random
import requests
import base64
import hashlib
from django.conf import settings
from payment.models import *


def make_base64(json_obj):
    json_str = json.dumps(json_obj, separators=(',', ':'))
    return base64.urlsafe_b64encode(bytes(json_str, "utf-8")).decode("utf-8")


def make_hash(input_str):
    m = hashlib.sha256()
    m.update(input_str.encode())
    return m.hexdigest()


def make_request_body(base64_payload):
    request_body = {
        "request": base64_payload
    }
    data_json = json.dumps(request_body)
    return data_json



def Payment( AMOUNT, REDIRECT_URL,  CALLBACK_URL, MOBILE_NUMBER):

    requests_url = f"{settings.PHONEPE_URL}/pg/v1/pay"
    payload = {
        "merchantId":settings.MERCHANT_ID,
        "merchantTransactionId":'MT8530926168102365478',
        "amount":AMOUNT ,
        "merchantUserId":"MUID123",
        "redirectUrl":REDIRECT_URL,
        "redirectMode":"REDIRECT",
        "callbackUrl": CALLBACK_URL,
        "paymentInstrument": {
            "type": "PAY_PAGE"
        },
        "mobileNumber": MOBILE_NUMBER,
    }

    base64_payload = make_base64(payload)
    verification_str = f"{base64_payload}/pg/v1/pay{settings.SALT_KEY}"
    X_VERIFY = make_hash(verification_str) + "###" + settings.SALT_INDEX
    data = make_request_body(base64_payload)

    headers = {
        "Content-Type": "application/json",
        "X-VERIFY":X_VERIFY
    }

    response = requests.post(requests_url,data=data, headers=headers)
    if response.status_code == 200:
        return [True,response.text]
    else:
        response = json.loads(response.text)
        msg = ""
        if response['code'] == "401":
            msg = "Something went wrong"
        else:
            msg = response['message']
        
            return [False,msg,response['code']]


def Payment_Request(amount,transaction_id,merchantuser_id,redirect_url,callback_url):
    
    requests_url = f"{settings.PHONEPE_URL}/pg/v1/pay" 
    merchant_id = settings.MERCHANT_ID
    salt_key = settings.SALT_KEY
    salt_index = settings.SALT_INDEX

    payload = {
        "merchantId":merchant_id,
        "merchantTransactionId":transaction_id,
        "amount":amount,
        "merchantUserId":merchantuser_id,
        "redirectUrl":redirect_url,
        "redirectMode":"POST",
        "callbackUrl":callback_url,
        "paymentInstrument": {
            "type": "PAY_PAGE"
        },
        "mobileNumber":"9860949758"
    }
    
    base64_payload = make_base64(payload)
    verification_str = f"{base64_payload}/pg/v1/pay{salt_key}"

    X_VERIFY = make_hash(verification_str) + "###" + salt_index
    
    data = make_request_body(base64_payload)

    headers = {
        "Content-Type": "application/json",
        "X-VERIFY":X_VERIFY
    }

    response = requests.post(requests_url,data=data, headers=headers)

    
    
    if response.status_code == 200:
        
        return [True,response.text]
    else:
        
        response = json.loads(response.text)
        print(response)
        msg = ""
        if response['code'] == "401":
            msg = "Something went wrong"
        else:
            msg = response['message']
        
            return [False,msg,response['code']]



def checkPhonePayStatus(transaction_id):
    
    merchant_id = settings.MERCHANT_ID
    salt_key = settings.SALT_KEY
    salt_index = settings.SALT_INDEX
    requests_url = f"{settings.PHONEPE_URL}/pg/v1/status/{merchant_id}/{transaction_id}" 

    X_VERIFY = f"/pg/v1/status/{merchant_id}/{transaction_id}{salt_key}"

    X_VERIFY = make_hash(X_VERIFY) + "###" + salt_index

    
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY":X_VERIFY,
        "X-MERCHANT-ID":merchant_id
    }

    response = requests.get(requests_url, headers=headers)
    print(response.status_code ,"--------------------")
    if response.status_code == 200:
        
        
        return [True,response.json()]
    elif response.status_code == 500:
        return [False,"Something went wrong."]
    else:
        try:
            message = response.json()['message']
        except:
            message = "Something went wrong."
        # print(response.json())
        return [False,response.json()]
