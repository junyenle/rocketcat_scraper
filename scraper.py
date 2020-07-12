import cssutils, time, queue, json
import atexit
from bs4 import BeautifulSoup
from splinter.browser import Browser
from splinter import exceptions
import selenium.common
import sys
from selenium.webdriver.common.keys import Keys
import time

browser = Browser('firefox', headless=False)
try:
    # visit site
    browser.visit("https://open.rocket.chat/")
    
    # log in manually for now because nobody gave me login info
    input("press return to continue once logged in")
    
    channels = ["general", "sandbox"]
    for channel in channels:
        # create output file
        rawfile = open("data/{}_raw.txt".format(channel), "w+")
        parsedfile = open("data/{}_parsed".format(channel), "w+")
        browser.visit("https://open.rocket.chat/channel/{}".format(channel))
        time.sleep(10)
        
        # scroll up to load previous messages
        # i have not figured out a way to detect when the channel is completely loaded
        # mostly because i am lazy and it doesnt really matter
        # so i just put 300 as a safe number
        # if it's too low, increase it. if it's too high (takes too long) decrease it
        # in any case it only takes 15 minutes to do 300 scrolls
        for i in range(300):
            browser.execute_script("document.querySelector('.messages-box .wrapper').scrollTo(0, -document.querySelector('.messages-box .wrapper').scrollHeight);")
            # for scroll loading time because rocket chat is a slow ass piece of shit
            time.sleep(3)
            
            
        # scrape raw file
        wrapper = browser.find_by_css('.messages-box .wrapper')
        html = BeautifulSoup(wrapper.html, 'html.parser')
        # use .replace('\\n', ' ').replace('\\t', '').replace('\\', '') to parse this
        rawfile.write(str(html.text.encode('unicode-escape')))
        
        # scrape parsed data 
        data = []
        wrapper = browser.find_by_css('.messages-box .wrapper .message')
        i = 0
        while True:
            try:
                thisdata = wrapper[i]
                thisdataparsed = []
                thisdataparsed.append(thisdata._element.get_attribute('data-date').strip())
                thisdatatextsplit = thisdata.text.split('\n')
                for j in range(len(thisdatatextsplit)):
                    thisdataparsed.append(str(thisdatatextsplit[j].strip().encode('unicode-escape')).replace('\\n', ' ').replace('\\t', '').replace('\\', '').strip("'").strip("b'"))
                data.append(thisdataparsed)
                i += 1
            except exceptions.ElementDoesNotExist:
                break
            except:
                print("bad data: {}".format(thisdatatextsplit))
                continue
        for k in range(i):
            parseddata = data[k]
            for m in range(len(parseddata)):
                parsedfile.write(data[k][m])
                parsedfile.write('\n')
            parsedfile.write('\n')
        
        print("finished scraping {} messages from {}".format(i, channel))
        
except selenium.common.exceptions.TimeoutException:
    print("timeout exception")
except selenium.common.exceptions.WebDriverException as e:
    print(e)