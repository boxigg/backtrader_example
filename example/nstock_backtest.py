# -*- coding: utf-8 -*-
# N stocks backtest


"""
MIT License

Copyright (c) 2018 MsLPrime

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import datetime as dt
import pandas as pd
import backtrader as bt
import tushare as ts


class ManmStrategy(bt.Strategy):
    params = (('n', 10), ('m', 20), ('codes', []))

    def __init__(self):
        super(ManmStrategy, self).__init__()
        self.positions_code = []
        self.man = []
        self.mam = []
        for each, eachdata in enumerate(self.datas):
            man = bt.indicators.MovingAverageSimple(eachdata.close, period=self.params.n)
            mam = bt.indicators.MovingAverageSimple(eachdata.close, period=self.params.m)  # plot=False(ctrl plot or not)
            self.man.append(man)
            self.mam.append(mam)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # # if want to find stock
        # ind = self.params.codes.index('000001.SZ')  # get index, then do what you want
        # data = self.datas[ind]

        for each, eachdata in enumerate(self.datas):
            code = eachdata._name
            if code == benchmark:
                continue
            pos = self.getposition(eachdata)
            # print(code, pos)
            if not pos.size:  # no market / no orders
                if self.man[each][0] > self.mam[each][0]:
                    self.buy(data=eachdata, size=5000)
            else:
                if self.man[each][0] < self.mam[each][0]:
                    self.sell(data=eachdata, size=5000)

    def stop(self):
        pass


if __name__ == '__main__':
    codes = ['000001.SZ', '603999.SH', '600000.SH']  # or set() -> list()
    benchmark = '000300.SH'
    inital_cash = 1e5
    begt = dt.datetime(2016, 1, 1)
    endt = dt.datetime(2018, 1, 1)

    cerebro = bt.Cerebro()
    # cerebro.addsizer(bt.sizers.FixedSize, stake=1000)  # 默认买入一手
    cerebro.broker.setcash(inital_cash)  # 初始资金
    cerebro.addstrategy(ManmStrategy, codes=codes)
    # Add Analyzer
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    # Feed Data
    for each, code in enumerate(codes):
        tohlcva = ts.get_k_data(code.split('.')[0],
                                start=str(begt.date()),
                                end=str(endt.date()),
                                autype='qfq')
        tohlcva.drop('code', axis=1, inplace=True)
        tohlcva['date'] = pd.to_datetime(tohlcva['date'])
        tohlcva.set_index('date', inplace=True)
        tohlcva = tohlcva[['open', 'high', 'low', 'close', 'volume']]
        tohlcva['openinterest'] = 0.0
        # print(tohlcva.head(10))
        data = bt.feeds.PandasData(dataname=tohlcva, fromdate=begt, todate=endt, plot=False)
        cerebro.adddata(data, name=code)
    # set benchmark
    tohlcva = ts.get_k_data(benchmark.split('.')[0],
                            start=str(begt.date()),
                            end=str(endt.date()),
                            index=True)
    tohlcva.drop('code', axis=1, inplace=True)
    tohlcva['date'] = pd.to_datetime(tohlcva['date'])
    tohlcva.set_index('date', inplace=True)
    tohlcva = tohlcva[['open', 'high', 'low', 'close', 'volume']]
    tohlcva['openinterest'] = 0.0
    data = bt.feeds.PandasData(dataname=tohlcva, fromdate=begt, todate=endt, plot=False)  # not plot benchmark
    cerebro.adddata(data, name=benchmark)
    cerebro.addobserver(bt.observers.Benchmark,
                        data=data,
                        timeframe=bt.TimeFrame.NoTimeFrame)
    # cerebro.addobserver(bt.observers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
    # cerebro.addanalyzer(bt.analyzers.TimeReturn,
    #                     timeframe=bt.TimeFrame.NoTimeFrame,
    #                     data=data,
    #                     _name='timereturns')
    cerebro.run()
    cerebro.plot()
