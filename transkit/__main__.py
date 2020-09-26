import random
import sys
from transkit.bot import Bot
import requests
import logging
import pytz
from datetime import datetime, timezone, tzinfo
import json

from .globals import PROD, DRIVER, PROFILE, DELAY_MIN, DELAY_MAX

LOGIN = 'arttronic' if PROD else 'login'
PASSWORD = 'ndef53' if PROD else 'password'

NUM_COMPARE_MIN = 3
NUM_COMPARE_MAX = 5 # максимально - 20
VIEW_TRESHOLD = 0.041 # от 0 до 1
COMPARE_TRESHOLD = 0.019 # от 0 до 1
RANDOM_MOVE_TRESHOLD = 0.073 # от 0 до 1
HEADEROFFSET=-170

local_day = datetime.now().astimezone(tz=pytz.timezone('Europe/Moscow')).strftime('%Y%m%d')

def failed(text):
    logging.error(text)
    exit(0)
    pass

def main(args):
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
    logging.basicConfig( filename="log/transkit-parse-{}.log".format(datetime.now().strftime('%Y%m%d%H%M')), level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger().addHandler(console)

    if len(args) < 2:
        failed('формат запуска: python -m transkit shedule|<имя_файла>')

    transmissions = []

    if args[1]=='shedule':
        logging.info('Загружаем расписание')
        try:
            ulr = 'https://mskakpp.ru/parsers/transkit-shedule/{}/'.format(local_day)
            r = requests.get(ulr)
            if r.status_code!=200:
                failed('Ошибка получения данных с сервера: {}'.format(r.status_code))
            print(json.loads(r.text))
        except Exception as e:
            failed('Ошибка при получения данных с сервера: {}'.format(str(e)))
    else:
        with open(args[1], 'r') as transmissions_file:
            transmissions = [row.strip() for row in transmissions_file]

    logging.info('Начинаем сканирование')
    ulr = 'https://mskakpp.ru/parsers/transkit-start/{}/'.format(local_day)
    requests.post(ulr)

    exit(0)

    bot = Bot('http://www.transkit.ru/', PROD, DRIVER, PROFILE)

    if bot.find(id='menuIconAccountActiveArea'):
        logging.info('  уже залогинены')
    else:
        logging.info('  надо логиниться')
        process_login(bot)

        if PROD:
            if bot.find(id='menuIconAccountActiveArea'):
                logging.info('  надо логиниться')
            else:
                logging.critical('логин ахтунг!!!!!!!!!!!!')
                exit('логин ахтунг!!!!!!!!!!!!')

    first = True
    for transmission in transmissions:
        if not first:
            bot.sleep(random.randint(DELAY_MIN, DELAY_MAX))
        first = False
        logging.info('начинаем коробку {}'.format(transmission))
        process_transmission(bot, transmission)
        logging.info('завершена коробка {}'.format(transmission))

    logging.info('завершено сканирование')
    ulr = 'https://mskakpp.ru/parsers/transkit-stop/{}/'.format(local_day)
    requests.post(ulr)

def do_compare(bot):
    logging.info('Выполняется сравнение')

    compare_button = bot.find(xpath='//td[@id="topMenuCMPButton"]/a')
    if not compare_button:
        logging.error('  Не удается найти кнопку перехода в сравнение')
        return False

    bot.move_to(compare_button, 'compare_button', scroll=False, randomize=5, ybaseoffset=HEADEROFFSET)
    bot.click_at(compare_button, 'compare_button')

    clean_link = bot.find(link_text_part='Очистить список сравнения')

    if not clean_link:
        logging.error('  не удается найти кнопку очистки сравнения')
        bot.back()
        return False

    logging.info('Очистка сравнения')
    bot.move_to(clean_link, 'clean_link', scroll=False, randomize=5)
    bot.click_at(clean_link, 'clean_link')
    bot.sleep(random.randint(7, 15))
    bot.back()
    bot.back()
    return True

def do_view(bot, part_name):
    logging.info('Выполняется просмотр запчасти')
    a_link = bot.find(link_text=part_name)
    if not a_link:
        logging.error('ссылка на страницу запчасти не найдена')
        return False

    bot.move_to(a_link, 'a_link', scroll=False, randomize=5)
    bot.click_at(a_link, 'a_link')
    back_button = bot.find(xpath='//*[@id="pagecontent"]/button')
    bot.sleep(random.randint(7, 15))
    bot.move_to(back_button, 'back_button', scroll=False, randomize=5)
    bot.click_at(back_button, 'back_button')

    return True

def process_login(bot):
    logging.debug('PROD={}'.format(PROD))

    button_link = bot.find(id='hiddenAuthBut')
    if not button_link:
        failed('Не могу найти кнопку для открытия формы входа')

    bot.move_to(button_link, 'button_link', scroll=False, randomize=5)
    bot.click_at(button_link, 'button_link')

    login_input = bot.find(id='login')
    if not button_link:
        failed('Не могу найти поле для логина')

    password_input = bot.find(name='password')
    if not button_link:
        failed('Не могу найти поле для пароля')

    button_enter = bot.find(xpath='//button[text()="Войти"]')
    if not button_link:
        failed('Не могу найти кнопку "войти"')

    if PROD:
        logging.info('do login')

        bot.move_to(login_input, 'login_input', scroll=False, randomize=5)
        login_input.clear()
        bot.send_keys_to(login_input, 'login_input', LOGIN)

        bot.move_to(password_input, 'password_input', scroll=False, randomize=5)
        password_input.clear()
        bot.send_keys_to(password_input, 'password_input', PASSWORD)

        bot.move_to(button_enter, 'button_enter', scroll=False, randomize=5)
        bot.click_at(button_enter, 'button_enter')
    else:
        logging.info('login skipped')

    return True

def process_transmission(bot, transmission):
    transmission = transmission.strip()
    if not transmission:
        logging.error('Коробка не указана')
        return False

    bot.sleep(random.randint(7, 15))

    logging.info('начинаем коробку {}'.format(transmission))
    num_compare = 0

    search_input = bot.find(id='dsch')
    if not search_input:
        failed('Не могу найти поле поиска')

    search_button = None

    if not PROD:
        search_button = bot.find(xpath='//*[@id="pnSearchForm"]/table/tbody/tr/td[2]/input')
    else:
        search_button = bot.find(id='pnSearchFormButton')

    if not search_button:
        logging.critical('Не могу кнопку поиска')
        failed('Не могу кнопку поиска')

    bot.move_to(search_input, 'search_input', scroll=False, randomize=5)
    search_input.clear()
    bot.send_keys_to(search_input, 'search_input', transmission)

    bot.move_to(search_button, 'search_button', scroll=False, randomize=5)
    bot.click_at(search_button, 'search_button')

    view_mode_button = bot.find(xpath='//*[@title="Показать все детали трансмиссии в виде таблицы"]')
    if not view_mode_button:
        transmission_link = bot.find(xpath='//a[text()="{}"]'.format(transmission))
        bot.move_to(transmission_link, 'transmission_link', scroll=False, randomize=5)
        bot.click_at(transmission_link, 'transmission_link')
        view_mode_button = bot.find(xpath='//*[@title="Показать все детали трансмиссии в виде таблицы"]')
        if not view_mode_button:
            transmission_search_link = bot.find(xpath='//p[text()="Трансмиссия"]')
            bot.move_to(transmission_search_link, 'transmission_search_link', scroll=False, randomize=5)
            bot.click_at(transmission_search_link, 'transmission_search_link')
            view_mode_button = bot.find(xpath='//*[@title="Показать все детали трансмиссии в виде таблицы"]')
            if not view_mode_button:
                transmission_link = bot.find(xpath='//a[text()="{}"]'.format(transmission))
                bot.move_to(transmission_link, 'transmission_link', scroll=False, randomize=5)
                bot.click_at(transmission_link, 'transmission_link')
                view_mode_button = bot.find(xpath='//*[@title="Показать все детали трансмиссии в виде таблицы"]')
                if not view_mode_button:
                    logging.error('кнопка режима просмотра не найдена')
                    return False

    bot.click_at(view_mode_button, 'view_mode_button')

    soup = bot.create_soup()
    tag_table = soup.find('table', attrs={'id': 'detailstable'})
    if not tag_table:
        logging.error('таблица деталей не найдена')
        return False

    parts = []
    for tag_tr in tag_table.findChildren('tr', recursive=True):
        tag_tr_class = tag_tr.get('class')
        if tag_tr_class and 'transtabletopbg' in tag_tr_class:
            logging.info('  пропускаем заголовок таблицы')
            continue

        # if tag_tr.find('button', attrs={'class': 'emailMe'}, recursive=True):
        #     logging.info('  пропускаем деталь нет в наличии')

        articul, cmp_div_id, cmp_calc_price, price_at_page = None, None, None, None
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

        for tag_td in tag_tr.findChildren('td', attrs={'class': 'spanPrice'}, recursive=False):
            price_at_page = tag_td.text
            break


        if articul:
            parts.append((articul, cmp_div_id, cmp_calc_price, price_at_page))
            logging.info('  найден компонент {} ({}) '.format(articul, price_at_page))

    for counter, part in enumerate(parts):
        if part[3]:
            if PROD:
                data = {
                    'transmission': transmission,
                    'partno': part[0],
                    'price': part[3],
                    'token': 'x777xx777x'
                }
                r = requests.post('https://mskakpp.ru/catalog/api/update-transkit/', json=data)
                logging.info('update: {}'.format(str(data)))

    for counter,part in enumerate(parts):

        if random.random() < RANDOM_MOVE_TRESHOLD:
            bot.move_to_random()

        logging.info('Обрабатываем деталь `{}` `{}` `{}`'.format(part[0],part[1],part[2]))

        if random.random() <= VIEW_TRESHOLD:
            do_view(bot, part[0])

        if random.random() <= COMPARE_TRESHOLD:
            cmp_input = bot.find(xpath='//*[@id="{}"]/form/input[3]'.format(part[1]))
            if cmp_input:
                logging.info('  найдена кнопка "в сравнение"')
                bot.move_to(cmp_input, 'cmp_input', scroll=False, randomize=5, ybaseoffset=HEADEROFFSET)
                bot.click_at(cmp_input, 'cmp_input')
                num_compare += 1
            else:
                logging.error('  не найдена кнопка "в сравнение"')

            if num_compare >= random.randint(NUM_COMPARE_MIN, NUM_COMPARE_MAX):
                if do_compare(bot):
                    num_compare = 0

        if part[3]:
            pass
        elif part[2]:
            bot.sleep(random.randint(1, 3))
            price_span = bot.find(id=part[2])
            if not price_span:
                logging.error('  не найден элемент рассчитать {}'.format(part[2]))
            else:
                bot.move_to(price_span, 'price_span', scroll=False, randomize=5, ybaseoffset=HEADEROFFSET)
                bot.click_at(price_span, 'price_span')
                price_span = bot.find(xpath='//span[@id="{}"]/span'.format(part[2]))
                if not price_span:
                    logging.error('  не найден элемент с ценой для {}'.format(part[2]))
                else:
                    if PROD:
                        price = price_span.get_attribute('innerHTML')
                        logging.debug('  YAHOO {}:{}'.format(part[0], price))
                        data = {
                            'transmission': transmission,
                            'partno': part[0],
                            'price': price,
                            'token':'x777xx777x'
                        }
                        r = requests.post('https://mskakpp.ru/catalog/api/update-transkit/', json=data)
                        logging.info('update: {}'.format(str(data)))
        else:
            if PROD:
                data = {
                    'transmission': transmission,
                    'partno': part[0],
                    'price': 0,
                    'token': 'x777xx777x'
                }
                r = requests.post('https://mskakpp.ru/catalog/api/update-transkit/', json=data)
                logging.info('update: {}'.format(str(data)))

    # полюбому перед выходом!!
    if num_compare >= 1:
        do_compare(bot)

    return True

if __name__ == '__main__':
    main(sys.argv)

# YAHOO !