"""HTTP Client functions for Join API."""
import datetime
import json
import logging
import os
import requests

from .const import SEND_URL, LIST_URL
from .cache import _get_cache_path

_LOGGER = logging.getLogger(__name__)

def get_devices(api_key):
    """Retrieve devices from Join API, with offline caching and logging."""
    success = False
    devices = []
    
    try:
        response = requests.get(LIST_URL + api_key, timeout=10)
        response.raise_for_status()
        resp_json = response.json()
        if resp_json.get('success') and not resp_json.get('userAuthError'):
            devices = [(r['deviceName'], r['deviceId']) for r in resp_json['records']]
            success = True
        else:
            _LOGGER.error(
                "Join API returned an error (success: %s, authError: %s). Check your API key.",
                resp_json.get('success'),
                resp_json.get('userAuthError')
            )
    except Exception as err:
        _LOGGER.warning("Failed to connect to Join API: %s. Falling back to offline cache.", err)

    if success:
        cache_path = _get_cache_path(api_key)
        if cache_path:
            try:
                with open(cache_path, 'w') as fh:
                    json.dump(devices, fh)
            except Exception as err:
                _LOGGER.debug("Failed to write to offline cache: %s", err)
        return devices
    else:
        cache_path = _get_cache_path(api_key)
        if cache_path and os.path.isfile(cache_path):
            try:
                mtime = os.path.getmtime(cache_path)
                cache_time = datetime.datetime.fromtimestamp(mtime)
                cache_age = datetime.datetime.now() - cache_time
                _LOGGER.warning(
                    "Loading offline cached devices. (Cache file was last updated %d days ago at %s)",
                    cache_age.days,
                    cache_time.strftime('%Y-%m-%d %H:%M:%S')
                )
                with open(cache_path, 'r') as fh:
                    return json.load(fh)
            except Exception as err:
                _LOGGER.error("Failed to read from offline cache: %s", err)
        
        _LOGGER.critical("Join API call failed and no offline cache is available.")
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
