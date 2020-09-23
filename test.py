from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
#from selenium.


class MyProfile(webdriver.firefox.firefox_profile.FirefoxProfile):
#class MyProfile(FirefoxProfile):
    @property
    def path(self):
        #path = "/home/pi/.mozilla/firefox/ntuqt8cq.default-esr"
        path = "/home/pi/.mozilla/firefox/"
        return path

#driver = webdriver.Firefox(firefox_profile=MyProfile())
driver = webdriver.Firefox(FirefoxProfile("/home/pi/.mozilla/firefox/ofvss46d.default-esr"))
#driver = webdriver.Firefox()

driver.get("https://solotony.com")
driver.maximize_window()
