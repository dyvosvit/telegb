Telegram bot to watch your trades on Poloniex or Bittrex.

This is Python 2 Script 

Example of screen is here:
https://prnt.sc/fmefvh


1. download and install python 2.7.13 for windows:
tick "Add python to PATH" !!

https://www.python.org/downloads/release/python-2713/

for linux users:

apt-get update&&apt-get upgrade

apt-get install curl

curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"

python get-pip.py

2. install python-telegram-bot

pip install python-telegram-bot --upgrade


HOWTO ACTIVATE THIS BOT:

In telepl.py or telebt.py:

Generate new API from Poloniex or Bittrex, change pkey/spkey

Change "TG_BOT_TOKEN" to your telegram bot token that you got from BotFather:

Talk to @BotFather and type "/newbot" to create a bot.

answer the questions by typing answers and pressing enter

then type in chat your bot's name (for ex. @gb-to-telegram)

and press start button

Change "TG_ID" to your telegram chat id (to find it out send command "/my_id" to telegram user @get_id_bot)

RUN:

for poloniex:
python telepl.py

for bittrex:
python telebt.py

#it worked for you, you use and like it = donate any amount you wish

#BTC: 1HRjjHByNL2enV1eRR1RkN698tucecL6FA

I welcome ideas, additions ....

My telegram is @Dyvosvit



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
либо
python -m pip install python-telegram-bot

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

#BTC: 1HRjjHByNL2enV1eRR1RkN698tucecL6FA

Я приветствую Ваши идеи, дополнения ...

Моя телеграмма @Dyvosvit








UPD: for community proxy users:

apt-get install tmux

tmux new-session

echo "127.0.0.1 localhost" >./my_hosts

echo "104.20.12.48 poloniex.com" >>./my_hosts

sudo unshare -m bash -c "mount ./my_hosts /etc/hosts --bind; bash"

cat /etc/hosts

python telebt.pyy

or

python telepl.py

