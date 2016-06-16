"""Python API for using Join by joaoapps."""
import requests

SEND_URL = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?deviceId="
LIST_URL = "https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices?apikey="

def get_devices(api_key):
    devices_json = requests.get(LIST_URL + api_key).json()['records']
    return [(d['deviceName'], d['deviceId']) for d in devices_json]

def send_notification(device_id, title, text, api_key=None):
    if api_key:
        requests.get(SEND_URL + device_id + "&title=" + title + "&text=" + text + "&apikey=" + api_key)
    else:
        requests.get(SEND_URL + device_id + "&title=" + title + "&text=" + text)
