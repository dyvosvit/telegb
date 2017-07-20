# A Telegram Bot for Poloniex Trades ##
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
want_pictures = False

# If you don't want console/ssh output, set this to False
want_console_output = False

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
import hmac
import hashlib
import httplib
import socket

timeout = 10
socket.setdefaulttimeout(timeout)

# Force all datetime calculations to UTC
# because that's what Poloniex uses
os.environ['TZ'] = 'UTC'

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    import urllib2
    from urllib2 import Request, urlopen, URLError, HTTPError
    from urllib import urlencode


class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def api_query(self, command, req={}):

        try:
            if(command == "returnTicker" or command == "return24Volume"):
                ret = urlopen(Request('https://www.poloniex.com/public?command=' + command))
                return json.loads(ret.read())
            elif(command == "returnOrderBook"):
                ret = urlopen(Request('https://www.poloniex.com/public?command=' + command +
                              '&currencyPair=' + str(req['currencyPair'])))
                return json.loads(ret.read())
            elif(command == "returnMarketTradeHistory"):
                ret = urlopen(Request('https://www.poloniex.com/public?command=' + "returnTradeHistory" +
                              '&currencyPair=' + str(req['currencyPair'])))
                return json.loads(ret.read())
            else:
                req['command'] = command
                req['nonce'] = int(time.time()*1000)
                post_data = urlencode(req)

                sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
                headers = { 'Sign': sign, 'Key': self.APIKey }

                # For deep debugging
                # req = urllib2.Request('https://www.poloniex.com/tradingApi', post_data, headers)
                # opener = urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=1))
                # ret = opener.open(req)

                ret = urlopen(Request('https://www.poloniex.com/tradingApi', post_data, headers))

                return json.loads(ret.read())

        except URLError as e:
            print "Polo is lagging, or we've got some error: '%s', '%s'" % (e.message, e.reason)
            return ''
        except ssl.SSLError as e:
            print "Internet is lagging, or we've got SSL error: '%s', '%s'" % (e.message, e.reason)
            return ''

    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook(self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory(self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})

    def returnBalances(self):
        return self.api_query('returnBalances')

    def returnTradeHistory(self, currencyPair, start=0, stop=0):
        params = {"currencyPair": currencyPair}
        if start > 0:
            params["start"] = start
        if stop > 0:
            params["stop"] = stop

        return self.api_query('returnTradeHistory', params)


def worker():
    bot = telegram.Bot(token=TG_BOT_TOKEN)
    printed = set()

    # Start out with last 24hrs history
    mostRecentTimestamp = int(time.time() - 86400)

    while (True):
        tradeHistory24h = poloClient.returnTradeHistory('All', mostRecentTimestamp)

        if set_debug:
            print "TRADE24: %s" % (json.dumps(tradeHistory24h))

        # If nothing new, sleep and loop
        if len(tradeHistory24h) == 0:
            if want_console_output:
                print "%s - No new trades since '%s'." % (time.strftime('%c'), time.strftime('%c', time.localtime(mostRecentTimestamp)))
            time.sleep(pollingInterval)
            continue

        # Sample JSON data
        # { "category": "exchange", "fee": "0.00250000", "tradeID": "860775", "orderNumber": "10510",
        #   "amount": "194.19281307", "rate": "0.00004444", "date": "2017-07-19 11:03:46",
        #   "total": "0.00862992", "type": "sell", "globalTradeID": 1942 }

        # Re-order trades based on globalTradeId
        poloResults = {}
        for pair in tradeHistory24h:
            for e in tradeHistory24h[pair]:
                e['pair'] = pair
                e['timestamp'] = int(time.mktime(time.strptime(e['date'], "%Y-%m-%d %H:%M:%S")))
                poloResults[int(e['globalTradeID'])] = e

        # Loop over most recent trades history
        for gtid in sorted(poloResults.keys())[-latestTrades:]:

            # TODO: get rid of this 'printed'
            if gtid in printed:
                continue

            # Remember that we already displayed this order
            printed.add(gtid)
            time.sleep(0.33)

            if want_pictures:
                if poloResults[gtid][2] == "BUY":
                    bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/buy.png')
                else:
                    bot.send_photo(chat_id=TG_ID, photo='https://raw.githubusercontent.com/dyvosvit/telegb/master/sell.png')

            # Construct strings
            # POLONIEX: BTC_DASH 2017-07-20 18:25:15 SELL of 194.19281307 DASH at 0.07390809 with revenue of +0.00919869

            coin = poloResults[gtid]['pair'].split('_')[1]
            type = poloResults[gtid]['type'].upper()
            botMessage = "<b>POLONIEX:</b> <b>%s</b> <b>%s</b> <b>%s</b> of %s <b>%s</b> at %s with %s of <b>%s%s</b>" % (
                poloResults[gtid]['pair'],
                poloResults[gtid]['date'],
                type, poloResults[gtid]['amount'], coin,
                poloResults[gtid]['rate'],
                'investments' if type == 'BUY' else 'revenue',
                '-' if type == 'BUY' else '+',
                poloResults[gtid]['total'])

            if set_debug:
                print botMessage

            if want_console_output:
                print "POLONIEX: %-9s %s (%d) %-4s %s at %s (%s%s)" % (
                    poloResults[gtid]['pair'], poloResults[gtid]['date'], poloResults[gtid]['timestamp'],
                    type, poloResults[gtid]['amount'], poloResults[gtid]['rate'], '-' if type == 'BUY' else '+',
                    poloResults[gtid]['total'])

            # Call Telegram bot API
            bot.send_message(chat_id=TG_ID, text=botMessage, parse_mode=telegram.ParseMode.HTML)

        # We've displayed all recent trades
        # Save the last trade timestamp for more efficient API calls.
        # Poloniex search results are inclusive so add 1 sec to account for this.
        mostRecentTimestamp = poloResults[max(printed)]['timestamp']+1

        # Display balance
        poloBalances = poloClient.returnBalances()

        txtBalance = 'No Balance'
        if 'BTC' in poloBalances:
            txtBalance = 'Current available Poloniex BTC balance: ' + poloBalances['BTC']

        if set_debug:
            print "Balances: %s" % (json.dumps(poloBalances))

        if want_console_output:
            print txtBalance

        bot.send_message(chat_id=TG_ID, text="<b>POLONIEX: %s</b>" % (txtBalance), parse_mode=telegram.ParseMode.HTML)

        # Sleep the while-loop
        time.sleep(pollingInterval)


if __name__ == '__main__':

    # Create the API client
    poloClient = poloniex(pkey, spkey)

    try:
        worker()
    except KeyboardInterrupt:
        print 'Quitting...'
        os._exit(0)
