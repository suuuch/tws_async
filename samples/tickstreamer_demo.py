from pprint import pprint

import ibapi
from ibapi.contract import Contract, ContractDetails
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

    def ContFut(self, symbol, exchange):
        reqId = self.getReqId()
        contract = Future(symbol=symbol, setType='FUT+CONTFUT', exchange=exchange)
        self.reqContractDetails(reqId, contract)

    def subscribe(self, contract):
        contracts = [
            Future(localSymbol='CLQ8', exchange='NYMEX', currency='USD')
        ]
        reqId = self.getReqId()
        for contract in contracts:
            self._reqId2Contract[reqId] = contract
            self.reqMktData(reqId, contract, genericTickList='588', snapshot=False,
                            regulatorySnapshot=False, mktDataOptions=[])

    @iswrapper
    def connectAck(self):

        pass

    @iswrapper
    def contractDetails(self, reqId: int, contract_details: ContractDetails):
        print(contract_details)
        print(contract_details.summary)
        pass

    def contractDetailsEnd(self, reqId:int):
        pass

    @iswrapper
    def tickPrice(self, reqId: int,
                  tick_type: TickType,
                  price: float,
                  attrib: ibapi.common.TickAttrib):

        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)

        self.tick_data.update({type_name: price})

    @iswrapper
    def tickSize(self, reqId: int,
                 tick_type: TickType,
                 size: int):

        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)

        self.tick_data.update({type_name: size})

    @iswrapper
    def tickGeneric(self, reqId: TickerId, tick_type: TickType, value: float):
        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)
        self.tick_data.update({type_name: value})

    def tickString(self, reqId: TickerId, tick_type: TickType, value: str):
        type_name = AVAILABLE_TICK_TYPES.get(tick_type, TickType)
        self.tick_data.update({type_name: value})
        if tick_type == 45:
            contract = self._reqId2Contract[reqId]
            self.tick_data.update({'symbol': contract.symbol, 'localSymbol': contract.localSymbol})
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


if __name__ == '__main__':
    tws = TickStreamer()
    tws.connect(host='127.0.0.1', port=4001, clientId=1)
    # tws.subscribe()
    tws.ContFut('CL', 'NYMEX')
    tws.run()
