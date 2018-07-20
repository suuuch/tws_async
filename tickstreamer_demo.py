# coding=utf-8
import argparse
import gevent
import ibapi
import os
from ibapi.contract import Contract, ContractDetails
from ibapi.common import TickerId
from ibapi.ticktype import TickType

from tws_async import TWSClient, iswrapper, Future, AVAILABLE_TICK_TYPES, ROOT_PATH, create_timed_rotating_log


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
        self.all_contract = []
        self.log_path = os.path.join(ROOT_PATH, 'logs')

    def ContFut(self, symbol, exchange, currency):
        reqId = self.getReqId()
        contract = Future(symbol=symbol, secType='FUT+CONTFUT', exchange=exchange, currency=currency)
        self.reqContractDetails(reqId, contract)

    def subscribe(self, symbol, exchange, currency):
        self.ContFut(symbol, exchange, currency)

    @iswrapper
    def sub_mkt_data(self):
        reqId = self.getReqId()
        for contract in self.contracts:
            self._reqId2Contract[reqId] = contract
            self.reqMktData(reqId, contract, genericTickList='588', snapshot=False,
                            regulatorySnapshot=False, mktDataOptions=[])

    @iswrapper
    def connectAck(self):
        pass

    @iswrapper
    def contractDetails(self, reqId: int, contract_details: ContractDetails):
        if contract_details.summary.secType == 'CONTFUT':
            self.contracts = [
                Future(localSymbol=contract_details.summary.localSymbol,
                       exchange=contract_details.summary.exchange,
                       currency=contract_details.summary.currency,
                       symbol=contract_details.summary.symbol,
                       secType='FUT',
                       lastTradeMonth=contract_details.summary.lastTradeDateOrContractMonth
                       )
            ]

    def contractDetailsEnd(self, reqId: int):
        # pprint(self.all_contract)
        self.sub_mkt_data()
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
            # pprint(self.tick_data)

            create_timed_rotating_log(self.tick_data, self.log_path)

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
    # Create ArgumentParser() object
    parser = argparse.ArgumentParser()
    # Add argument
    parser.add_argument('--symbol', required=True, help='Futures Symbol')
    parser.add_argument('--exchange', required=True, help='Future Exchange')
    parser.add_argument('--currency', type=str, help='Currency , Default is USD', default='USD')
    parser.add_argument('--clientId', type=int, help='client id ', default=111)
    # Print usage
    parser.print_help()
    # Parse argument
    args = parser.parse_args()
    # Print args
    print(args)
    print(args.symbol)
    print(type(args.symbol))
    print(args.exchange)
    print(type(args.exchange))
    print(args.currency)
    print(type(args.currency))
    print(args.clientId)
    print(type(args.clientId))

    tws = TickStreamer()
    tws.connect(host='127.0.0.1', port=4001, clientId=args.clientId)
    tws.subscribe(args.symbol, args.exchange, args.currency)
