#it worked for you, you use and like it = donate any amount you wish
#BTC: 1HRjjHByNL2enV1eRR1RkN698tucecL6FA
#ETH: 0x4e5e7b86baf1f8d6dfb8a242c85201c47fa86c74
#ZEC: t1aKAm7qXi6fbGvAhbLioZm3Q8obb4e3BRo

#depends/installs
# pip install python-telegram-bot --upgrade
set_debug = False
#generate new API key/secret from Poloniex and put them here
pkey = ''
spkey = ''

# put in your telegram chat id from @get_id_bot
TG_ID = ""
# put in the telegram bot token from @BotFather
TG_BOT_TOKEN = ""

pollingInterval = 1
latestTrades = 10


import threading
import os
import ssl
import telegram
import time
import json
import time, datetime
from datetime import date, datetime
import calendar
import hmac,hashlib
import httplib
import socket

timeout = 10
socket.setdefaulttimeout(timeout)

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen, URLError, HTTPError
    from urllib import urlencode

class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(date.createTimeStamp(after['return'][x]['datetime']))
                            
        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urlopen(Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urlopen(Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urlopen(Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }
            #print(req)
            try:
                ret = urlopen(Request('https://poloniex.com/tradingApi', post_data, headers))
            except URLError as e:
                print("Polo is lagging, we've got some error")
                print(e.message,e.reason)
                print("  ... continue")
                return ''
            except ssl.SSLError:
                print("Internet is lagging, we've got SSL error")
                return ''


            jsonRet = json.loads(ret.read())

            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})
        
    def returnBalances(self):
        return self.api_query('returnBalances')

    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})


testapi = poloniex(pkey,spkey)
pollingInterval = 1

def pollCoinsTrades24h():
    print_coins = []
    tradeHistory24h = testapi.returnTradeHistory('All')
    pollResult = {}
    if tradeHistory24h != '':
        if set_debug:
            print(tradeHistory24h)
        try:
            with open(check_coins, 'r') as afile:
                for coin in afile:
                    print_coins += [coin.strip()]
        except:
            if print_coins == []:
                print_coins = 'ETH XRP XEM LTC STR  BCN ETC DGB SC BTS DOGE DASH GNT EMC2 STEEM XMR ARDR STRAT NXT  ZEC LSK  FCT GNO NMC MAID   BURST GAME  DCR  SJCX RIC FLO REP NOTE CLAM SYS PPC EXP XVC VTC FLDC LBC AMP POT NAV XCP  BTCD  RADS   PINK GRC  NAUT  BELA  OMNI HUC NXC VRC  XPM VIA PASC  BTM NEOS XBC  BLK SBD BCY'
                print_coins = print_coins.strip().split()
        work_set = {}
        for line in tradeHistory24h:
            for element in tradeHistory24h[line]:
#                print(element)
                signd = ''
                try:
                    signd = '-' if element['type']=='buy' else '+'
                    totald = signd+element['total']
                    thetext = 'with investments of' if element['type']=='buy' else 'with revenue of'
                    work_set[int(element['globalTradeID'])]=[line, element['date'],element['type'].upper(), 'of',line.split('_')[1] , 'at', element['rate'],thetext,totald]
                except:
                    pass
        for key in sorted(work_set.keys(),reverse=True)[:latestTrades]:
            pollResult[key] = work_set[key]
    return pollResult


bot = telegram.Bot(token=TG_BOT_TOKEN)
printed = {}
savedLen = len(printed)
while (True):
    pollResult=pollCoinsTrades24h()
    if pollResult!='':
        for key in sorted(pollResult.keys()):
            if key not in printed.keys():
                printed[key]=True
                time.sleep(0.33)
                if pollResult[key][2]=="BUY":
                    bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/buy.png')
                else:
                    bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/sell.png')
                pollResult[key][0]='<b>'+pollResult[key][0]+'</b>'
                pollResult[key][2]='<b>'+pollResult[key][2]+'</b>'
                pollResult[key][8]='<b>'+pollResult[key][8]+'</b>'
                print "<b>POLONIEX: </b>"+' '.join(pollResult[key])
                bot.send_message(chat_id=TG_ID, text="<b>POLONIEX: </b>"+' '.join(pollResult[key]), parse_mode=telegram.ParseMode.HTML)
        if savedLen < len(printed):
            savedLen = len(printed)
            balance = testapi.returnBalances()
            text_balance = 'No balance'
            if balance != '':
                try:
                    text_balance = 'Current available Poloniex BTC balance: ' + balance['BTC']
                except:
                    pass
            print text_balance
            bot.send_message(chat_id=TG_ID, text='<b>'+"POLONIEX: "+text_balance+'</b>', parse_mode=telegram.ParseMode.HTML)
    time.sleep(pollingInterval)
