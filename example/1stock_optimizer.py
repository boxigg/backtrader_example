# -*- coding: utf-8 -*-
# one stock optimizer


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
    params = (('n', 10), ('m', 20))

    def __init__(self):
        super(ManmStrategy, self).__init__()
        self.dataclose = self.datas[0].close
        self.man = bt.indicators.MovingAverageSimple(self.dataclose, period=self.params.n)
        self.mam = bt.indicators.MovingAverageSimple(self.dataclose, period=self.params.m)

    def next(self):
        if not self.position:
            if self.man[0] > self.mam[0]:
                self.order = self.buy()  # default buy at next day open
        else:
            if self.man[0] < self.mam[0]:
                self.order = self.close()  # close


if __name__ == '__main__':
    code = '000001.SZ'
    inital_cash = 1e5
    begt = dt.datetime(2013, 1, 1)
    endt = dt.datetime(2018, 1, 1)

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(inital_cash)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
    # cerebro.addstrategy(ManmStrategy)
    cerebro.optstrategy(ManmStrategy, n=range(10, 15))
    # Add Analyzer
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns', tann=252)  # set bt.analyzers.Returns()' params
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    # Feed Data
    tohlcva = ts.get_k_data(code.split('.')[0],
                            start=str(begt.date()),
                            end=str(endt.date()),
                            autype='qfq')
    tohlcva.drop('code', axis=1, inplace=True)
    tohlcva['date'] = pd.to_datetime(tohlcva['date'])
    tohlcva.set_index('date', inplace=True)
    tohlcva = tohlcva[['open', 'high', 'low', 'close', 'volume']]
    tohlcva['openinterest'] = 0.0
    data = bt.feeds.PandasData(dataname=tohlcva, fromdate=begt, todate=endt)
    cerebro.adddata(data)

    res = cerebro.run()  # return list
    for eachres in res:
        print('params: ', eachres[0].params.n, eachres[0].params.m)
        print('returns: ', eachres[0].analyzers.returns.get_analysis())
        print('drawdown: ', eachres[0].analyzers.drawdown.get_analysis())
        print('------')
    # cerebro.plot()
