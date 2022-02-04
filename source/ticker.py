#!/usr/bin/env python3


# Alfred-ticker
# Light rain, mist 🌦   🌡️+41°F (feels +37°F, 96%) 🌬️0mph 🌒 2022-02-03 Thu 8:51AM


from lib import requests
import json
import sys
import datetime 
from config import WATCHLIST, SYMBOL_UP, SYMBOL_DOWN, API_KEY


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

response = requests.request("GET", url, headers=headers, params=querystring)

myData = response.json()
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
