# Telegram Bot to watch your trades on Poloniex or Bittrex.

This is Python 2 Script 

Example of screen is here:
https://prnt.sc/fmefvh

## Windows

1. Download and install python 2.7.13 for windows:
tick "Add python to PATH" !!

https://www.python.org/downloads/release/python-2713/

## Linux

1. Install curl and pip

    ```
    sudo apt-get update && sudo apt-get upgrade
    sudo apt-get install curl
    
    curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
    sudo python get-pip.py
    ```
    
2. Install python-telegram-bot

    ```
    sudo pip install python-telegram-bot --upgrade
    ```

## HOWTO CREATE AND CONFIGURE THIS BOT:

_telepl.py_ is for Poloniex
_telebt.py_ is for Bittrex

1. Generate new API key from Poloniex or Bittrex. Edit the appropriate script file for your exchange and change the __pkey__ and __spkey__ variables.

2. Talk to @BotFather and type "/newbot" to create a bot. Answer the questions by typing answers and pressing enter.

3. Start a chat to your bot's name (for ex. @gb-to-telegram) and press start button

4. Start another chat with https://telegram.me/get_id_bot This bot will reveal your __Chat ID__

5. Edit the appropriate script and change __TG_BOT_TOKEN__ to the telegram bot token that you got from BotFather and change __TG_ID__ to your telegram chat id that you got from @get_id_bot

### Optional

In the script there are several settings you can tune to suit your desires:

    want_pictures = True (or False)       // Displays 'BUY' and 'SELL' text images in bot chat
    pollingInterval = 5                   // How many seconds to sleep between queries
    latestTrades = 10                     // How many of the most recent trades to display per interval
    coinBalancesToShow = ['BTC', 'USDT']  // Show or not show other coin balances
    balancesInterval = 0                  // Display coin balances after this many intervals
    logFile = "telepl.log"                // All logging happens in this file; appends on restart
    logLevel = logging.WARNING            // INFO, WARNING, DEBUG

## RUNING THE BOT:

### For Poloniex:

    python telepl.py

### For Bittrex:

    python telebt.py

If it worked for you, you use and like it = donate any amount you wish

#BTC: 1hHa79zoc4REFWFHwMCRQgW7fYPXJHbpf

I welcome ideas, additions ....

Telegram: @Dyvosvit / @krixtr

---

Телеграмм бот для отслеживания торгов на Poloniex или Bittrex.

Это скрипт рассчитан на Python версии 2.7.Х

Пример экрана:
https://prnt.sc/fmefvh


1. загрузить и установить python 2.7.13 для виндовоза:
При установке отметьте «Добавить python в PATH» !!

ссылка для скачивания:
https://www.python.org/downloads/release/python-2713/

Для пользователей linux:

apt-get update && apt-get upgrade
apt-get install curl
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python get-pip.py

2. Установить модуль python-telegram-bot

pip install python-telegram-bot --upgrade
либо(windows)
c:\python27\python -m pip install python-telegram-bot

Как автивировать Бота для телеграмма:

Внутрь telepl.py или telebt.py:

вписываете новосозданный API от Poloniex или Bittrex, измените значения вверху увидите чтото типа pkey / spkey

Измените «TG_BOT_TOKEN» на токен ботлета телеграммы, который вы получили от BotFather:
как получить этот токен
в любом чате пишите @BotFather, enter, жмете на эту же сслыку
Открывается чат с @BotFather и введите команду /newbot, чтобы создать бота.
Отец всех ботов будет спрашивать имя бота и т.п.
Ответьте на вопросы, набрав ответы и нажав enter
папа всех ботов даст вам ваш токен, впишите его в telebt.py или telepl.py в поле TG_BOT_TOKEN
Затем введите в любом чате имя своего нового бота (например, у меня это @gb-to-telegram)

И нажмите кнопку «Пуск/Старт» в меню разговора со своим ботом, бота надо запустить иначе он будет неактивен
с токеном бота пока все 

Измените «TG_ID» на ваш идентификатор чата телеграммы 
пишите в любом чате @get_id_bot, жмете на эту же ссылку, отправляете команду /my_id
получаете ваш телеграм айди
вписываете его в telebt.py или telepl.py в поле TG_ID

запуск:

Для poloniex:
python telepl.py

Для биттрекса:
python telebt.py

так вот если мой бот у вас работет, вы им пользуетесь = пожертвуйте любую сумму, которую вы хотите

#BTC: 1hHa79zoc4REFWFHwMCRQgW7fYPXJHbpf

Я приветствую Ваши идеи, дополнения ...

Моя телеграмма @Dyvosvit
