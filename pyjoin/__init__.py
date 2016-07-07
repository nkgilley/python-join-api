"""Python API for using Join by joaoapps."""
import requests

SEND_URL = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?deviceId="
LIST_URL = "https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices?apikey="

def get_devices(api_key):
    response = requests.get(LIST_URL + api_key).json()
    if response.get('success') and not response.get('userAuthError'):
        return [(r['deviceName'], r['deviceId']) for r in response['records']]
    return False

def send_notification(device_id, text, title=None, icon=None, smallicon=None, api_key=None):
    req_url = SEND_URL + device_id + "&text=" + text
    if title: req_url += "&title=" + title
    if icon: req_url += "&icon=" + icon
    if smallicon: req_url += "&smallicon=" + smallicon
    if api_key: req_url += "&apikey=" + api_key
    requests.get(req_url)

def ring_device(device_id, api_key=None):
    req_url = SEND_URL + device_id + "&find=true" if not api_key else SEND_URL + device_id + "&find=true&apikey=" + api_key
    requests.get(req_url)

def send_url(device_id, url, title=None, text=None, api_key=None):
    req_url = SEND_URL + device_id + "&url=" + url
    if title: req_url += "&title=" + title
    req_url += "&text=" + text if text else "&text="
    if api_key: req_url += "&apikey=" + api_key
    requests.get(req_url)

def set_wallpaper(device_id, url, api_key=None):
    req_url = SEND_URL + device_id + "&wallpaper=" + url
    if api_key: req_url += "&apikey=" + api_key
    requests.get(req_url)

def send_file(device_id, url, title=None, text=None, api_key=None):
    req_url = SEND_URL + device_id + "&file=" + url
    if title: req_url += "&title=" + title
    req_url += "&text=" + text if text else "&text="
    if api_key: req_url += "&apikey=" + api_key
    requests.get(req_url)

def send_sms(device_id, sms_number, sms_text, api_key=None):
    req_url = SEND_URL + device_id + "&smsnumber=" + sms_number + "&smstext=" + sms_text
    if api_key: req_url += "&apikey=" + api_key
    requests.get(req_url)

