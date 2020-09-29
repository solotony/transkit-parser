from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from pyvirtualdisplay import Display


class MyProfile(webdriver.firefox.firefox_profile.FirefoxProfile):
#class MyProfile(FirefoxProfile):
    @property
    def path(self):
        #path = "/home/pi/.mozilla/firefox/ntuqt8cq.default-esr"
        path = "/home/pi/.mozilla/firefox/"
        return path

#driver = webdriver.Firefox(firefox_profile=MyProfile())
#driver = webdriver.Firefox(FirefoxProfile("/home/pi/.mozilla/firefox/ofvss46d.default-esr"))
display = Display(visible=0, size=(1280, 1024))
display.start()

driver = webdriver.Firefox()
driver.maximize_window()
driver.get("https://solotony.com/tools/ip/")

display.stop()