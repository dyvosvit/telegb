## A Telegram Bot for Poloniex Trades ##
#
# If it worked for you, you use and like it = donate any amount you wish
# BTC: 1HRjjHByNL2enV1eRR1RkN698tucecL6FA
# ETH: 0x4e5e7b86baf1f8d6dfb8a242c85201c47fa86c74
# ZEC: t1aKAm7qXi6fbGvAhbLioZm3Q8obb4e3BRo
#

# Depends/installs
# pip install python-telegram-bot --upgrade

set_debug = False

# If you don't want the 'BUY'/'SELL' images in your Telegram, set this to False
want_pictures = True

# If you don't want console/ssh output, set this to False
want_console_output = True

# Generate new API key/secret from Poloniex and put them here
pkey = ''
spkey = ''

# Put in your telegram chat id from @get_id_bot
# Add the bot and start chat: https://telegram.me/get_id_bot
# It will respond with 'Your Chat ID = NNNNNNN'
TG_ID = ""

# Put in the telegram bot token from @BotFather
TG_BOT_TOKEN = ""

pollingInterval = 5
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

        try:
            if(command == "returnTicker" or command == "return24Volume"):
                ret = urlopen(Request('https://www.poloniex.com/public?command=' + command))
                return json.loads(ret.read())
            elif(command == "returnOrderBook"):
                ret = urlopen(Request('https://www.poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
                return json.loads(ret.read())
            elif(command == "returnMarketTradeHistory"):
                ret = urlopen(Request('https://www.poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
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

                ret = urlopen(Request('https://www.poloniex.com/tradingApi', post_data, headers))
                jsonRet = json.loads(ret.read())
                return self.post_process(jsonRet)

        except URLError as e:
            print("Polo is lagging, we've got some error")
            print(e.message,e.reason)
            print("  ... continue")
            return ''
        except ssl.SSLError:
            print("Internet is lagging, we've got SSL error")
            return ''

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
                print_coins = 'ETH XRP XEM LTC STR BCN ETC DGB SC BTS DOGE DASH GNT EMC2 STEEM XMR ARDR STRAT NXT ZEC LSK FCT GNO NMC MAIDBURST GAME DCR SJCX RIC FLO REP NOTE CLAM SYS PPC EXP XVC VTC FLDC LBC AMP POT NAV XCP BTCD RADSPINK GRC NAUT BELA OMNI HUC NXC VRC XPM VIA PASC BTM NEOS XBC BLK SBD BCY'
                print_coins = print_coins.strip().split()
        work_set = {}
        for line in tradeHistory24h:
            for element in tradeHistory24h[line]:
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

def worker():
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

                    if want_pictures:
                        if pollResult[key][2]=="BUY":
                            bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/buy.png')
                        else:
                            bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/sell.png')

                    pollResult[key][0]='<b>'+pollResult[key][0]+'</b>'
                    pollResult[key][2]='<b>'+pollResult[key][2]+'</b>'
                    pollResult[key][8]='<b>'+pollResult[key][8]+'</b>'

                    if want_console_output:
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

                if want_console_output:
                    print text_balance

                bot.send_message(chat_id=TG_ID, text='<b>'+"POLONIEX: "+text_balance+'</b>', parse_mode=telegram.ParseMode.HTML)

        time.sleep(pollingInterval)

if __name__ == '__main__':
    try:
        worker()
    except KeyboardInterrupt:
        print 'Quitting...'
        os._exit(0)
