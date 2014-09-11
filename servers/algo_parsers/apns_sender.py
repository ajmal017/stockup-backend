import time

from lib.apns import APNs, Payload
from tornado import ioloop

import config


apns = APNs(use_sandbox=True)


apns = APNs(use_sandbox=True, cert_file="certs/stockup_dev_cert.pem", key_file="certs/stockup_key_nopass.pem")

def success():
    print("Sent push message to APNS gateway.")
    ioloop.IOLoop.instance().stop()

def send():
    identifier = 1
    expiry = time.time()+3600
    token_hex = config.TEST_IPAD_TOKEN
    payload = Payload(alert="Hello World!", sound="default", badge=1)
    apns.gateway_server.send_notification(identifier, expiry, token_hex, payload, success)

def on_response(status, seq):
    print "sent push message to APNS gateway error status %s seq %s" % (status, seq)

def on_connected():
    apns.gateway_server.receive_response(on_response)

# Connect the apns
apns.gateway_server.connect(on_connected)

# Wait for the connection and send a notification
ioloop.IOLoop.instance().add_timeout(time.time()+5, send)


print "here"