from django.shortcuts import render

import os
import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse("Verification failed", status=403)

    elif request.method == 'POST':
        data = json.loads(request.body)
        try:
            messages = data["entry"][0]["changes"][0]["value"].get("messages", [])
            for message in messages:
                phone = message["from"]
                text = message["text"]["body"]
                send_message(phone, f"You said: {text}")
        except Exception as e:
            print("Error:", e)
        return HttpResponse("EVENT_RECEIVED", status=200)

@csrf_exempt
def send_message(phone, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=payload)
