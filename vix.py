import requests
from datetime import datetime, timedelta
from scipy import interpolate
import math

from keys import quandlKey, tosKey
from access import ToS_Access

auth = ToS_Access()
auth.Access()

def riskFreeRate(days):
    """[summary]
    
    Arguments:
        days {int} -- days until option expiration. 
    
    Returns:
        [float] -- risk free rate for the diration of option expiry
    """
    today = datetime.today()+timedelta(days=-5)
    today = today.strftime('%Y-%m-%d')

    endpoint = r'https://www.quandl.com/api/v3/datasets/USTREASURY/YIELD.json?start_date={}&api_key={}'.format(today,quandlKey)

    req = requests.get(url=endpoint)
    meta = req.json()
    data = meta['dataset']

    maturity = data['column_names'][1:]
    rates = data['data'][0][1:8]
    matDays = [365/12, 365/12*2, 365/12*3, 365/12*6, 365, 365*2, 365*3] 
    
    cs = interpolate.splrep(matDays, rates)
    
    return interpolate.splev(days,cs)/100

def roundDown(value, list):
    """This can be better optimized
    
    Arguments:
        value {float} -- value to round down
        list {[str]} -- list of string numbers. Rounds down to closes number in list
    
    Returns:
        [float] -- Strike rounded down to
    """


    flts = [float(i) for i in list]
    res = []
    flts.sort()

    for val in flts:
        if value > val:
            res = val
    return res

def impVol(tick):
    auth.Access()

    option_url = r"https://api.tdameritrade.com/v1/marketdata/chains"

    start_date = datetime.now() + timedelta(days=15)
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = datetime.now() + timedelta(days=45)
    end_date = end_date.strftime("%Y-%m-%d")

    payload = {'apikey': tosKey,
                'symbol': tick,
                'optionType': 'S',
                'strikeCount': '50',
                # 'range': 'ALL',
                'fromDate': start_date,
                'toDate': end_date
                }
    
    header = {'Authorization': 'Bearer {}'.format(auth.access_tkn),
                'Content-Type': "application/json"}

    req = requests.get(url=option_url, params=payload, headers=header)
    content = req.json()

    if content['status'] != 'SUCCESS':
        Exception

    calls = content['callExpDateMap']
    puts = content['putExpDateMap']
    keys = list(calls)
    T = []
    r = []
    F = []
    K0 = []
    sig2 = []

    for key in keys:
        resTable = []

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
            r_curr = riskFreeRate(days)
            r.append(r_curr)
            #time till expiry in minutes divided by minutes in year
            T_curr = (expDate-nowDate)/60/525600
            T.append(T_curr)

            #initiate large dummy forward difference
            #initiate large dummy forward difference
            Fdiff = 10000
            #find call and put option with smallest price distance. This is your Forward
            for strike in strikes:
                call_mid = calls[key][strike][0]['mark']
                put_mid = puts[key][strike][0]['mark']
                markDiff = abs(call_mid-put_mid)
                if markDiff < Fdiff:
                    Fdiff = markDiff
                    fStrike = float(strike)
                    fcall = call_mid
                    fput = put_mid

            rt = r_curr*T_curr
            F_curr = fStrike + math.exp(rt)*(fcall-fput)
            F.append(F_curr)
            K0_curr = roundDown(F_curr, strikes)
            K0.append(K0_curr)
            markAvg = (calls[key][str(K0_curr)][0]['mark']+puts[key][str(K0_curr)][0]['mark'])/2
            resTable.append([K0_curr, markAvg])
            countNoBid = 0
            strikes.reverse()
            for strike in strikes:
                if float(strike) < K0_curr:
                    if puts[key][strike][0]['bid'] == 0:
                        countNoBid += 1
                        if countNoBid == 2:
                            break
                    else:
                        countNoBid = 0
                        resTable.append([float(strike), puts[key][strike][0]['mark']])

            strikes.reverse()
            countNoBid = 0
            for strike in strikes:
                if float(strike) > K0_curr:
                    if calls[key][strike][0]['bid'] == 0:
                        countNoBid += 1
                        if countNoBid == 2:
                            break
                    else:
                        countNoBid = 0
                        resTable.append([float(strike), calls[key][strike][0]['mark']])
            
            variance = []
            resTable = sorted(resTable)
            for i, point in enumerate(resTable):
                if i == 0:
                    deltaK = abs(resTable[i][0]-resTable[i+1][0])
                elif i == len(resTable)-1:
                    deltaK = abs(resTable[i][0]-resTable[i-1][0])
                else:
                    deltaK = abs(resTable[i+1][0]-resTable[i-1][0])/2
                a = deltaK/(point[0]**2)
                b = math.exp(r_curr*T_curr)
                contrib = a*b*point[1]
                variance.append(contrib)
            varsum = sum(variance)
            
            A = 2/T_curr*sum(variance)

            B = 1/T_curr*(F_curr/K0_curr-1)**2

            sig2.append(A-B)

    if len(sig2) == 2:
        vix = 0
        #number minutes in 30 days
        N30 = 30*1440
        #number of minutes in year
        N365 = 1440*365
        #max difference between expiries in minutes
        Ndiff = (max(T)-min(T))*N365
        #weighted average of variance
        vix = T[0]*sig2[0]*abs(T[1]*N365-N30)/Ndiff+T[1]*sig2[1]*abs(T[0]*N365-N30)/Ndiff
        vix = 100*math.sqrt(vix*N365/N30)

    elif len(sig2) == 1:
        #need to weight this if away from 30 days
        vix = 100*math.sqrt(sig2[0])
    else:
        Exception
    return(vix)


if __name__ == '__main__':

    print(impVol('XLF'))

    pass

