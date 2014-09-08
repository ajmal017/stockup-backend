import logging
import sys
import motor
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop, PeriodicCallback

AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')
logging.basicConfig(filename='../log',level=logging.INFO)

logger = logging.getLogger(__name__)

db = motor.MotorClient().ss

def inserted(result, error):
    if error:
        logger.error(error)
    else:
        pass


def insert_stock_info(stock_info):
    pass


def handle_request(response):
    if response.error:
        logger.error(response.error)
    else:
        stock_vars = response.body.decode(encoding='GB18030', errors='strict')
        for var in stock_vars.strip().split('\n'):
            info = var.split('"')
            try:
                print info[1].split(',')
                insert_stock_info()

            except Exception:
                logger.error(sys.exc_info()[0])


def fetch_stock_info():
    http_client = AsyncHTTPClient()
    ## TODO: parse stocks_all.txt
    http_client.fetch('http://hq.sinajs.cn?list=sh600037,sh600039,0000,sh600052', handle_request)


def main():
    PeriodicCallback(fetch_stock_info, 2000).start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()