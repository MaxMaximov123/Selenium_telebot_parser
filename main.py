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
sum1 = check_sum


def work():
    while True:
        run_pending()
        time.sleep(0.5)


def get_data():
    while True:
        try:
            ua = dict(DesiredCapabilities.CHROME)
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            # options.add_argument('window-size=1920x935')
            # driver = webdriver.Chrome(chrome_options=options)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            driver.get('https://kwenta.eth.limo/dashboard/markets/')

            time.sleep(4)
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
                # print(fun.value_of_css_property('color'))
                add_zn = ''
                if fun.find_element_by_tag_name('span').value_of_css_property('color') == 'rgba(239, 104, 104, 1)':
                    add_zn = '- '
                    minus.append([add_zn + fun.text, titl.text.split('\n')[0]])
                else:
                    plus.append([add_zn + fun.text, titl.text.split('\n')[0]])
                exp_data.append([titl.text.split('\n')[0] + '\n\n', add_zn + fun.text])
            bot.send_message(
                admin_id, f"Longs pay Shorts if positive:\n{tabulate(plus)}\nShorts pay Longs if negative:\n{tabulate(minus)}")
            return
        except Exception as e:
            print("ERROR   ", e)
            time.sleep(120)



@bot.message_handler(commands=["start"])
def welcome(message):
    if message.chat.id == admin_id:
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        markup.add(types.KeyboardButton(text="Прочие данные"))
        bot.send_message(admin_id, 'Привет, я бот для оповещении об изменениях на сайте', reply_markup=markup)



@bot.message_handler(content_types=["text"])
def chat(message):
    if message.chat.id == admin_id and message.text == "Прочие данные":
        get_data()


get_data()
# every(every_minutes).minutes.do(get_data)
th = Thread(target=work)
th.start()


if __name__ == '__main__':
    bot.infinity_polling()
