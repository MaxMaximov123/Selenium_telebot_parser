from pprint import pprint
from schedule import every, run_pending
import telebot
from config import *
from threading import Thread
import time
from selenium import webdriver
from telebot import types
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from tabulate import tabulate


bot = telebot.TeleBot(token)


def work():
    while True:
        run_pending()
        time.sleep(0.5)


def get_data():
    while True:
        try:
            print("запуск")
            ua = dict(DesiredCapabilities.CHROME)
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            # options.add_argument('window-size=1920x935')
            # driver = webdriver.Chrome(chrome_options=options)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            driver.get('https://kwenta.eth.limo/dashboard/markets/')

            time.sleep(5)
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
            str_plus, str_minus = '\n', '\n'
            for i in range(len(plus)):
                plus[i][0] = f"{round(plus[i][0], 4)}({round(plus[i][0] * 24 * 365, 1)}%)"
                str_plus += f"{plus[i][0]}    {plus[i][1]}\n"
            for i in range(len(plus)):
                minus[i][0] = f"{round(minus[i][0], 4)}({round(minus[i][0] * 24 * 365, 1)}%)"
                str_minus += f"{minus[i][0]}    {minus[i][1]}\n"
            # print(f"Longs pay Shorts if positive:\n {str_plus}\nShorts pay Longs if negative:\n {str_minus}")
            bot.send_message(
                channel_name, f"Longs pay Shorts if positive:\n{str_plus}\nShorts pay Longs if negative:\n{str_minus}")
            return
        except Exception as e:
            print("ERROR   ", e)


@bot.message_handler(commands=["start"])
def welcome(message):
    if message.chat.id == admin_id:
        bot.send_message(message.chat.id, 'Привет, я бот для оповещении об изменениях на сайте')


# get_data()
every().hour.at(f":{every_minutes}").do(get_data)
th = Thread(target=work)
th.start()


if __name__ == '__main__':
    bot.infinity_polling()
