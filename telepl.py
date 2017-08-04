# A Telegram Bot for Poloniex Trades #
#
# If it worked for you, you use and like it = donate any amount you wish
# @dyvosvit - Original author:
#   BTC: 1HRjjHByNL2enV1eRR1RkN698tucecL6FA
#   ETH: 0x4e5e7b86baf1f8d6dfb8a242c85201c47fa86c74
#   ZEC: t1aKAm7qXi6fbGvAhbLioZm3Q8obb4e3BRo
# @Krixt improvements:
#   BTC: 1CdVfNqs2eH94hSnH2ZMCKdMFrTd44VHcY
#   ETH: 0xF4738514F79736CEC609E437173a3d62bB9f7714
#

# Depends/installs
# pip install python-telegram-bot --upgrade

# Generate new API key/secret from Poloniex and put them here
pkey = ''
spkey = ''

# Put in your telegram chat id from @get_id_bot
# Add the bot and start chat: https://telegram.me/get_id_bot
# It will respond with 'Your Chat ID = NNNNNNN'
TG_ID = ""

# Put in the telegram bot token from @BotFather
TG_BOT_TOKEN = ""

# If you don't want the 'BUY'/'SELL' images in your Telegram, set this to False
want_pictures = False

# How frequently to poll for new trades
pollingInterval = 5

# How many of the most recent trades to display
latestTrades = 10

# Which coin balances to display; supports all coins
coinBalancesToShow = ['BTC', 'USDT', 'ETH']

# How often, additionally, in pollingIntervals, to show balances?
# Balances will always be shown after BUY/SELL regardless of this setting.
# 0 = disabled; Ex: balancesInterval=60 and pollingInterval=5 means show balances every 300s/5m
balancesInterval = 0

# Change logging level. Options:
# DEBUG (most verbose, including JSON dumps), INFO, WARNING (Default)
import logging
logFile = "telepl.log"
logLevel = logging.DEBUG

#
# ## Should not need to change anything below here ##
#

import os
import ssl
import telegram
import time
import json
import hmac
import hashlib
import httplib
import socket
from tempfile import gettempdir

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
                req['nonce'] = int(time.time() * 1000)
                post_data = urlencode(req)

                sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
                headers = {'Sign': sign, 'Key': self.APIKey}

                # For deep debugging
                # req = urllib2.Request('https://www.poloniex.com/tradingApi', post_data, headers)
                # opener = urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=1))
                # ret = opener.open(req)

                ret = urlopen(Request('https://www.poloniex.com/tradingApi', post_data, headers))

                return json.loads(ret.read())

        except HTTPError as e:
            logging.warning("HTTP Error: %d '%s'" % (e.code, e.reason))
            return ''
        except URLError as e:
            logging.warning("Polo is lagging, or we've got some error: '%s', '%s'" % (e.message, e.reason))
            return ''
        except ssl.SSLError as e:
            logging.warning("Internet is lagging, or we've got SSL error: '%s'" % (e.message))
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


def getMostRecentTimestamp():

    # Default 24hrs ago
    mrt = int(time.time() - 86400)

    try:
        with open(gettempdir() + "/telepl_last", "r") as f:
            t = f.readline()

            if t != "":
                l = int(t)

            if l > mrt:
                mrt = l

            logging.debug("Read '%s' from TMP/telepl_last. Using '%d' as timestamp." % (t, mrt))

    except (IOError, ValueError):
        logging.info("No /telepl_last file found or unable to parse contents. Continuing.")

    return mrt


def worker():

    # Initialize the Telegram BOT
    bot = telegram.Bot(token=TG_BOT_TOKEN)

    # For counting intervals
    numIntervals = 0

    # Start out with last 24hrs history or previously saved left-off point
    mostRecentTimestamp = getMostRecentTimestamp()

    # So we can call this as a helper
    def displayBalances():

        # Display balance
        poloBalances = poloClient.returnBalances()
        logging.debug("JSON DUMP Balances: %s" % (json.dumps(poloBalances)))

        txtBalance = ''
        for k in coinBalancesToShow:
            if k in poloBalances:
                txtBalance += "%s: %s | " % (k, poloBalances[k])

        if len(txtBalance) == 0:
            txtBalance = '(Not Available)'

        botMessage = "<b>POLONIEX: Current Poloniex Balances: %s</b>" % (txtBalance)

        logging.info(botMessage)
        bot.send_message(chat_id=TG_ID, text=botMessage, parse_mode=telegram.ParseMode.HTML)

    # Main loop
    while (True):

        # Get the history from Polo
        tradeHistory = poloClient.returnTradeHistory('All', mostRecentTimestamp)
        logging.debug("Trade History: %s" % (json.dumps(tradeHistory)))

        # For interval printing
        if balancesInterval > 0:
            numIntervals += 1

        # If nothing new, sleep and loop
        if len(tradeHistory) == 0:

            logging.info("No new trades since '%s'." % (time.strftime('%c', time.localtime(mostRecentTimestamp))))

            if numIntervals > balancesInterval:
                displayBalances()
                numIntervals = 0

            time.sleep(pollingInterval)
            continue

        # Sample JSON data
        # {"error": "Connection timed out. Please try again."}
        # { "category": "exchange", "fee": "0.00250000", "tradeID": "860775", "orderNumber": "10510",
        #   "amount": "194.19281307", "rate": "0.00004444", "date": "2017-07-19 11:03:46",
        #   "total": "0.00862992", "type": "sell", "globalTradeID": 1942 }

        # Some internal error within Poloniex. A string is returned.
        if 'error' in tradeHistory:
            logging.warning("Poloniex Error: '%s'" % (tradeHistory['error']))
            time.sleep(pollingInterval)
            continue

        # Re-order trades based on globalTradeId
        poloResults = {}
        for pair in tradeHistory:
            for e in tradeHistory[pair]:
                e['pair'] = pair
                e['timestamp'] = int(time.mktime(time.strptime(e['date'], "%Y-%m-%d %H:%M:%S")))
                poloResults[int(e['globalTradeID'])] = e

        # Loop over most recent trades history
        for gtid in sorted(poloResults.keys())[-latestTrades:]:

            # Artifical sleep as to not pound the API
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
            botMessage = "<b>POLONIEX:</b> <b>%s</b> %s <b>%s</b> of %s <b>%s</b> at %s with %s of <b>%s%s</b>" % (
                poloResults[gtid]['pair'],
                poloResults[gtid]['date'],
                type, poloResults[gtid]['amount'], coin,
                poloResults[gtid]['rate'],
                'investments' if type == 'BUY' else 'revenue',
                '-' if type == 'BUY' else '+',
                poloResults[gtid]['total'])

            logging.info(botMessage)

            # Call Telegram bot API
            bot.send_message(chat_id=TG_ID, text=botMessage, parse_mode=telegram.ParseMode.HTML)

            # Save the last trade timestamp for more efficient API calls.
            # Poloniex search results are inclusive so add 1 sec to account for this.
            mostRecentTimestamp = poloResults[gtid]['timestamp'] + 1

        # Always show balances after BUY/SELL
        displayBalances()

        # Write out latest trade timestamp for better restart
        with open(gettempdir() + "/telepl_last", "w") as f:
            f.write("%d" % (mostRecentTimestamp))

        # Sleep the while-loop
        time.sleep(pollingInterval)


if __name__ == '__main__':

    # Setup logging
    logging.basicConfig(filename=logFile, level=logLevel, format='%(asctime)s %(levelname)s: %(message)s')
    logging.info("# Welcome to Telebot for Poloniex")

    # Create the API client
    try:
        poloClient = poloniex(pkey, spkey)
    except:
        msg = "Unable to initialize Poloniex client. Check API key and secret for accuracy"
        logging.critical(msg)
        print msg
        os._exit(1)

    try:
        worker()
    except KeyboardInterrupt:
        print 'Quitting...'
        os._exit(0)
