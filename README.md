# volTracker

This will compare implied volatility of a stock or index against its
realized volitility. Implied volatility is calulated by using the VIX
whitepaper formula found here: https://www.cboe.com/micro/vix/vixwhite.pdf

To get started you need to set up API access with Think or Swim and Quandl. To get started with ToS API, watch this video: 

https://youtu.be/qJ94sSyPGBw

Once you have created an account, make a file named 'keys.py' and
add user_name, password, and tosKey (api key). Also need to download
chrome driver to your computer. Add the path in the file as:

chromePath = r'C:\Path\to\driver'

Finally register for free quandl api here: https://www.quandl.com/sign-up. Save your api key as quandlKey. Then you should be ready to go.

Main.py currently under work. Vix.py was validated against data used
in VIX whitepaper, but needs testing under live markets.