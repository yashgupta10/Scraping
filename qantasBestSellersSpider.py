import scrapy
import pandas as pd
import time
import re
import os
import json
import csv
import winsound
from bs4 import BeautifulSoup
from scrapy_splash import SplashRequest
import requests
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
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains
#pip install -U google-api-python-client
from googleapiclient import discovery

#pip install -U oauth2client
from oauth2client.client import GoogleCredentials
from google.oauth2 import service_account

#pip install pandas-gbq -U
from google.cloud import bigquery
from google.cloud import secretmanager
from google.cloud import resourcemanager_v3

#os.environ['http_proxy'] = 'http://3.24.58.156:3128'
#os.environ['https_proxy'] = 'https://3.24.58.156:3128'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + "\\application_default_credentials.json"
credentials = GoogleCredentials.get_application_default()
sm_client = secretmanager.SecretManagerServiceClient()
sa_key = json.loads(sm_client.access_secret_version(request={"name":'projects/123/secrets/abc/versions/1'}).payload.data.decode("UTF-8"))
credentials = service_account.Credentials.from_service_account_info(sa_key)
#Setup Application Default Credentials -- https://cloud.google.com/docs/authentication/client-libraries#python


ua = UserAgent()
username = os.getenv("USERNAME")
binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
fp = (r'C:\Users\Yash Gupta\AppData\Roaming\Mozilla\Firefox\Profiles\ibhfvizo.default-release')
opts = Options()
opts.profile = fp
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities["pageLoadStrategy"] = "normal"
opts.add_argument(f'user-agent=ua.chrome')
opts.headless = True




class qantasBestSellersSpider(scrapy.Spider):
    name = "qantas_bestsellers"
    custom_settings = {
        'CONCURRENT_REQUESTS': 20,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 20,
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'LOG_LEVEL': 'ERROR',
    }
    
    headers = {
        "User-Agent": ua.random,
    }
    start_urls = [
        "https://www.ebay.com.au/n/all-stores",
    ]
    df_product_links = []
    df_product_detail_done = []
    df_product_detail = []
    product_detail = []
    
    def closed(self, reason):
        pd.DataFrame(self.product_detail).to_csv('qantas_product_detail3.csv', index=False)
        print('closed')

        
    def start_requests(self):
        print('***********Start**********')
        self.df_product_links = pd.read_csv('qantas_product_links.csv')
        self.df_product_detail_done = pd.read_csv('qantas_product_detail_final.csv')
        for link in self.df_product_links['product_link']:
            if link not in self.df_product_detail_done['product_link'].tolist():
                yield  scrapy.Request(url=link, callback=self.parse_product_detail, headers=self.headers, meta={'dont_merge_cookies': True})
    
          
    def parse_product_detail(self, response):
        print('******** In parse_product_detail')
        driver = webdriver.Firefox(capabilities=firefox_capabilities,firefox_binary=binary, options = opts)
        driver.get(response.request.url)
        driver.maximize_window()
        time.sleep(1)
        hierarchy = ''
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[1]')))
            hierarchy_element = driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[1]/div[1]')
            for e in hierarchy_element.find_elements(By.TAG_NAME, 'a'):
                hierarchy = hierarchy+ '/' + e.get_attribute("innerHTML") 
            hierarchy1 = hierarchy.rsplit('/', 1)[1]
            hierarchy2 = hierarchy.rsplit('/', 1)[0]
        except:
            print("Hierarchy Not Found:", response.request.url)
            hierarchy1 = 'N/A'
            hierarchy2 = 'N/A'
        body1 = []
        body_list = []
        try:  
            body1_element =  driver.find_element(By.XPATH,'/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div[1]')
            #print(body1_element.get_attribute("innerHTML"))
            i=0
            for e in body1_element.find_elements(By.TAG_NAME, 'div'):
                if((i>=1) and (i<=4)):
                    if ('Review' in e.text):
                        i = i-1
                        continue
                    body1.append(e.text)
                i=i+1

            body_list.append(body1[0])
            body_list.append(re.search(r"SKU:\s*(\w+)", body1[1]).group(1) if re.search(r"SKU:\s*(\w+)", body1[1]) else None)
            body_list.append(body1[2].replace('Sold and delivered by ', ''))
            # body_list.append(re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', body1[3])[0])
            # body_list.append(re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', body1[3])[1])
            body_list.append(body1[3].replace('\n', ' '))
        except:
            print("Body 1 not found", response.request.url)
            body_list.append('N/A')
            body_list.append('N/A')
            body_list.append('N/A')
            body_list.append('N/A')
        try:
            body2_elements = driver.find_elements(By.XPATH,'/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div[*]/div[2]')
            for e in body2_elements:
                if ('Dispatch' in e.text):
                    body2_element = e.text
                    break
            body_list.append(body2_element.split('\n')[0])
            body3_elements = driver.find_elements(By.XPATH,'/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div[*]/div[1]')
            for e in body3_elements:
                if (' delivery' in e.text):
                    body3_element = e.text
                    break
            body_list.append(body3_element.split('\n')[0])
            body_list.append(body3_element.split('\n')[1])
        except:
            print('Delivery not found: ',response.request.url)
            body_list.append('N/A')
            body_list.append('N/A')
            body_list.append('N/A')
        try:
            self.product_detail.append( {'brand': body_list[0],
                                'product_name': hierarchy1,
                                'sku':body_list[1],
                                'sold_delivered_by':body_list[2],
                                'price':body_list[3],
                                'dispatch':body_list[4],
                                'delivery_type':body_list[5],
                                'delivery_cost':body_list[6],
                                'hierarchy': hierarchy2,
                                'product_link':response.request.url
                               })
            print({'brand': body_list[0],
                                'product_name': hierarchy1,
                                'sku':body_list[1],
                                'sold_delivered_by':body_list[2],
                                'price':body_list[3],
                                'dispatch':body_list[4],
                                'delivery_type':body_list[5],
                                'delivery_cost':body_list[6],
                                'hierarchy': hierarchy2,
                                'product_link':response.request.url
                               })
            with open('product_detail_live.csv', "a") as csvfile:
                headers = ['brand', 'product_name','sku','sold_delivered_by','price','dispatch','delivery_type','delivery_cost','hierarchy','product_link']
                writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)
                if os.stat('product_detail_live.csv').st_size == 0:
                        writer.writeheader()  # file doesn't exist yet, write a header
                writer.writerow({'brand': body_list[0],
                                'product_name': hierarchy1,
                                'sku':body_list[1],
                                'sold_delivered_by':body_list[2],
                                'price':body_list[3],
                                'dispatch':body_list[4],
                                'delivery_type':body_list[5],
                                'delivery_cost':body_list[6],
                                'hierarchy': hierarchy2,
                                'product_link':response.request.url
                               })
        except:
            print('Cound not append data:', response.request.url)
        driver.close()
