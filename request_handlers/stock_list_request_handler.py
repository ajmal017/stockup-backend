from tornado import gen
from config import get_db

from request_handlers.base_request_handler import BaseRequestHandler


class StockListRequestHandler(BaseRequestHandler):

    @gen.coroutine
    def get(self):
        coll = get_db().stock_catalog
        doc = yield coll.find_one()
        self.write(doc)
