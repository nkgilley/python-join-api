"""Python API for using Join by joaoapps."""
import hashlib
import json
import os
import tempfile
import requests
from flask import request, Response, Flask 

SEND_URL = "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?apikey="
LIST_URL = "https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/listDevices?apikey="
REGISTER_URL = "https://joinjoaomgcd.appspot.com/_ah/api/registration/v1/registerDevice/"
PUBLIC_IP_URL = "https://api.ipify.org"
DEFAULT_PORT = "1820"


class Action(object):

        def __init__(self, action):
            self.action = action
            self.response = Response(status=200, headers={"Content-Type": "text/html"})

        def __call__(self, *args):
            data = request.json
            if self.action:
                self.action(data)
            return self.response

class Listener:
    def __init__(self, name, port, api_key,public_ip=None):
        self.api_key = api_key
        self.name = name
        self.port = port 
        if public_ip == None:
            self.public_ip = self.get_public_ip()
        else:
            self.public_ip = public_ip

        if port == None:
            self.port = DEFAULT_PORT
        else:
            self.port = port

        self.deviceID = self.get_device_id()
        self.app = Flask(self.name)

    def get_device_id(self):
        devices = get_devices(self.api_key)
        for d in devices:
            name, id = d
            if name == self.name:
                return id
        return self.register() 

    def run(self):
        self.app.run(host="0.0.0.0", port=self.port, debug=False, use_reloader=False)

    def add_callback(self, handler=None):
        self.app.add_url_rule("/push", self.name, Action(handler),methods=["POST"])

    def register(self):
        data = {
            "apikey": self.api_key,
            "regId": "{}:{}".format(self.public_ip,self.port),
            "deviceName": self.name, 
            "deviceType": 13
        }
        r = requests.post(REGISTER_URL, data = data)
        if r.status_code!=200:
            raise Exception("Unable to register to join")
        return r.json().get("deviceId")

    def get_public_ip(self):
        r = requests.get(PUBLIC_IP_URL)
        if r.status_code !=200:
            raise Exception("Unable to get public IP")
        return r.text
    
def _get_cache_path(api_key):
    """Generate a safe cache file path based on a hashed API key."""
    try:
        hashed_key = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    except Exception:
        return None

    # Try standard user cache directory first, fall back to system temp
    for base in [
        os.path.join(os.path.expanduser("~"), ".cache", "pyjoin"),
        os.path.join(tempfile.gettempdir(), "pyjoin")
    ]:
        try:
            os.makedirs(base, exist_ok=True)
            # Verify write permissions
            test_path = os.path.join(base, ".write_test")
            with open(test_path, "w") as f:
                f.write("")
            os.remove(test_path)
            return os.path.join(base, f"{hashed_key}.json")
        except Exception:
            continue
    return None


def get_devices(api_key):
    """Retrieve devices from Join API, with robust offline caching support."""
    success = False
    devices = []
    
    try:
        # Wrap the API call and JSON parsing to handle network outages gracefully
        response = requests.get(LIST_URL + api_key, timeout=10)
        response.raise_for_status()
        resp_json = response.json()
        if resp_json.get('success') and not resp_json.get('userAuthError'):
            devices = [(r['deviceName'], r['deviceId']) for r in resp_json['records']]
            success = True
    except Exception:
        # Network outage, timeout, or server error encountered
        pass

    if success:
        # Successfully fetched from API; update cache
        cache_path = _get_cache_path(api_key)
        if cache_path:
            try:
                with open(cache_path, 'w') as fh:
                    json.dump(devices, fh)
            except Exception:
                # Fail silently if cache is unwritable to avoid disrupting normal API operations
                pass
        return devices
    else:
        # Fetch failed; try loading from offline cache
        cache_path = _get_cache_path(api_key)
        if cache_path and os.path.isfile(cache_path):
            try:
                with open(cache_path, 'r') as fh:
                    return json.load(fh)
            except Exception:
                pass
        return False

def send_notification(api_key, text, device_id=None, device_ids=None, device_names=None, title=None, icon=None, smallicon=None, vibration=None, image=None, url=None, tts=None, tts_language=None, sound=None, notification_id=None, category=None, actions=None):
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
    if category: req_url += "&category=" + category
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

def set_mediavolume(api_key, mediavolume, device_id=None, device_ids=None, device_names=None):
    if device_id is None and device_ids is None and device_names is None: return False
    req_url = SEND_URL + api_key + "&mediaVolume=" + mediavolume
    if device_id: req_url += "&deviceId=" + device_id
    if device_ids: req_url += "&deviceIds=" + device_ids
    if device_names: req_url += "&deviceNames=" + device_names
    requests.get(req_url)
