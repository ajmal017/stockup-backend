from datetime import datetime
from tornado import gen
from base_request_handler import BaseRequestHandler


class PriceRequestHandler(BaseRequestHandler):

    def initialize(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Cache-Control', 'no-cache, must-revalidate')

    @gen.coroutine
    def get(self):
        """
        :arg:
            start_time: the start time of the query in ISO 8601 format without timezone
            end_time: the end time of the query in the same format
            stock_ids: list of comma separated stock_id to be queried

        :return:
        """
        start_time_raw = self.get_argument('start_time', None)
        end_time_raw = self.get_argument('end_time', None)
        ids_raw = self.get_argument('stock_ids', None)
        if not (start_time_raw and end_time_raw and ids_raw):
            self.write({'arguments': ['start_time', 'end_time', 'stock_ids']})
            return

        stock_ids = map(lambda x: int(x), ids_raw.split(','))

        start_time = datetime.strptime(start_time_raw, self.datetime_repr)
        end_time = datetime.strptime(end_time_raw, self.datetime_repr)

        query = {
            '_id.c': {
                '$in': stock_ids
            },
            '$and':
            [
                {'_id.d': {'$gte': start_time}},
                {'_id.d': {'$lte': end_time}}
            ]
        }

        cursor = self.db.stocks.find(query)

        self.write('[')
        for document in (yield cursor.to_list(length=100)):
            del document['_id']['d']
            self.write({'doc': document})
            self.write(',')
        self.write(']')