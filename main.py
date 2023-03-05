from pprint import pprint
from schedule import every, run_pending
import telebot
from config import *
from threading import Thread
import time
from selenium import webdriver
from telebot import types
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from tabulate import tabulate


print("START")
bot = telebot.TeleBot(token)
SEND_MESSAGE = True

options = webdriver.ChromeOptions()
options.add_argument('headless')
# options.add_argument('window-size=1920x935')
# driver = webdriver.Chrome(chrome_options=options)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get('https://kwenta.eth.limo/dashboard/markets/')
time.sleep(5)


def work():
    while True:
        run_pending()
        time.sleep(0.5)


def get_data():
    global driver
    while True:
        try:
            print("запуск")
            ua = dict(DesiredCapabilities.CHROME)
            titles = driver.find_elements_by_xpath('//div[@class="sc-b443446-8 cBdjNX"]')
            fundings = driver.find_elements_by_xpath(
                '//div[@class="sc-54e96af5-0 sc-54e96af5-1 sc-14eb40a9-1 kZKXJo table-body-cell"]')
            data = []
            exp_data = []
            loc = []
            plus = []
            minus = []
            for i in range(len(fundings)):
                loc.append(fundings[i])
                if (i + 1) % 6 == 0:
                    data.append(loc)
                    loc = []
            for item in data:
                titl, fun = item[0], item[3]
                add_zn = ''
                if fun.find_element_by_tag_name('span').value_of_css_property('color') == 'rgba(239, 104, 104, 1)':
                    add_zn = '-'
                    minus.append([float(add_zn + fun.text[:-1]), titl.text.split('\n')[0]])
                else:
                    plus.append([float(add_zn + fun.text[:-1]), titl.text.split('\n')[0]])
                exp_data.append([titl.text.split('\n')[0] + '\n\n', add_zn + fun.text])
            plus.sort(key=lambda x: x[0])
            minus.sort(key=lambda x: x[0])
            with open('daily_sum.json', 'r') as f:
                daily_sum = json.load(f)
            for val, t in plus:
                daily_sum[t] = daily_sum.get(t, 0) + val
            for val, t in minus:
                daily_sum[t] = daily_sum.get(t, 0) + val
            with open('daily_sum.json', 'w') as f:
                json.dump(daily_sum, f, ensure_ascii=False)
            str_plus, str_minus = '\n', '\n'
            for i in range(len(plus)):
                plus[i][0] = f"{round(plus[i][0], 4)}({round(plus[i][0] * 24 * 365, 1)}%)"
                str_plus += f"{plus[i][0]}    {plus[i][1]}\n"
            for i in range(len(plus)):
                minus[i][0] = f"{round(minus[i][0], 4)}({round(minus[i][0] * 24 * 365, 1)}%)"
                str_minus += f"{minus[i][0]}    {minus[i][1]}\n"
            # print(f"Longs pay Shorts if positive:\n {str_plus}\nShorts pay Longs if negative:\n {str_minus}")
            if SEND_MESSAGE:
                bot.send_message(
                    channel_name,
                    f"Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
            else:
                print(f"Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
                print('-' * 20)
            return
        except Exception as e:
            print("ERROR   ", e)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            driver.get('https://kwenta.eth.limo/dashboard/markets/')


def send_weekly_sum():
    while True:
        try:
            with open('weekly_sum.json', 'r') as f:
                weekly_sum = json.load(f)
            plus = []
            minus = []
            for key in weekly_sum:
                if weekly_sum[key] < 0:
                    minus.append([weekly_sum[key], key])
                else:
                    plus.append([weekly_sum[key], key])
            plus.sort(key=lambda x: x[0])
            minus.sort(key=lambda x: x[0])
            str_minus, str_plus = '\n', '\n'
            for i in range(len(plus)):
                plus[i][0] = f"{round(plus[i][0], 4)}({round(plus[i][0] * 24 * 365, 1)}%)"
                str_plus += f"{plus[i][0]}    {plus[i][1]}\n"
            for i in range(len(plus)):
                minus[i][0] = f"{round(minus[i][0], 4)}({round(minus[i][0] * 24 * 365, 1)}%)"
                str_minus += f"{minus[i][0]}    {minus[i][1]}\n"

            if SEND_MESSAGE:
                bot.send_message(
                    channel_name,
                    f"Weekly\n\n Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
            else:
                print(f"Weekly\n\n Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
                print('-' * 20)
            with open('weekly_sum.json', 'w') as f:
                f.write('{}')
            return
        except Exception as e:
            print('ERROR: ', e)


def send_daily_sum():
    while True:
        try:
            with open('daily_sum.json', 'r') as f:
                daily_sum = json.load(f)
            with open('weekly_sum.json', 'r') as f:
                weekly_sum = json.load(f)
            for key in daily_sum:
                weekly_sum[key] = weekly_sum.get(key, 0) + daily_sum[key]
            with open('weekly_sum.json', 'w') as f:
                json.dump(weekly_sum, f, ensure_ascii=False)
            plus = []
            minus = []
            for key in daily_sum:
                if daily_sum[key] < 0:
                    minus.append([daily_sum[key], key])
                else:
                    plus.append([daily_sum[key], key])
            plus.sort(key=lambda x: x[0])
            minus.sort(key=lambda x: x[0])
            str_minus, str_plus = '\n', '\n'
            for i in range(len(plus)):
                plus[i][0] = f"{round(plus[i][0], 4)}({round(plus[i][0] * 24 * 365, 1)}%)"
                str_plus += f"{plus[i][0]}    {plus[i][1]}\n"
            for i in range(len(plus)):
                minus[i][0] = f"{round(minus[i][0], 4)}({round(minus[i][0] * 24 * 365, 1)}%)"
                str_minus += f"{minus[i][0]}    {minus[i][1]}\n"

            if SEND_MESSAGE:
                bot.send_message(
                    channel_name,
                    f"Daily\n\n Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
            else:
                print(f"Daily\n\n Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
                print('-' * 20)
            with open('daily_sum.json', 'w') as f:
                f.write('{}')
            return
        except Exception as e:
            print('ERROR: ', e)


@bot.message_handler(commands=["start"])
def welcome(message):
    if message.chat.id == admin_id:
        bot.send_message(message.chat.id, 'Привет, я бот для оповещении об изменениях на сайте')


# get_data()

every().hour.at(f":{every_minutes}").do(get_data)
every().monday.at(every_week_mon_time).do(send_weekly_sum)
every().day.at(every_day_time).do(send_daily_sum)

th = Thread(target=work)
th.start()


if __name__ == '__main__':
    bot.infinity_polling()
