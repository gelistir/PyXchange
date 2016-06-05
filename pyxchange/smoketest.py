#!/usr/bin/env python2.7

import unittest

import server
import engine

from test_utils import *


class JsonTest(unittest.TestCase):
    py, json = { 'key': None }, '{"key": null}'

    def testLoads(self):
        """ Test JSON loads """

        assert engine.json_loads('true')  is True
        assert engine.json_loads('false') is False
        assert engine.json_loads('null')  is None
        assert engine.json_loads(self.json) == self.py

        with self.assertRaises(TypeError):
            assert engine.json_loads(None)


    def testDumps(self):
        """ Test JSON dumps """

        assert engine.json_dumps(True)  == 'true'
        assert engine.json_dumps(False) == 'false'
        assert engine.json_dumps(None)  == 'null'
        assert engine.json_dumps(self.py) == self.json

        with self.assertRaises(TypeError):
            assert engine.json_dumps(object)


class MatcherTest(unittest.TestCase):
    def setUp(self):
        """ Create matcher, one trader and one client (market data) """

        self.matcher = engine.Matcher()

        self.client1 = ClientPair.create('client-1', self.matcher)
        self.trader1 = TraderPair.create('trader-1', self.matcher)


    def tearDown(self):
        """ Remove client and trader from the matcher """

        self.matcher.removeClient(self.client1.client)

        if self.trader1:
            self.matcher.removeTrader(self.trader1.trader)


    def testTypeError(self):
        """ Test handling of non-dict data """

        self.matcher.handleMessageStr(self.trader1.trader, 'null')
        self.trader1.transport.assertDisconnected()


    def testUnknownMessage(self):
        """ Test handling of unknown message """

        self.matcher.handleMessageDict(self.trader1.trader, { u'message': u'test' })
        self.trader1.transport.assertMessage({u'text': u'unknown message', u'message': u'error'})


    def testInvalidMessage(self):
        """ Test handling of bogus messages and invalid values """

        # wrong order id
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 0, u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong order id', u'message': u'error'})

        # wrong type of order id (TypeError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': None, u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong order id', u'message': u'error'})

        # missing order id (KeyError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong order id', u'message': u'error'})

        # wrong price
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 0, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong price', u'message': u'error'})

        # wront type of price (TypeError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': None, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong price', u'message': u'error'})

        # missing price (KeyError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong price', u'message': u'error'})

        # wrong quantity
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'quantity': 0, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong quantity', u'message': u'error'})

        # wrong type of quantity (TypeError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'quantity': None, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong quantity', u'message': u'error'})

        # missing quantity (KeyError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong quantity', u'message': u'error'})

        # wrong type of side (TypeError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': None })
        self.trader1.transport.assertMessage({u'text': u'order has wrong side', u'message': u'error'})

        # missing side (KeyError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'quantity': 1, u'message': u'createOrder' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong side', u'message': u'error'})

        # wrong order id
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 0, u'message': u'cancelOrder' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong order id', u'message': u'error'})

        # wrong type of order id (TypeError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': None, u'message': u'cancelOrder' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong order id', u'message': u'error'})

        # missing order id (KeyError)
        self.matcher.handleMessageDict(self.trader1.trader, { u'message': u'cancelOrder' })
        self.trader1.transport.assertMessage({u'text': u'order has wrong order id', u'message': u'error'})


    def testCreateCancelOrder(self):
        """ Test create/cancel order """

        # create bid order
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({ u'report': u'NEW', u'orderId': 1, u'quantity': 1, u'message': u'executionReport' })

        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 2, u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({ u'report': u'NEW', u'orderId': 2, u'quantity': 1, u'message': u'executionReport' })

        self.client1.transport.assertMessage({ u'type': u'orderbook', u'side': u'bid', u'price': 1, 'quantity': 1})
        self.client1.transport.assertMessage({ u'type': u'orderbook', u'side': u'bid', u'price': 1, 'quantity': 2})

        # insert existing order
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 1, u'quantity': 1, u'message': u'createOrder', u'side': u'BUY' })
        self.trader1.transport.assertMessage({u'text': u'order already exists', u'message': u'error'})

        # cancel order
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'message': u'cancelOrder' })
        self.trader1.transport.assertMessage({ u'orderId': 1, u'message': u'executionReport', 'report': u'CANCELED', u'quantity': 1 })
        self.client1.transport.assertMessage({ u'type': u'orderbook', u'side': u'bid', u'price': 1, 'quantity': 1})

        # cancel nonexistent order
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'message': u'cancelOrder' })
        self.trader1.transport.assertMessage({ u'text': u'order does not exists', u'message': u'error' })

        # test orders are removed when trader disconnects
        self.matcher.removeTrader(self.trader1.trader)
        self.trader1 = None

        self.client1.transport.assertMessage({u'price': 1, u'type': u'orderbook', u'side': u'bid', u'quantity': 0})


class TradingTest(unittest.TestCase):
    def setUp(self):
        self.matcher = engine.Matcher()

        self.client1 = ClientPair.create('client-1', self.matcher)
        self.trader1 = TraderPair.create('trader-1', self.matcher)
        self.trader2 = TraderPair.create('trader-2', self.matcher)

        # enter some bid orders
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 1, u'price': 10, u'quantity': 10, u'message': u'createOrder', u'side': u'BUY' })
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 2, u'price': 20, u'quantity': 10, u'message': u'createOrder', u'side': u'BUY' })
        self.matcher.handleMessageDict(self.trader1.trader, { u'orderId': 3, u'price': 30, u'quantity': 10, u'message': u'createOrder', u'side': u'BUY' })

        # enter some ask orders
        self.matcher.handleMessageDict(self.trader2.trader, { u'orderId': 1, u'price': 40, u'quantity': 10, u'message': u'createOrder', u'side': u'SELL' })
        self.matcher.handleMessageDict(self.trader2.trader, { u'orderId': 2, u'price': 50, u'quantity': 10, u'message': u'createOrder', u'side': u'SELL' })
        self.matcher.handleMessageDict(self.trader2.trader, { u'orderId': 3, u'price': 60, u'quantity': 10, u'message': u'createOrder', u'side': u'SELL' })

        # clear messages received until now
        self.client1.transport.clear()
        self.trader1.transport.clear()
        self.trader2.transport.clear()


    def tearDown(self):
        self.matcher.removeClient(self.client1.client)
        self.matcher.removeTrader(self.trader1.trader)
        self.matcher.removeTrader(self.trader2.trader)


    def testTrade(self):
        self.matcher.handleMessageDict(self.trader2.trader, { u'orderId': 4, u'price': 15, u'quantity': 25, u'message': u'createOrder', u'side': u'SELL' })

        self.trader1.transport.assertMessage({u'report': u'FILL', u'orderId': 3, u'message': u'executionReport', u'price': 30, u'quantity': 10})
        self.trader2.transport.assertMessage({u'report': u'FILL', u'orderId': 4, u'message': u'executionReport', u'price': 30, u'quantity': 10})
        self.client1.transport.assertMessage({u'price': 30, u'time': 0, u'type': u'trade', u'quantity': 10})

        self.trader1.transport.assertMessage({u'report': u'FILL', u'orderId': 2, u'message': u'executionReport', u'price': 20, u'quantity': 10})
        self.trader2.transport.assertMessage({u'report': u'FILL', u'orderId': 4, u'message': u'executionReport', u'price': 20, u'quantity': 10})
        self.client1.transport.assertMessage({u'price': 20, u'time': 0, u'type': u'trade', u'quantity': 10})

        # remaining quantity of order 4 is inserted to orderbook
        self.trader2.transport.assertMessage({u'report': u'NEW', u'orderId': 4, u'message': u'executionReport', u'quantity': 5})

        self.client1.transport.assertMessage({u'price': 30, u'type': u'orderbook', u'side': u'bid', u'quantity': 0})
        self.client1.transport.assertMessage({u'price': 20, u'type': u'orderbook', u'side': u'bid', u'quantity': 0})
        self.client1.transport.assertMessage({u'price': 15, u'type': u'orderbook', u'side': u'ask', u'quantity': 5})


    def testSelfMatch(self):
        # self-match protection
        self.matcher.handleMessageDict(self.trader2.trader, { u'orderId': 4, u'price': 40, u'quantity': 10, u'message': u'createOrder', u'side': u'BUY' })
        self.trader2.transport.assertMessage({u'text': u'self-match rejected', u'message': u'error'})


if __name__ == '__main__':
    unittest.main()


# EOF

