"""Python API for using Join by joaoapps."""
import requests

SEND_URL = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?apikey="
LIST_URL = "https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices?apikey="

def get_devices(api_key):
    response = requests.get(LIST_URL + api_key).json()
    if response.get('success') and not response.get('userAuthError'):
        return [(r['deviceName'], r['deviceId']) for r in response['records']]
    return False

def send_notification(api_key, text, device_id=None, device_ids=None, device_names=None, title=None, icon=None, smallicon=None, vibration=None, image=None, url=None, tts=None, tts_language=None, sound=None, notification_id=None, actions=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&text=" + text
    if title: req_url += "&title=" + title
    if icon: req_url += "&icon=" + icon
    if image: req_url += "&image=" + image
    if smallicon: req_url += "&smallicon=" + smallicon
    if vibration: req_url += "&vibration=" + vibration
    if url: req_url += "&url=" + url
    if tts: req_url += "&say=" + tts
    if tts_language: req_url += "&language=" + tts_language
    if sound: req_url += "&sound=" + sound
    if notification_id: req_url += "&notificationId=" + notification_id
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    if actions:
        action_strings = []
        for action in actions:
            action_str = action
            if actions[action]:
                action_str += "=:=" + "=:=".join(actions[action])
            action_strings.append(action_str)
        req_url += "&actions=" + "|||".join(action_strings)
    requests.get(req_url)

def ring_device(api_key, device_id=None, device_ids=None, device_names=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&find=true"
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    requests.get(req_url)

def send_url(api_key, url, device_id=None, device_ids=None, device_names=None, title=None, text=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&url=" + url
    if title: req_url += "&title=" + title
    req_url += "&text=" + text if text else "&text="
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    requests.get(req_url)

def set_wallpaper(api_key, url, device_id=None, device_ids=None, device_names=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&wallpaper=" + url
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    requests.get(req_url)

def send_file(api_key, url, device_id=None, device_ids=None, device_names=None, title=None, text=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&file=" + url
    if title: req_url += "&title=" + title
    req_url += "&text=" + text if text else "&text="
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    requests.get(req_url)

def send_sms(api_key, sms_number, sms_text, device_id=None, device_ids=None, device_names=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&smsnumber=" + sms_number + "&smstext=" + sms_text
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    requests.get(req_url)

