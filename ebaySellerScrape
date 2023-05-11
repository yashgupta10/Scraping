import requests
#for HTML manipulation and pulling option chain
from bs4 import BeautifulSoup,SoupStrainer
import traceback
import pandas as pd
import calendar
import datetime
import time
import os
import re
import urllib.parse
import urllib
from urllib.request import Request,urlopen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
import winsound
from fake_useragent import UserAgent

ua = UserAgent()
username = os.getenv("USERNAME")
binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
fp = (r'C:\Users\Yash Gupta\AppData\Roaming\Mozilla\Firefox\Profiles\q7imc2hk.yashscrape')
opts = Options()
opts.profile = fp
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities["pageLoadStrategy"] = "normal"
opts.add_argument(f'user-agent=ua.chrome')
link = 'https://www.ebay.com.au/n/all-stores'
headers = {
        "User-Agent": ua.random,
    }

seller_links = []
seller_detail = []
error_list = []

# Get seller links
driver = webdriver.Firefox(capabilities=firefox_capabilities,firefox_binary=binary, options = opts)
driver.get(link)
soup = BeautifulSoup(driver.page_source, "html.parser")
for block in soup.find("div",{"id":"AB"}):
    for block2 in block.find_all("ul",{"class":"itemcols"}):
        for li in block2.find_all("li"):
            seller_links.append( {'seller_name': li.text,'seller_link':li.find("a")['href'] })
df_seller_links = pd.DataFrame(seller_links)
df_seller_links

#For every seller get detailed information
for link in df_seller_links['seller_link'].tolist():
    try:
        driver.get(link)
        driver.maximize_window()
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'str-seller-card')))
        except:
            print('Seller List not Found: ',link )
            winsound.Beep(2500, 1000)
            pass
        soup = BeautifulSoup(driver.page_source, "html.parser")
        element = soup.find("div",{"class": "str-seller-card"})
        search =  soup.find("label",{"class":"ui-helper-hidden-accessible","for":"search-static"})
        for i in element.find("div",{"class": "str-seller-card__stats"}):
            temp_list = []
            for j in i:
                temp_list.append(j.text)
        about = []
        for a in soup.find("div",{"class":"str-about-description about-layout--gutters"}).find("section",{"class":"str-about-description__seller-info"}):
            about.append(a.text)

        seller_detail.append({'seller_name':element.find("div",{"class": "str-seller-card__store-name"}).text,
                                   'seller_url':link,
                                   'seller_feedback': temp_list[0],
                                   'seller_items_sold':temp_list[1],
                                   'seller_followers':temp_list[2],
                                   'seller_search_items': re.sub(r"Search all\s*","", search.text),
                                   'seller_about_location': re.sub(r"^Location:\s*", "", about[0]),
                                   'seller_member_since':re.sub(r"Member since:\s*", "", about[1]),
                                    'seller_about_name':re.sub(r"Seller:\s*", "", about[2]) } )
    except:
        error_list.append(link)
        print('Error', link )
        pass 
seller_detail_df = pd.DataFrame(seller_detail)
seller_detail_df.drop_duplicates(inplace = True)
seller_detail_df
pd.DataFrame(seller_detail_df).to_csv('seller_detail_df.csv', index=False)
