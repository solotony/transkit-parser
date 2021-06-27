from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
import logging
from .globals import PROD
from pyvirtualdisplay import Display

class Bot:

    def sleep(self, t):
        if PROD:
            time.sleep(t)

    RANDOFFSETX = random.randint(10, 15)
    RANDOFFSETY = random.randint(10, 15)

    def __init__(self, starturl, prod_mode, driver, profile, hidden):
        self.display = None
        if hidden:
            self.display = Display(visible=0, size=(1280, 1024))
            self.display.start()
        self.prod_mode = prod_mode
        self.starturl = starturl
        if driver == 'CHROME':
            self.driver = webdriver.Chrome()
        elif driver == 'FF':
            from selenium.webdriver.firefox.options import Options #noqa

            options = Options()
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.download.dir", "./data")
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/json,text/plain,text/html,*/*")

            if profile is None:
                self.driver = webdriver.Firefox(firefox_options=options)
            else:
                self.driver = webdriver.Firefox(profile, firefox_options=options)
        self.driver.maximize_window()
        self.driver.get(self.starturl)


    def getstart(self):
        self.driver.get(self.starturl)


    def __del__(self):
        if self.display is not None:
            self.display.stop()

    def navigate(self, url):
        self.driver.navigate().to(url)


    def find(self, id=None, name=None, xpath=None, link_text=None, link_text_part=None, tag_name=None, klass=None):
        self.sleep(2)
        try:
            if id:
                element = self.driver.find_element_by_id(id)
                logging.debug('find ok element with id="{}"'.format(id))
                return element
            if klass:
                element = self.driver.find_element_by_class_name(klass)
                logging.debug('find ok element with class="{}"'.format(klass))
                return element
            if name:
                element = self.driver.find_element_by_name(name)
                logging.debug('find ok element with name="{}"'.format(name))
                return element
            if xpath:
                element = self.driver.find_element_by_xpath(xpath)
                logging.debug('find ok element with xpath="{}"'.format(xpath))
                return element
            if link_text:
                element = self.driver.find_element_by_link_text(link_text)
                logging.debug('find ok element with link_text="{}"'.format(link_text))
                return element
            if link_text_part:
                element = self.driver.find_element_by_partial_link_text(link_text_part)
                logging.debug('find ok element with link_text_part="{}"'.format(link_text_part))
                return element
            if tag_name:
                element = self.driver.find_element_by_tag_name(tag_name)
                logging.debug('find ok element with tag_name="{}"'.format(tag_name))
                return element
            else:
                logging.error('bad find_element params')
                return None
        except Exception as e:
            logging.error('find_element failed: {}'.format(str(e)))
            return None

    def scroll_shim(self, object, ybaseoffset=0):
        x = object.location['x']
        y = object.location['y'] + ybaseoffset
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        self.driver.execute_script(scroll_by_coord)
        self.driver.execute_script(scroll_nav_out_of_way)

    def move_to(self, element, element_name, scroll=False, randomize=0, ybaseoffset=0):
        logging.debug('move_to')
        logging.info('move_to')
        self.sleep(2)
        try:
            if scroll:
                location = element.location_once_scrolled_into_view
            else:
                location = element.location
            logging.debug('location of {} is {}'.format(element_name, str(location)))
        except Exception as e:
            logging.error('failed to get location of {}: {}'.format(element_name, str(e)))
            return False
        if randomize>1:
            steps = random.randint(2,randomize)
            logging.debug('randomize {} steps {}: '.format(randomize, steps))
            for step in reversed(range(1, steps+1)):
                actions = ActionChains(self.driver)
                x_offset = random.randint(-step*self.RANDOFFSETX,step*self.RANDOFFSETX)
                y_offset = random.randint(-step*self.RANDOFFSETY,step*self.RANDOFFSETY)
                try:
                    actions.move_to_element_with_offset(element, x_offset, y_offset+ybaseoffset)
                    actions.pause(random.random()*2)
                    actions.perform()
                    logging.debug('+({},{})'.format(x_offset, y_offset))
                except Exception as e:
                    logging.debug('x({},{})'.format(x_offset, y_offset))
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(element, 1, ybaseoffset+1)
            actions.pause(random.random()*2)
            actions.perform()
            logging.debug('moved to {}'.format(element_name))
            return True
        except Exception as e:
            logging.debug('retry with scroll'.format(element_name, str(e)))
        self.scroll_shim(element)
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.random()*2)
            actions.perform()
            logging.debug('moved (with scrioll) to {}'.format(element_name))
            return True
        except Exception as e:
            logging.error('failed to move to {}: {}'.format(element_name, str(e)))
            return False

    def click_at(self, element, element_name):
        self.sleep(2)
        try:
            # #ActionChains(self.driver).move_to_element(element).click().pause(3).perform()
            # self.driver.click(element)
            element.click()
            logging.debug('clicked at {}'.format(element_name))
            return True
        except Exception as e:
            pass

        try:
            self.send_keys_to_body(Keys.PAGE_UP)
            element.click()
            logging.debug('clicked at {}'.format(element_name))
            return True
        except Exception as e:
            pass

        try:
            self.send_keys_to_body(Keys.PAGE_DOWN)
            element.click()
            logging.debug('clicked at {}'.format(element_name))
            return True
        except Exception as e:
            pass

        try:
            self.send_keys_to_body(Keys.PAGE_DOWN)
            element.click()
            logging.debug('clicked at {}'.format(element_name))
            return True
        except Exception as e:
            logging.error('failed to click at {}: {}'.format(element_name, str(e)))
            return False



    def send_keys_to(self, element, element_name, keys):
        self.sleep(2)
        try:
            element.send_keys(keys)
            logging.debug('send keys to {}'.format(element_name))
            return True
        except Exception as e:
            logging.error('failed to send keys to {}: {}'.format(element_name, str(e)))
            return False

    def send_keys_to_body(self, keys):
       return self.send_keys_to(self.driver.find_element_by_tag_name('body'), 'body', keys)


    def create_soup(self, element=None, element_name=None):
        if element:
            try:
                data = element.get_attribute('outerHTML')
                soup = BeautifulSoup(data, 'html5lib')
                logging.debug('init BeautifulSoup from {}'.format(element_name))
                return soup
            except Exception as e:
                logging.error('failed init BeautifulSoup from {}: {}'.format(element_name, str(e)))
                return None
        else:
            try:
                data = self.driver.page_source
                soup = BeautifulSoup(data, 'html5lib')
                logging.debug('init BeautifulSoup from page_sorce')
                return soup
            except Exception as e:
                logging.error('failed to init BeautifulSoup from page_sorce: {}'.format(str(e)))
                return None

    def back(self):
        self.driver.back()


    def move_to_random(self, randomize=5):
        links = self.driver.find_elements_by_tag_name('a')
        if not links or not len(links):
            return False
        link = random.choice(links)
        return self.move_to(link, randomize)

    def find_all(self, *, klass=None):
        self.sleep(2)
        try:
            if klass:
                elements = self.driver.find_elements_by_class_name(klass)
                logging.debug('find ok elements with class="{}"'.format(klass))
                return elements
        except Exception as e:
            logging.error('find_element failed: {}'.format(str(e)))
            return None