from pprint import pprint

import ibapi
from ibapi.contract import Contract
from ibapi.common import TickerId
from ibapi.ticktype import TickType

from tws_async import TWSClient, iswrapper, Future, AVAILABLE_TICK_TYPES, ROOT_PATH


class TickStreamer(TWSClient):
    """
    Get live streaming tick data from TWS or gateway server.
    """

    def __init__(self):
        TWSClient.__init__(self)
        self.accountName = ''
        self._reqIdSeq = 0
        self._reqId2Contract = {}
        self.tick_data = {}

    def subscribe(self):
        contracts = [
            Future(localSymbol='CLQ8', exchange='NYMEX', currency='USD')
        ]
        for contract in contracts:
            reqId = self.getReqId()
            self._reqId2Contract[reqId] = contract
            self.reqMktData(reqId, contract, genericTickList='588', snapshot=False,
                            regulatorySnapshot=False, mktDataOptions=[])

    @iswrapper
    def connectAck(self):
        # self.reqAccountUpdates(1, '')
        # self.reqOpenOrders()
        # self.reqPositions()
        pass

    @iswrapper
    def tickPrice(self, reqId: int,
                  tick_type: TickType,
                  price: float,
                  attrib: ibapi.common.TickAttrib):
        contract = self._reqId2Contract[reqId]
        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)
        # print('{} {} price {}'.format(contract.symbol,type_name, price))
        self.tick_data.update({type_name: price})

    @iswrapper
    def tickSize(self, reqId: int,
                 tick_type: TickType,
                 size: int):
        contract = self._reqId2Contract[reqId]
        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)
        # print('{} {} size {}'.format(contract.symbol, type_name,size))
        self.tick_data.update({type_name: size})

    @iswrapper
    def tickGeneric(self, reqId: TickerId, tick_type: TickType, value: float):
        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)
        # print(tick_type,type_name,value)
        self.tick_data.update({type_name: value})
        pass

    def tickString(self, reqId: TickerId, tick_type: TickType, value: str):
        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)
        # print(tick_type,type_name,value)
        self.tick_data.update({type_name: value})
        if tick_type == 45:
            pprint(self.tick_data)

    @iswrapper
    def updateAccountTime(self, timeStamp: str):
        print('Time {}'.format(timeStamp))

    @iswrapper
    def accountDownloadEnd(self, accountName: str):
        self.accountName = accountName

    @iswrapper
    def updateAccountValue(self, key: str, val: str, currency: str,
                           accountName: str):
        print('Account update: {} = {} {}'.format(key, val, currency))

    @iswrapper
    def position(self, account: str,
                 contract: Contract,
                 position: float,
                 avgCost: float):
        print('Position: {} {} @ {}'.format(position, contract.symbol, avgCost))

    @iswrapper
    def positionEnd(self):
        pass


tws = TickStreamer()
tws.connect(host='127.0.0.1', port=4001, clientId=1)
tws.subscribe()
tws.run()
