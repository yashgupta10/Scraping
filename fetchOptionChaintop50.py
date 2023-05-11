import requests
from bs4 import BeautifulSoup
import pandas as pd
import calendar
import datetime
import os
import urllib.parse

def get_processed_options(symbol,date,workDir):   
    baseUrl = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + symbol + "&date="+date
    #print(baseUrl)
    headers = {
         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }

    html_content = requests.get(baseUrl,headers=headers).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    #print(soup.prettify()) # print the parsed data of html
    #print(soup.prettify())
    #Get Underlying Price
    underlying_price=[]
    underlying_price_html = soup.find("div", attrs={"class": "content_big"})
    underlying_price_html = underlying_price_html.find_all('td')
    for row_number,td in enumerate(underlying_price_html):
        if row_number == 1:
            underlying_price = (td.text.strip().replace(u'\xa0', u'').split('\n'))
        elif row_number > 1:
            break
    underlying_price = ((underlying_price[0].split(' ')))
    underlying_price= float(underlying_price[3].replace(',', ''))
    underlying_price_left = underlying_price - (underlying_price/10)
    underlying_price_right = underlying_price + (underlying_price/10)
    #get options table
    optTable = soup.find("table", attrs={"id": "octable"})
    optTableData = optTable.find_all('tr')
    # Get all the headings of Lists
    headings = []
    dfDatalist = []
    i=0
    for row_number, tr_nos in enumerate(optTableData):
        if row_number <=1:
            th_columns = tr_nos.find_all('th')
            temp_list = []
            for th in th_columns:
                temp_list.append(th.text.replace('\n', ' ').strip())
            headings.append(temp_list)
            continue
        if row_number != len(optTableData) - 1  :
            td_columns = tr_nos.find_all('td')
            temp_list = []
            for td in td_columns:
                temp_list.append(td.text.replace('\n', ' ').strip())
            dfDatalist.append(temp_list)


    dfOptTable = pd.DataFrame(dfDatalist, columns = headings[1]) 
    dfOptTable= dfOptTable.apply(lambda x: x.str.replace(',', ''), axis=1)
    dfOptTable = dfOptTable.apply(pd.to_numeric, errors='coerce')
    
    dfOptTable = dfOptTable.drop(columns='Chart')
    dfOptTable.columns = (dfOptTable.columns[:10]+'_calls').append( dfOptTable.columns[10:]  + '_puts')
    dfOptTable['Symbol'] = symbol
    dfOptTable['Date']=date
    dfOptTable['UnderlyingPrice']=underlying_price
    dfOptTable.to_csv(workDir+'\\'+symbol+'_'+date+'_option.csv', index = False)
    return (''+symbol+'_'+date+'_option.csv saved')
    
#####################################################################################
#Start here     
#####################################################################################
#top50stock list
sym_list = ['ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'INFRATEL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY', 'EICHERMOT', 'GAIL', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'HDFC', 'ICICIBANK', 'ITC', 'IOC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'UPL', 'ULTRACEMCO', 'VEDL', 'WIPRO', 'YESBANK', 'ZEEL']
cal = calendar.Calendar(0)
workDir=os.getcwd()+'\optionChains'
try:
    os.mkdir(workDir)
except:
    pass
month = cal.monthdatescalendar(datetime.datetime.now().year, datetime.datetime.now().month)
if (max(month[-1]).month == datetime.datetime.now().month):
    lastweek = month[-1]
else:
    lastweek = month[-2]
lastThursday = lastweek[3]
lastThursday = lastThursday.strftime('%d%b%Y').upper()
result=pd.DataFrame(columns = None)

for sym in sym_list:
    print(get_processed_options(urllib.parse.quote(sym),lastThursday,workDir))
