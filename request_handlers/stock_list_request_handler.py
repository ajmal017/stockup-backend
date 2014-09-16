from tornado import gen

from request_handlers.base_request_handler import BaseRequestHandler


class StockListRequestHandler(BaseRequestHandler):

    @gen.coroutine
    def get(self):
        coll = self.db.stock_catalog
        doc = yield coll.find_one()
        self.write(doc)
