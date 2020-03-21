import requests
import math
from datetime import datetime,timedelta

from access import ToS_Access
from keys import quandlKey, tosKey
from vix import impVol

auth = ToS_Access()
auth.Access()

def getSpot(tick):
        header = {'Authorization': 'Bearer {}'.format(auth.access_tkn),
            'Content-Type': "application/json"}
        endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format(tick)
        payload = {'apikey': tosKey}
        req1 = requests.get(url=endpoint, params=payload, headers=header)
        quote = req1.json()
        last = quote[tick]['lastPrice']
        return last

def realizedVol(data):

    var = []
    n = len(data)-1

    for i in range(n):
        var.append(math.log(data[i+1]/data[i]))

    realVol = 100*math.sqrt(252/n*sum(var)**2)

    return realVol

def getStockHist(tick):

    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(tick)

    payload = {
        'apikey': tosKey,
        'period': str(6),
        'periodType': 'month',
        'frequecy': str(1),
        'frequencyType': 'daily'
    }
    header = {'Authorization': 'Bearer {}'.format(auth.access_tkn),
            'Content-Type': "application/json"}

    req = requests.get(url=endpoint, params=payload, headers=header)
    content = req.json()

    close = []

    for day in content['candles']:
        close.append(day['close'])

    lastdate = content['candles'][-1]['datetime']

    #converts from LA to NY time. Daily candles updated at 1AM NY time
    lastdate = datetime.fromtimestamp(lastdate/1000)+timedelta(hours=3)
    nowdate = datetime.now()+timedelta(hours=3)

    if lastdate.date() != nowdate.date():
        last = getSpot(tick)
        close.append(last)

    return close

def realVol(tick):

    data = getStockHist(tick)
    return realizedVol(data)

if __name__ == '__main__':

    tick = input("Enter Stock Ticker: ")

    realized = realVol(tick)
    print("Realized Vol: {}".format(realized))
    implied = impVol(tick)
    print ("Implied Vol: {}".format(implied))

    if realized > implied:
        discount = (realized-implied)/implied*100
        print("Implied Vol Discount of {}%".format(round(discount,2)))
    elif implied > realized:
        premium = (implied-realized)/implied*100
        print("Implied Vol Premium of {}%".format(round(premium, 2)))
