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
print('1 OK')
display.start()
print('2 OK')
driver = webdriver.Firefox()
print('3 OK')
driver.maximize_window()
print('4 OK')
driver.get("https://solotony.com/tools/ip/")
print('5 OK!!!')
display.stop()
print('6 OK')