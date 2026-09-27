#!/usr/bin/env python3


# Alfred-ticker, first release
# Light rain, mist 🌦   🌡️+41°F (feels +37°F, 96%) 🌬️0mph 🌒 2022-02-03 Thu 8:51AM

# removed `requests` dependency
# Tuesday, March 1, 2022  Overcast ☁️   🌡️+29°F (feels +24°F, 56%) 🌬️←4mph 🌑 

# 1.1: switched from RapidAPI yh-finance (dead) to Yahoo's keyless chart endpoint
# Sunday, September 27, 2026


import json
import sys
import datetime
from concurrent.futures import ThreadPoolExecutor
from config import WATCHLIST, SYMBOL_UP, SYMBOL_DOWN
import urllib.request
import urllib.error
from urllib.parse import quote as urlquote


CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1d&interval=1d"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def emit(items):
    print(json.dumps({"items": items}))


def fetch_quote(symbol):
    """Return the chart `meta` dict for a symbol, None if Yahoo has no data, or raise on network errors."""
    URLrequest = urllib.request.Request(CHART_URL.format(urlquote(symbol)))
    URLrequest.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(URLrequest, timeout=10) as URLresponse:
            myURLData = json.load(URLresponse)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise
    results = (myURLData.get('chart') or {}).get('result') or []
    return results[0].get('meta') if results else None


def format_price(value, currency):
    price = '{:,.2f}'.format(value)
    return "$" + price if currency in ('USD', '', None) else price + " " + currency


MY_TICKER = sys.argv[1] if len(sys.argv) > 1 else ''
if MY_TICKER == '':
    MY_TICKER = WATCHLIST

symbols = [s.strip().upper() for s in MY_TICKER.split(',') if s.strip()]
if not symbols:
    emit([{
        "title": "No ticker to look up",
        "subtitle": "Type a symbol, or set WATCHLIST in workflow config",
        "valid": False,
    }])
    sys.exit(0)

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(fetch_quote, s) for s in symbols]

MYOUTPUT = {"items": []}

for symbol, future in zip(symbols, futures):
    try:
        quote = future.result()
    except urllib.error.HTTPError as err:
        log(f"{symbol}: HTTP {err.code}")
        MYOUTPUT["items"].append({
            "title": f"{symbol}: Yahoo Finance error ({err.code})",
            "subtitle": "The quote endpoint rejected the request — try again later",
            "valid": False,
            "icon": {"path": "icons/Warning.png"},
        })
        continue
    except Exception as err:
        log(f"{symbol}: {err}")
        MYOUTPUT["items"].append({
            "title": f"{symbol}: could not reach Yahoo Finance",
            "subtitle": str(err),
            "valid": False,
            "icon": {"path": "icons/Warning.png"},
        })
        continue

    if not quote or quote.get('regularMarketPrice') is None:
        MYOUTPUT["items"].append({
            "title": f"{symbol}: oops, this doesn't exist or there's no data",
            "subtitle": "",
            "icon": {"path": "icons/Warning.png"},
            "arg": "https://finance.yahoo.com/"
        })
        continue

    currency = quote.get('currency')
    price = quote['regularMarketPrice']
    prev = quote.get('chartPreviousClose') or quote.get('previousClose')
    currentPrice_ts = quote.get('regularMarketTime')
    myTS = datetime.datetime.fromtimestamp(currentPrice_ts).strftime("%Y-%m-%d %H:%M:%S") if currentPrice_ts else ''

    shortName = ' '.join((quote.get('longName') or quote.get('shortName') or symbol).split())
    t_symbol = quote.get('symbol') or symbol

    if prev:
        tk_change = price - prev
        tk_change_perc = tk_change / prev * 100
        chIcon = SYMBOL_UP if tk_change > 0 else SYMBOL_DOWN if tk_change < 0 else ''
        changeStr = " " + (chIcon + " " if chIcon else "") + f"{tk_change:+.2f} ({tk_change_perc:+.2f}%)"
        prevStr = " Previous close: " + format_price(prev, currency)
    else:
        changeStr = ''
        prevStr = ''

    MYOUTPUT["items"].append({
        "title": shortName + ": " + format_price(price, currency) + changeStr,
        "subtitle": "Updated on: " + myTS + prevStr,
        "arg": "https://finance.yahoo.com/quote/" + urlquote(t_symbol)
    })

print(json.dumps(MYOUTPUT))
