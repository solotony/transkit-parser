from selenium.common.exceptions import MoveTargetOutOfBoundsException
import random
from bs4 import BeautifulSoup
import time
import re
import os
import sys
from transkit.bot import Bot
from bs4 import BeautifulSoup

PROD = 1

LOGIN = 'arttronic' if PROD else 'login'
PASSWORD = 'ndef53' if PROD else 'password'
TEST = 0 if PROD else 1

NUM_COMPARE_MIN = 3
NUM_COMPARE_MAX = 5 # максимально - 20
VIEW_TRESHOLD = 0 # от 0 до 1
COMPARE_TRESHOLD = 0 # от 0 до 1
RANDOM_MOVE_TRESHOLD = 0 # от 0 до 1
HEADEROFFSET=-170

TRANSMISSIONS = ['CVT2M','DCT-7G (724.0)','DCT250 (DSG)','DCT450 (DSG)','DCT470 (DSG)','DPO, AL4','E-18C','E4N71B','E4OD','F1C1 (CVT)']
#TRANSMISSIONS = ['DPO, AL4', 'E4OD']

def main(args):
    transmission = random.choice(TRANSMISSIONS)

    bot = Bot('http://www.transkit.ru/')

    if bot.find(id='menuIconAccountActiveArea'):
        print('  INFO уже залогинены')
    else:
        print('  INFO надо логиниться')
        process_login(bot)
        if bot.find(id='menuIconAccountActiveArea'):
            print('  INFO залогинены успешно')
        else:
            exit('  CRITICAL логин ахтунг!!!!!!!!!!!!')

    process_transmission(bot, transmission)

def do_compare(bot):
    print('Выполняется сравнение')

    compare_button = bot.find(xpath='//td[@id="topMenuCMPButton"]/a')
    if not compare_button:
        print('  ERROR Не удается найти кнопку перехода в сравнение')
        return False

    bot.move_to(compare_button, 'compare_button', scroll=False, randomize=5, ybaseoffset=HEADEROFFSET)
    bot.click_at(compare_button, 'compare_button')

    clean_link = bot.find(link_text_part='Очистить список сравнения')

    if not clean_link:
        print('  ERROR не удается найти кнопку очистки сравнения')
        bot.back()
        return False

    print('Очистка сравнения')
    bot.move_to(clean_link, 'clean_link', scroll=False, randomize=5)
    bot.click_at(clean_link, 'clean_link')
    bot.back()
    bot.back()
    return True

def do_view(bot, part_name):
    print('Выполняется просмотр запчасти')
    a_link = bot.find(link_text=part_name)
    if not a_link:
        print('  ERROR ссылка на страницу запчасти не найдена')
        return False

    bot.move_to(a_link, 'a_link', scroll=False, randomize=5)
    bot.click_at(a_link, 'a_link')
    back_button = bot.find(xpath='//*[@id="pagecontent"]/button')
    bot.move_to(back_button, 'back_button', scroll=False, randomize=5)
    bot.click_at(back_button, 'back_button')

    return True

def process_login(bot):
    print('TEST={}'.format(TEST))

    button_link = bot.find(id='hiddenAuthBut')
    if not button_link:
        exit('  CRITICAL Не могу найти кнопку для открытия формы входа')

    bot.move_to(button_link, 'button_link', scroll=False, randomize=5)
    bot.click_at(button_link, 'button_link')

    login_input = bot.find(id='login')
    if not button_link:
        exit('  CRITICAL Не могу найти поле для логина')

    password_input = bot.find(name='password')
    if not button_link:
        exit('  CRITICAL Не могу найти поле для пароля')

    button_enter = bot.find(xpath='//button[text()="Войти"]')
    if not button_link:
        exit('  CRITICAL Не могу найти кнопку "войти"')

    if not TEST:
        bot.move_to(login_input, 'login_input', scroll=False, randomize=5)
        bot.send_keys_to(login_input, 'login_input', LOGIN)

        bot.move_to(password_input, 'password_input', scroll=False, randomize=5)
        bot.send_keys_to(password_input, 'password_input', PASSWORD)

        bot.move_to(button_enter, 'button_enter', scroll=False, randomize=5)
        bot.click_at(button_enter, 'button_enter')



    return True


def process_transmission(bot, transmission):
    print('Коробка {}'.format(transmission))
    num_compare = 0

    search_input = bot.find(id='dsch')
    if not search_input:
        exit('  CRITICAL Не могу найти поле поиска')

    search_button = None

    if TEST:
        search_button = bot.find(xpath='//*[@id="pnSearchForm"]/table/tbody/tr/td[2]/input')
    else:
        search_button = bot.find(id='pnSearchFormButton')

    if not search_button:
        exit('  CRITICAL Не могу кнопку поиска')

    bot.move_to(search_input, 'search_input', scroll=False, randomize=5)
    bot.send_keys_to(search_input, 'search_input', transmission)

    bot.move_to(search_button, 'search_button', scroll=False, randomize=5)
    bot.click_at(search_button, 'search_button')

    view_mode_button = bot.find(xpath='//*[@title="Показать все детали трансмиссии в виде таблицы"]')
    bot.click_at(view_mode_button, 'view_mode_button')

    soup = bot.create_soup()
    tag_table = soup.find('table', attrs={'id': 'detailstable'})
    if not tag_table:
        print('  ERROR таблица деталей не найдена')
        return False

    parts = []
    for tag_tr in tag_table.findChildren('tr', recursive=True):
        tag_tr_class = tag_tr.get('class')
        if tag_tr_class and 'transtabletopbg' in tag_tr_class:
            print('  INFO пропускаем заголовок таблицы')
            continue

        if tag_tr.find('button', attrs={'class': 'emailMe'}, recursive=True):
            print('  INFO пропускаем деталь нет в наличии')
            continue

        articul, cmp_div_id, cmp_calc_price = None, None, None
        for counter, tag_td in enumerate(tag_tr.findChildren('td', recursive=False)):
            if counter == 1:
                tag_a = tag_td.find('a')
                if tag_a:
                    articul = ','.join([x.strip() for x in tag_a.text.split(',')])
            if counter == 5:
                tag_div = tag_td.find('div')
                if tag_div:
                    cmp_div_id = tag_div.attrs["id"]
            if counter == 7:
                tag_span = tag_td.find('span', attrs={'class': 'calcPrice'},  recursive=False)
                if tag_span:
                    cmp_calc_price = tag_span.attrs["id"]

        if articul:
            parts.append((articul, cmp_div_id, cmp_calc_price))
            print('  INFO найден компонент {} '.format(articul))


    for counter,part in enumerate(parts):

        if random.random() < RANDOM_MOVE_TRESHOLD:
            bot.move_to_random()

        print('Обрабатываем деталь `{}` `{}` `{}`'.format(part[0],part[1],part[2]))

        if random.random() <= VIEW_TRESHOLD:
            do_view(bot, part[0])

        if random.random() <= COMPARE_TRESHOLD:
            cmp_input = bot.find(xpath='//*[@id="{}"]/form/input[3]'.format(part[1]))
            if cmp_input:
                print('  INFO найдена кнопка "в сравнение"')
                bot.move_to(cmp_input, 'cmp_input', scroll=False, randomize=5, ybaseoffset=HEADEROFFSET)
                bot.click_at(cmp_input, 'cmp_input')
                num_compare += 1
            else:
                print('  ERROR не найдена кнопка "в сравнение"')

            if num_compare >= random.randint(NUM_COMPARE_MIN, NUM_COMPARE_MAX):
                if do_compare(bot):
                    num_compare = 0

        price_span = bot.find(id=part[2])
        bot.move_to(price_span, 'price_span', scroll=False, randomize=5, ybaseoffset=HEADEROFFSET)
        bot.click_at(price_span, 'price_span')
        price_span = bot.find(xpath='//span[@id="{}"]/span'.format(part[2]))
        price = price_span.get_attribute('innerHTML')
        print('  YAHOO {}:{}'.format(part[0], price))


    # полюбому перед выходом
    if num_compare >= 1:
        do_compare(bot)

    return True

if __name__ == '__main__':
    main(sys.argv)
