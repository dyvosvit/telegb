# it worked for you, you use and like it = donate any amount you wish
# BTC: 1hHa79zoc4REFWFHwMCRQgW7fYPXJHbpf
# ETH: 0x4e5e7b86baf1f8d6dfb8a242c85201c47fa86c74

set_debug = False

import imp, sys, pip, time, thread, traceback

def install(package):
    pip.main(["install", package])

try:
    imp.find_module("python-telegram-bot")
except ImportError:
    print "The 'python-telegram-bot' package is not installed. Attempting to install..."
    install("python-telegram-bot")

try:
    imp.find_module("requests")
except ImportError:
    print "The 'requests' package is not installed. Attempting to install..."
    install("requests")

#generate new API key/secret from Bittrex and put them here
bkey = ""
bskey= ""
pollingInterval = 1
latestTrades = 10
# put in your telegram chat id from @get_id_bot
TG_ID = ""
# put in the telegram bot token from @BotFather
TG_BOT_TOKEN = ""

import threading
import os
# import ssl
import telegram
import time
import json
import time, datetime
import datetime
import calendar
import hmac, hashlib
import httplib
import requests

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen, URLError, HTTPError
    from urllib import urlencode


BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

PUBLIC_SET = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getorderbook',
          'getmarkethistory']

MARKET_SET = ['getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit']

ACCOUNT_SET = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']


class Bittrex(object):

    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.public_set = set(PUBLIC_SET)
        self.market_set = set(MARKET_SET)
        self.account_set = set(ACCOUNT_SET)

    def api_query(self, method, options=None):
        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))
        base_url = 'https://bittrex.com/api/v1.1/%s/'
        request_url = ''

        if method in self.public_set:
            request_url = (base_url % 'public') + method + '?'
        elif method in self.market_set:
            request_url = (base_url % 'market') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        elif method in self.account_set:
            request_url = (base_url % 'account') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        #print(options)
        request_url += urlencode(options)

        signature = hmac.new(self.api_secret, request_url, hashlib.sha512).hexdigest()

        headers = {"apisign": signature}

        try:
            ret = requests.get(request_url, headers=headers)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            return {'success':False}
        if ret.ok:
            return ret.json()
        else:
            return {'success':False}

    def get_markets(self):
        return self.api_query('getmarkets')

    def get_currencies(self):
        return self.api_query('getcurrencies')

    def get_ticker(self, market):
         return self.api_query('getticker', {'market': market})

    def get_market_summaries(self):
        return self.api_query('getmarketsummaries')

    def get_orderbook(self, market, depth_type, depth=20):
        return self.api_query('getorderbook', {'market': market, 'type': depth_type, 'depth': depth})

    def get_market_history(self, market, count):
        return self.api_query('getmarkethistory', {'market': market, 'count': count})

    def buy_market(self, market, quantity, rate):
        return self.api_query('buymarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def buy_limit(self, market, quantity, rate):
        return self.api_query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_market(self, market, quantity, rate):
        return self.api_query('sellmarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_limit(self, market, quantity, rate):
       return self.api_query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def cancel(self, uuid):
       return self.api_query('cancel', {'uuid': uuid})

    def get_open_orders(self, market):
        return self.api_query('getopenorders', {'market': market})

    def get_balances(self):
       return self.api_query('getbalances', {})

    def get_balance(self, currency):
        return self.api_query('getbalance', {'currency': currency})

    def get_deposit_address(self, currency):
       return self.api_query('getdepositaddress', {'currency': currency})

    def get_order(self, uuid):
       return self.api_query('getorder', {'uuid': uuid})

    def get_deposit_history(self, currency=""):
        if currency == "":
            return self.api_query('getdeposithistory')
        else:
            return self.api_query('getdeposithistory', {"currency": currency})

    def get_withdrawal_history(self, currency=""):
        if currency == "":
            return self.api_query('getwithdrawalhistory')
        else:
            return self.api_query('getwithdrawalhistory', {"currency": currency})

    def get_order_history(self, market = ""):
        if market == "":
            return self.api_query('getorderhistory')
        else:
            return self.api_query('getorderhistory', {"market": market})


testapi = Bittrex(bkey, bskey)

def f(a,n,s):
    return (s+str(format(a, '.8f'))).rjust(n)

def calculateEstimatedBTCs(balanceBTC):
    bittrexCoinz={}
    if resultBalances['success']==True:
         for i in resultBalances['result']:
            if (i['Balance']!=0):
                bittrexCoinz[i['Currency']]=i
    totalRevenues=0
    if resultTicker['success']==True:
        for i in resultTicker['result']:
            market,coin =  i['MarketName'].split('-')
            if (market=='BTC') and (coin in bittrexCoinz.keys()):
                totalRevenues += float(bittrexCoinz[coin]['Balance']*i['Last'])
    return float(balanceBTC)+totalRevenues

def pollBittrexTrades():
    resultMarkets=testapi.get_order_history()
    text_out={}
    if resultMarkets['success']==True:
        #print len(resultMarkets)
        for i in resultMarkets['result'][:latestTrades]:
            date=i['TimeStamp'].replace('T',' ').split('.')[0]
#            dt = datetime.datetime.strptime(i['TimeStamp'], '%Y-%m-%dT%H:%M:%S.%f')
#            utc_time = time.mktime(dt.timetuple())
            #print(str(utc_time).split('.')[0])
            text_out[date]=[i['Exchange'], date,
                                      i['OrderType'][6:],str(i['Quantity']),'of',i['Exchange'][4:],
                                      'at',f(i['PricePerUnit'],0,''),'resulting',
                                      '-'+str(i['Price']) if i['OrderType'][6:] == 'BUY' else '+'+str(i['Price'])]
    return text_out

bot = telegram.Bot(token=TG_BOT_TOKEN)
printed = {}
savedLen = len(printed)
estimatedValueBTC = 0
while (True):
    pollResult = pollBittrexTrades()
    #print pollResult
    for key in sorted(pollResult.keys()):
        if key not in printed.keys():
            printed[key] = True
            time.sleep(0.33)
            if pollResult[key][2] == "BUY":
                bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/buy.png')
            else:
                bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/sell.png')
            pollResult[key][2] = '<b>' + pollResult[key][2] + '</b>'
            pollResult[key][5] = '<b>' + pollResult[key][5] + '</b>'
            pollResult[key][9] = '<b>' + pollResult[key][9] + '</b>'
            print ' '.join(pollResult[key])
            bot.send_message(chat_id=TG_ID, text="<b>BITTREX: </b>"+' '.join(pollResult[key]), parse_mode=telegram.ParseMode.HTML)
    if savedLen < len(printed):
        savedLen = len(printed)
        text_balance = 'Current available BTC balance is: '
        balance = testapi.get_balance('BTC')
        if balance['success'] == True:
            text_balance = text_balance + '{:+.14f}'.format(float(balance['result']['Available']))
        else:
            text_balance = text_balance + ' ... some error occured ...'
        print text_balance
        time.sleep(0.3)
        resultBalances = testapi.get_balances()
        time.sleep(0.3)
        # print resultBalances['result']
        resultTicker = testapi.get_market_summaries()
        time.sleep(0.3)
        # print resultTicker['result']
        estimValueCurrent = calculateEstimatedBTCs(balance['result']['Available'])
        text_estimated = 'Current estimated value of portfolio in BTCs (lastprice):{:+.14f}'.format(
            float(estimValueCurrent))
        print text_estimated
        bot.send_message(chat_id=TG_ID, text='<b>' + text_balance + '</b>', parse_mode=telegram.ParseMode.HTML)
        bot.send_message(chat_id=TG_ID, text='<b>' + text_estimated + '</b>', parse_mode=telegram.ParseMode.HTML)
    #print 'wait 1 sec'
    time.sleep(pollingInterval)
