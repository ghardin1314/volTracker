import requests
import math
from datetime import datetime,timedelta
import pytz

from access import ToS_Access

from ToSlogin import api_key

def getSpot(tick):
        header = {'Authorization': 'Bearer {}'.format(auth.access_tkn),
            'Content-Type': "application/json"}
        endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format(tick)
        payload = {'apikey': api_key}
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
        'apikey': api_key,
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
    
def getImpVol(tick):

    spot = getSpot(tick)

    option_url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    start_date = datetime.now() + timedelta(days=15)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = datetime.now() + timedelta(days=45)
    end_date = end_date.strftime("%Y-%m-%d")

    payload = {'apikey': api_key,
                'symbol': 'XLF',
                'optionType': 'S',
                'strikeCount': 2,
                'fromDate': start_date,
                'toDate': end_date
                }
    
    header = {'Authorization': 'Bearer {}'.format(auth.access_tkn),
                'Content-Type': "application/json"}

    req = requests.get(url=option_url, params=payload, headers=header)
    content = req.json()
    calls = content['callExpDateMap']
    puts = content['putExpDateMap']

    keys = list(calls)
    vols = []
    vp = []
    dwVol = []

    for key in keys:

        strikes = list(calls[key])
        test = calls[key][strikes[0]]

        #gets rid of weekly options
        if calls[key][strikes[0]][0]['expirationType'] != 'R':
            calls.pop(key)
            puts.pop(key)
        else:
            vols = []
            weights = []
            for strike in strikes:
                strikeVol = calls[key][strike][0]['volatility']


            #     strikeVol = calls[key][strike][0]['volatility']
            #     # days = calls[key][strike][0]['daysToExpiration']
            #     weight = 1/abs(float(strike)-spot)
            #     wVol = strikeVol*weight
            #     vols.append(wVol)
            #     weights.append(weight)


            #     strikeVol = puts[key][strike][0]['volatility']
            #     days = puts[key][strike][0]['daysToExpiration']
            #     weight = 1/abs(float(strike)-spot)
            #     wVol = strikeVol*weight
            #     vols.append(wVol)
            #     weights.append(weight)
            # strike_avg = sum(vols)/sum(weights)
            # vp.append(strike_avg)
            # days = calls[key][strike][0]['daysToExpiration']
            # day_weight.append[days]
            # dwVol.append(strike_avg*days)

    # ImpVol = sum(vp)/sum(day_weight)

    return


if __name__ == '__main__':
    auth = ToS_Access()
    auth.Access()

    test = getStockHist("XLF")
    var = realizedVol(test)

    getImpVol("XLF")

    # option_url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    # payload = {'apikey': api_key,
    #             'symbol': 'XLF',
    #             'optionType': 'S',
    #             'strikeCount': 5
    #             }
    
    # header = {'Authorization': 'Bearer {}'.format(auth.access_tkn),
    #             'Content-Type': "application/json"}

    # req = requests.get(url=option_url, params=payload, headers=header)
    # content = req.json()
    # print(content)



