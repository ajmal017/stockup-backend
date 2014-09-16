import os
import time
from lib.apns import Payload, APNs
from tornado import gen

from servers import config

_here = os.path.dirname(os.path.abspath(__file__))

class ApnsSender:
    apns = APNs(use_sandbox=True,
                cert_file=os.path.join(_here, "certs/stockup_dev_cert.pem"),
                key_file=os.path.join(_here, "certs/stockup_key_nopass.pem"))
    connected = False

    @classmethod
    def connect(cls):
        ApnsSender.apns.gateway_server.connect(cls.on_connected)

    @gen.coroutine
    def send(self):
        if not ApnsSender.connected:
            return
        identifier = 1
        expiry = time.time()+3600
        token_hex = config.TEST_IPAD_TOKEN
        payload = Payload(alert="Hello World!", sound="default", badge=1)
        yield gen.Task(ApnsSender.apns.gateway_server.send_notification, identifier, expiry, token_hex, payload)
        print "Sent push message to APNS gateway."

    @classmethod
    def on_response(cls, status, seq):
        print "sent push message to APNS gateway error status %s seq %s" % (status, seq)

    @classmethod
    def on_connected(cls):
        ApnsSender.apns.gateway_server.receive_response(cls.on_response)
        cls.connected = True

apns_sender = ApnsSender()
