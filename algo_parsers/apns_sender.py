import logging
import os
import time

from tornado import gen

import config
from lib.apns import Payload, APNs


_here = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

class ApnsSender:
    apns = APNs(use_sandbox=True,
                cert_file=os.path.join(_here, "certs/stockup_dev_cert.pem"),
                key_file=os.path.join(_here, "certs/stockup_key_nopass.pem"))
    connected = False

    @classmethod
    def connect(cls, callback=None):
        if not callback:
            callback = cls.on_connected
        ApnsSender.apns.gateway_server.connect(callback)

    @gen.coroutine
    def send(self):
        if not ApnsSender.connected:
            raise gen.Return(False)
        identifier = 1
        expiry = time.time()+3600
        token_hex = config.TEST_IPAD_TOKEN
        payload = Payload(alert="Hello World!", sound="default", badge=1)
        yield gen.Task(ApnsSender.apns.gateway_server.send_notification, identifier, expiry, token_hex, payload)
        config.debug_log(logger, "Sent push message to APNs gateway")
        raise gen.Return(True)

    @classmethod
    def on_response(cls, status, seq):
        logger.error("sent push message to APNS gateway error status %s seq %s" % (status, seq))

    @classmethod
    def on_connected(cls):
        ApnsSender.apns.gateway_server.receive_response(cls.on_response)
        cls.connected = True

apns_sender = ApnsSender()
