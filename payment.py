import json
from telegram import LabeledPrice


def vip_price(language):
    with open('json/messages.json') as json_data:
        js_data = json.load(json_data)
    label = js_data['messages'][language]['VIP_status']
    price_vip = LabeledPrice(label=label, amount=js_data['payments']['VIP'])
    return price_vip
