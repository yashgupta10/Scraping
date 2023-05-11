import requests
from bs4 import BeautifulSoup , SoupStrainer
import traceback
import pandas as pd
import calendar
import datetime
import time
import winsound
import os
import re
import urllib.parse
import urllib
from urllib.request import Request, urlopen
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

from fake_useragent import UserAgent


frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second


ua = UserAgent()
username = os.getenv("USERNAME")
binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
fp = (r'C:\Users\Yash Gupta\AppData\Roaming\Mozilla\Firefox\Profiles\q7imc2hk.yashscrape')
opts = Options()
opts.profile = fp
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities["pageLoadStrategy"] = "normal"
opts.add_argument(f'user-agent=ua.chrome')

# headers = {
#         "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Accept-Encoding": "gzip, deflate",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "Sec-Fetch-Dest": "document",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-Site": "none",
#         "Sec-Fetch-User": "?1",
#         "Cache-Control": "max-age=0",
#         "Referer": "https://www.google.com/"
#     }
headers = {
        "User-Agent": ua.random,
    }
driver = webdriver.Firefox(capabilities=firefox_capabilities,firefox_binary=binary, options = opts)

#Get Departments
department_list = []
baseUrl ="https://www.amazon.com.au/gp/bestsellers/"
driver.get(baseUrl)
driver.maximize_window()
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, '_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz')))
except:
    print('Department List not Found')
    pass


soup = BeautifulSoup(driver.page_source, "html.parser")
departments = soup.find_all("div", {"class":"_p13n-zg-nav-tree-all_style_zg-browse-group__88fbz"})
for links in departments[0].select('a[href^="/gp"]'):
    department_list.append({'dept_name':links.text,'dept_link':'https://www.amazon.com.au'+links.get("href")})
department_list_df = pd.DataFrame(department_list)
department_list_df = department_list_df[~department_list_df['dept_name'].str.contains('Amazon')]
department_list_df = department_list_df[~department_list_df['dept_name'].str.contains('Audible')]
department_list_df = department_list_df[~department_list_df['dept_name'].str.contains('Apps & Games')]
department_list_df = department_list_df[~department_list_df['dept_name'].str.contains('Kindle')]
department_list_df = department_list_df[~department_list_df['dept_name'].str.contains('Gift Cards')]
department_list_df

#Get Product List per deparment
product_list = []
for dept_name,department_link in zip(department_list_df['dept_name'],department_list_df['dept_link']):
    baseUrl =department_link
    driver.get(baseUrl)
    driver.maximize_window()
    #driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    driver.execute_async_script(
                """
            count =3000;
            let callback = arguments[arguments.length - 1];
            t = setTimeout(function scrolldown(){
                window.scrollTo(0, count);
                if(count < (document.body.scrollHeight || document.documentElement.scrollHeight)){
                  count+= 1000;
                  t = setTimeout(scrolldown, 1000);
                }else{
                  callback((document.body.scrollHeight || document.documentElement.scrollHeight));
                }
            }, 1000);"""
            )
    try:
        last_product = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'p13n-asin-index-49')))
        driver.execute_script("arguments[0].scrollIntoView();", last_product)
    except:
        print('Product List not Found')
        pass


    soup = BeautifulSoup(driver.page_source, "html.parser")
    best_products = soup.find("div",{"class":"p13n-desktop-grid"}).find_all("div", {"class":"p13n-sc-uncoverable-faceout"})
    for product in best_products:
        product_list.append( {'dept_name': dept_name,
                              'product_link':'https://www.amazon.com.au/'+((product.select('a[href^="/"]'))[0])['href'],
                              'product_id':product.attrs['id'],
                              'product_name': (product.select('a[href^="/"]'))[1].text,
                             })


    next_button = soup.select_one('.a-last > a')
    if next_button and "disabled" not in next_button.attrs.get('class', ''):
        next_url = "https://www.amazon.com.au" + next_button['href'] 
        driver.get(next_url)
        driver.maximize_window()
        driver.execute_async_script(
                """
            count =3000;
            let callback = arguments[arguments.length - 1];
            t = setTimeout(function scrolldown(){
                console.log(count, t);
                window.scrollTo(0, count);
                if(count < (document.body.scrollHeight || document.documentElement.scrollHeight)){
                  count+= 1000;
                  t = setTimeout(scrolldown, 1000);
                }else{
                  callback((document.body.scrollHeight || document.documentElement.scrollHeight));
                }
            }, 1000);"""
            )
        try:
            last_product = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, 'p13n-asin-index-49')))
            driver.execute_script("arguments[0].scrollIntoView();", last_product)
        except:
            print('Product List not Found')
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        best_products = soup.find("div",{"class":"p13n-desktop-grid"}).find_all("div", {"class":"p13n-sc-uncoverable-faceout"})
        for product in best_products:
            product_list.append( {'dept_name': dept_name,
                              'product_link':'https://www.amazon.com.au/'+((product.select('a[href^="/"]'))[0])['href'],
                              'product_id':product.attrs['id'],
                              'product_name': (product.select('a[href^="/"]'))[1].text,
                             })
product_list_df = pd.DataFrame(product_list)
product_list_df

#Get details from product page
#handle -- seee all buying options
#seller_list = []
for product_id,product_link in zip(product_list_df_filter['product_id'],product_list_df_filter['product_link']):
    try:
        driver.get(product_link)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        soup1 = BeautifulSoup((requests.get(url=product_link, headers=headers)).text, 'html.parser')
    except:
        time.sleep(10)
        winsound.Beep(frequency, duration)
        driver = webdriver.Firefox(capabilities=firefox_capabilities,firefox_binary=binary, options = opts)
        continue
    driver.maximize_window()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'bylineInfo_feature_div')))
    except:
        print(product_id, 'Page not Found')
        pass

    counter = 0 
    brand = None
    category = None
    dept_hierarchy = ""
    try:
        brand = (soup.find("div",{"id":"bylineInfo_feature_div"})).find("div",{"class":"a-section a-spacing-none"}).text
    except:
        print(product_id, 'Brand not Found')
        pass

    try:
        category = soup1.find("div",{"id":"detailBulletsWrapper_feature_div"}).find_all("ul",{"class":"a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"})[1].find("span",{"class":"a-list-item"}).text
        category = re.sub(r'\s*\([^)]*\)\s*', ' > ', category)
    except:
        pass
    try:
        for tr in soup1.find("div",{"id":"productDetails_db_sections"}).find("table",{"id":"productDetails_detailBullets_sections1"}):
            if (tr.find('th').text).strip() == "Best Sellers Rank":
                category = tr.find('td').text  
                category = re.sub(r'\s*\([^)]*\)\s*', ' > ', category)
    except:
        pass

    try:
        for i in soup.find("div",{"id":"wayfinding-breadcrumbs_feature_div"}).find_all("a"):
            dept_hierarchy = dept_hierarchy+(i.text).strip()+ " >>" 
    except:
        print(product_id, 'Hierarchy not Found')
        pass


    # Regular buybox
    try:
        seller_id = re.search(r'seller=([A-Z0-9]+)', (soup.find("div",{"class":"tabular-buybox-container"}).find("a", {"id":"sellerProfileTriggerId"})).get("href")).group(1)
        seller_list.append({'prod_name':product_id,'seller_id':seller_id,'primary':True ,'dept_hierarchy':dept_hierarchy,
                            'brand': brand, 'category':category})
        counter+=1
    except:
        pass
    # Other Sellers
    if soup.find_all("span",{"class":"a-size-small mbcMerchantName"}):
        a = ActionChains(driver)
        for element in (driver.find_element(By.ID, "mbc")).find_elements(By.CLASS_NAME,"a-box"):
            if "mbc-offer-added-to-cart" in element.get_attribute('innerHTML'):
                driver.execute_script("arguments[0].scrollIntoView();", element)
                a.move_to_element(element).click().perform()
        for element in (driver.find_elements(By.CLASS_NAME,"a-popover")):
            try:
                seller_list.append({'prod_name':product_id,
                                    'seller_id':re.search(r'seller=([A-Z0-9]+)',element.find_element(By.TAG_NAME,"a").get_attribute("href")).group(1),
                                    'primary':False,'dept_hierarchy':dept_hierarchy, 'brand': brand, 'category':category})
                counter+=1
            except:
                pass
    # New Sellers
    if soup.find("span",{"data-action":"show-all-offers-display"}):
        new_seller_link = (soup.find("span",{"data-action":"show-all-offers-display"})).find('a')['href']
        seller_list.append({'prod_name':product_id,'new_seller_link':new_seller_link})
        counter+=1
    # Subscription Sellers
    # try to find links - use this 
    if soup.find_all("div",{"id":"shipFromSoldByAbbreviated_feature_div"}):
        for seller in soup.find_all("div",{"id":"shipFromSoldByAbbreviated_feature_div"}):                
            seller_list.append({'prod_name':product_id,'subscription_seller':re.search(r'Sold by:\s+(.+)', seller.text).group(1)})
            counter+=1
    print(product_id, " Went in loops: ", counter)        
seller_list_df =  pd.DataFrame(seller_list)
seller_list_df

pd.DataFrame(department_list).to_csv('department_list.csv', index=False)
pd.DataFrame(product_list).to_csv('product_list.csv', index=False)
pd.DataFrame(seller_list).to_csv('seller_list.csv', index=False)
pd.DataFrame(seller_detail_list_df).to_csv('seller_detail_list_df.csv', index=False)
