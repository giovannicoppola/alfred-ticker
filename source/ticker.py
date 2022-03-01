#!/usr/bin/env python3


# Alfred-ticker, first release
# Light rain, mist 🌦   🌡️+41°F (feels +37°F, 96%) 🌬️0mph 🌒 2022-02-03 Thu 8:51AM

# removed `requests` dependency
# Tuesday, March 1, 2022  Overcast ☁️   🌡️+29°F (feels +24°F, 56%) 🌬️←4mph 🌑 


import json
import sys
import datetime 
from config import WATCHLIST, SYMBOL_UP, SYMBOL_DOWN, API_KEY
import urllib.request 
import urllib.parse 
from urllib.parse import urlencode


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


MY_TICKER = sys.argv[1]
if MY_TICKER == '':
    MY_TICKER = WATCHLIST

MYOUTPUT = {"items": []}  

url = "https://yh-finance.p.rapidapi.com/market/v2/get-quotes"

querystring = {"region":"US","symbols":MY_TICKER} #comma-separated

headers = {
    'x-rapidapi-host': "yh-finance.p.rapidapi.com",
    'x-rapidapi-key': API_KEY
    }

myURLdict = {'region': 'US', 'symbols':MY_TICKER}
qstr = urlencode(myURLdict)
url=url+"?"+qstr
#log (url)


URLrequest = urllib.request.Request(url)
URLrequest.add_header("x-rapidapi-host","yh-finance.p.rapidapi.com")
URLrequest.add_header("x-rapidapi-key",API_KEY)

with urllib.request.urlopen(URLrequest) as URLresponse: 
            myURLData = json.load(URLresponse)
            log(URLresponse.status) 
            #log(myURLData) 


myData = myURLData
zz = len (myData['quoteResponse']['result'])

for x in range(zz):
    if 'regularMarketPrice' in myData['quoteResponse']['result'][x]:
    
        currentPrice = myData['quoteResponse']['result'][x]['regularMarketPrice']
        currentPrice = '{:,.2f}'.format(currentPrice)
        
        previousClose = myData['quoteResponse']['result'][x]['regularMarketPreviousClose']
        previousClose = '{:,.2f}'.format(previousClose)
        currentPrice_ts = myData['quoteResponse']['result'][x]['regularMarketTime']
        myTS = datetime.datetime.fromtimestamp(currentPrice_ts)  
    
        myTS = myTS.strftime( "%Y-%m-%d %H:%M:%S")  
        
        shortName = myData['quoteResponse']['result'][x]['shortName']
        currency = myData['quoteResponse']['result'][x]['currency']
        t_symbol = myData['quoteResponse']['result'][x]['symbol']
        tk_change = myData['quoteResponse']['result'][x]['regularMarketChange']
        tk_change_perc = myData['quoteResponse']['result'][x]['regularMarketChangePercent']
        
        
        if tk_change > 0:
            chIcon=SYMBOL_UP
        elif tk_change < 0:
            chIcon=SYMBOL_DOWN

        tk_change = format(tk_change,'.2f')
        tk_change_perc = format(tk_change_perc,'.2f')




        MYOUTPUT["items"].append({
                "title": shortName+": $"+str(currentPrice) +" " + chIcon+" "+str(tk_change) +" ("+str(tk_change_perc)+"%)",
                "subtitle": "Updated on: "+ myTS+ " Previous close: $"+str(previousClose),

                "arg": "https://finance.yahoo.com/quote/"+t_symbol 
                })
    else:
        MYOUTPUT["items"].append({
                "title": "oops, this doesn't exist or there's no data",
                "subtitle": "",
                "icon": {
                                "path": "icons/Warning.png"
                            },

                "arg": "https://finance.yahoo.com/" 
                })
        

print (json.dumps(MYOUTPUT))
