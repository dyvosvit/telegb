#it worked for you, you use and like it = donate any amount you wish
#BTC: 1HRjjHByNL2enV1eRR1RkN698tucecL6FA
#ETH: 0x4e5e7b86baf1f8d6dfb8a242c85201c47fa86c74
#ZEC: t1aKAm7qXi6fbGvAhbLioZm3Q8obb4e3BRo
import telegram
import time
from datetime import datetime, timedelta

i_want_to_see_the_result_in_console = True
#depends/installs
# pip install python-telegram-bot

# put in your telegram chat id from @get_id_bot
TG_ID = ""

# put in the telegram bot token from @BotFather
TG_BOT_TOKEN = ""

#interval to poll in seconds
pollingInterval = 3600
#name the file
file_to_read_every_interval='testfile.txt'
#init your TG BOT
bot = telegram.Bot(token=TG_BOT_TOKEN)
#forever
while (True):
#readfile
    text=open(file_to_read_every_interval,'r').read().strip()
# print timestamp and text to console if there's need of it
    timestamp = str(datetime.utcnow()).split('.')[0]
    if i_want_to_see_the_result_in_console:
        print(timestamp)
        print(text)
#send message with timestamp
    bot.send_message(chat_id=TG_ID, text=timestamp, parse_mode=telegram.ParseMode.HTML)
#send message with text
    bot.send_message(chat_id=TG_ID, text=text, parse_mode=telegram.ParseMode.HTML)
#waiting interval
    time.sleep(pollingInterval)
