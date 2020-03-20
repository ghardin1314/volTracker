import requests
from datetime import datetime, timedelta
from scipy import interpolate

from keys import quandlKey, tosKey
from access import ToS_Access

auth = ToS_Access()
auth.Access()

def riskFreeRate(days):
    today = datetime.today()
    today = today.strftime('%Y-%m-%d')

    endpoint = r'https://www.quandl.com/api/v3/datasets/USTREASURY/YIELD.json?start_date={}&end_date={}&api_key={}'.format(today,today,quandlKey)

    req = requests.get(url=endpoint)
    meta = req.json()
    data = meta['dataset']

    maturity = data['column_names'][1:]
    rates = data['data'][0][1:8]
    matDays = [365/12, 365/12*2, 365/12*3, 365/12*6, 365, 365*2, 365*3] 
    
    cs = interpolate.splrep(matDays, rates)
    
    return interpolate.splev(days,cs)/100

def vix(tick):

    option_url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    start_date = datetime.now() + timedelta(days=15)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = datetime.now() + timedelta(days=45)
    end_date = end_date.strftime("%Y-%m-%d")

    payload = {'apikey': tosKey,
                'symbol': 'XLF',
                'optionType': 'S',
                'strikeCount': 10,
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
    T = []
    r = []
    F = []

    for key in keys:

        strikes = list(calls[key])

        #gets rid of weekly options
        if calls[key][strikes[0]][0]['expirationType'] != 'R':
            calls.pop(key)
            puts.pop(key)

        else:
            expDate = calls[key][strikes[0]][0]['expirationDate']/1000-6.5*3600
            nowDate = datetime.now().timestamp()
            days = calls[key][strikes[0]][0]['daysToExpiration']
            #get risk free rate
            r.append(riskFreeRate(days))
            #time till expiry in minutes divided by minutes in year
            T.append((expDate-nowDate)/60/525600)
    
    pass


if __name__ == '__main__':

    vix('XLK')

    pass

