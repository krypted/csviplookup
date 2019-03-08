#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install lxml before running using `pip install lxml`

"""
# Import necessary modules
import requests
import io
import csv
import random
import time
from datetime import datetime
from lxml import html



# For collect and set proxies
proxies = requests.get('https://www.proxy-list.download/api/v1/get?type=http')

proxies = proxies.text.split('\r\n')



http_proxy = random.choice(proxies)
proxyDict = { 
              "http"  : 'http://' + http_proxy, 
              "https" : 'http://' + http_proxy, 

            }



# Import APP ID's
IMPORT_FILE_NAME = 'input.csv'
ips = []
with open(IMPORT_FILE_NAME, 'r') as csvFile:
    reader = csv.reader(csvFile)
    for row in reader:
        ips.append(row[0])
print('Total ip imported: ' + str(len(ips)))


# Custom Header
headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
           'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'X-Requested-With': 'XMLHttpRequest'}

# Base URL(For creating session and extracting cookie)
url = 'https://www.whatismyip.com/ip-address-lookup/?iref=navbar'

# Search or POST URL
search_url = 'https://www.whatismyip.com/custom/response.php'

# Creating Session
session = requests.Session()

# Doing BASE GET requests
r = session.get(url, headers=headers, proxies=proxyDict)




# Here data points will be store
ip_list = []
country_list = []
state_list = []
postal_list = []
isp_list = []

for i, ip_ in enumerate(ips):
    
    try:
        # Basic Clean up (Removing \n and space)
        ip_ = str(ip_).replace('\n','').replace(' ','')
        
        # Making paramas
        data = dict(ip=ip_, action='ip-lookup')
        
        # Extracting cookes
        __cfduid = r.cookies.get_dict()['__cfduid']
        __cfduid = '__cfduid=' + __cfduid
        
        dwqa_anonymous = r.cookies.get_dict()['dwqa_anonymous']
        dwqa_anonymous = 'dwqa_anonymous=' + dwqa_anonymous
        cookie_data = __cfduid + '; ' + dwqa_anonymous
        
        cookie_data = dict(Cookie=cookie_data)
        
        # Finalize header(merge)
        headers = {**headers, **cookie_data}
    
        # POST requests data
        r2 = session.post(search_url, data=data, headers=headers, proxies=proxyDict)
        
        # Making LXML object
        root = html.fromstring(r2.content)
        
        
        # Country Code
        country_list.append(root.xpath('div[1]/div[2]/table/tbody/tr[6]/td[2]')[0].text)
        
        # State
        if root.xpath('div[1]/div[2]/table/tbody/tr[4]/td[2]')[0].text == '-':
            state_list.append(root.xpath('div[1]/div[1]/table/tbody/tr[4]/td[2]')[0].text)
        else:
            state_list.append(root.xpath('div[1]/div[2]/table/tbody/tr[4]/td[2]')[0].text)
            
            
        # ISP provider
        if root.xpath('div[1]/div[2]/table/tbody/tr[10]/td[2]')[0].text == '-':
            isp_list.append(root.xpath('div[1]/div[1]/table/tbody/tr[10]/td[2]')[0].text)
        else:
            isp_list.append(root.xpath('div[1]/div[2]/table/tbody/tr[10]/td[2]')[0].text)
            
        
        # Postal
        if root.xpath('div[1]/div[2]/table/tbody/tr[8]/td[2]')[0].text == '-':
            postal_list.append(root.xpath('div[1]/div[1]/table/tbody/tr[8]/td[2]')[0].text)
        else:
            postal_list.append(root.xpath('div[1]/div[2]/table/tbody/tr[8]/td[2]')[0].text)
        
        ip_list.append(ip_)
        
        
        print('Left: ' + str(len(ips)-i))
        # Random sleep for not putting pressure on server
        time.sleep(random.random())
        
    except Exception as e: 
        print('Error: ' + str(e))
        print('id :' + str(ip_))
        pass
    

# Zip data  
data = [[a,b,c,d] for a,b,c,d in zip(ip_list, country_list, state_list, isp_list)]
 
# Export to CSV     
EXPORT_FILE_NAME = 'output-' + "{:%Y_%m_%d_%M_%S}".format(datetime.now())  + '.csv'   
with open(EXPORT_FILE_NAME, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(data)

print(EXPORT_FILE_NAME + ' saved successfully.')

    
    
    
    
    
