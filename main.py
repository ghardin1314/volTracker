import requests
import math
from datetime import datetime,timedelta
import pytz

from access import ToS_Access
from keys import quandlKey, tosKey
from vix import impVol

auth = ToS_Access()
auth.Access()

def getSpot(tick):
    auth.Access()
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
        var.append((math.log(data[i+1]/data[i]))**2)

    realVol = 100*math.sqrt(252/n*sum(var))

    return realVol

def realtimeVol(data, days):
    R = 0
    n = days

    data = data[-n:]

    #time until end of trading day
    nwTime = datetime.now(pytz.timezone('US/Eastern'))
    endTime = nwTime.replace(hour=16, minute=0, second=0)
    if nwTime > endTime:
        endTime = endTime + timedelta(days=1)
    s = (endTime - nwTime).seconds
    var = []
    for i in range(n-1):
        var.append(math.log(data[i+1]/data[i]))

    for i, data in enumerate(var):
        if i == 0:
            R += (86400-s)/86400*data**2
        else:
            R += data**2


    realVol = 100*math.sqrt(252/n*R)
    return realVol

def getStockHist(tick):
    auth.Access()

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

    if lastdate.date() != nowdate.date() and nowdate.weekday()<5:
        last = getSpot(tick)
        close.append(last)

    return close

def realVol(tick):

    data = getStockHist(tick)
    return realtimeVol(data, 21)

def checkVols(tick):

    data = getStockHist(tick)
    days = [10,20,30]
    implied = impVol(tick)
    print ("Implied Vol: {}".format(implied))
    for day in days:
        realized = realtimeVol(data, day)
        print("{} day Realized Vol: {}".format(day, realized))
        if realized > implied:
            discount = (realized-implied)/implied*100
            print("{} day Implied Vol Discount of {}%".format(day, round(discount,2)))
        elif implied > realized:
            premium = (implied-realized)/implied*100
            print("{} day Implied Vol Premium of {}%".format(day, round(premium, 2)))

if __name__ == '__main__':

    tick = input("Enter Stock Ticker: ")

    checkVols(tick)
