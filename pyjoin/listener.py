"""Local callback listener for Join API using Flask."""
from flask import request, Response, Flask
import requests

from .const import REGISTER_URL, PUBLIC_IP_URL, DEFAULT_PORT
from .client import get_devices

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
    def __init__(self, name, port, api_key, public_ip=None):
        self.api_key = api_key
        self.name = name
        self.port = port 
        if public_ip is None:
            self.public_ip = self.get_public_ip()
        else:
            self.public_ip = public_ip

        if port is None:
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
        self.app.add_url_rule("/push", self.name, Action(handler), methods=["POST"])

    def register(self):
        data = {
            "apikey": self.api_key,
            "regId": "{}:{}".format(self.public_ip, self.port),
            "deviceName": self.name, 
            "deviceType": 13
        }
        r = requests.post(REGISTER_URL, data=data)
        if r.status_code != 200:
            raise Exception("Unable to register to join")
        return r.json().get("deviceId")

    def get_public_ip(self):
        r = requests.get(PUBLIC_IP_URL)
        if r.status_code != 200:
            raise Exception("Unable to get public IP")
        return r.text
