from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from DrissionPage import ChromiumPage, ChromiumOptions
import pandas as pd
import requests
import time

def connect(keyword):
    options = ChromiumOptions()
    driver = ChromiumPage(options)
    time.sleep(5)
    driver.get(f'https://www.welcometothejungle.com/fr/jobs?&query={keyword}&sortBy=mostRecent')
    return driver

def get_links(keyword="data engineer"):
    links=[]
    driver = connect(keyword)
    try:
        time.sleep(10)
        html = driver.html
        soup = BeautifulSoup(html, 'html.parser')
                
        for page in range(1,2):
            items = soup.find('ul', 'sc-104bokb-0 ewzTDK ais-Hits-list')
            for item in items:
                try:
                    date = item.find('time').get("datetime")
                    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                    current_date = datetime.utcnow()
                    date_difference = current_date - date_obj
                    if date_difference <= timedelta(days=1):
                        links.append("https://www.welcometothejungle.com"+item.find("a",{"class": 'sc-1gjh7r6-0 iPeVkS'}).get("href"))
                except:
                    pass
                
            if(date_difference > timedelta(days=1)):
                break
            
            if(len(links) > 50):
                break
            else:
                driver.eles("@class: jCRLMV")[-1].click()
                time.sleep(5)

    except:
        print("Error Keyword ..")
    print(len(links),"Jobs for",keyword)
    
    return links,driver

def get_data(keyword="data engineer"):
    List_job = []
    links,driver = get_links(keyword)

    print(keyword, 'Job extraction ...')
    
    for i in range(len(links)):
        try:
            job = {}
            driver.get(links[i])
            time.sleep(10)
            soup = BeautifulSoup(driver.html,'html.parser')

            try:
                job['job_link'] = links[i]
            except:
                job['job_link'] = None
                
            try:
                job["job_name"] = soup.find('h2', {'class':"sc-gvZAcH lodDwl wui-text"}).text.strip()
            except:
                job["job_name"] = keyword

            try: 
                ul = soup.find('div',{'class':'fhzEMX'}).find_all('ul')
                job_text = ''
                for li in ul:
                    job_text += ' '+li.text
                if job_text=='':
                    job_text = soup.find('div',{'class':'kqgROr'}).text
                job["job_text"] = job_text
            except:
                job["job_text"] = None

            try:
                job["job_company"] = soup.find('span',{'class':'sc-gvZAcH lpuzVS wui-text'}).text.strip()
            except:
                job["job_company"] = "Not found"

            
            try:
                job_villes = soup.find_all('div',{'class':'sc-bOhtcR eDrxLt'})[1].find_all('span',{'class':'dhOyPm'})
                job_ville=''
                for ville in job_villes:
                    job_ville += ville.text.strip()
                
                job["job_location"] = job_ville
            except:
                job["job_location"] = None

            try:
                job["job_type"] = soup.find_all('div',{'class':'sc-bOhtcR eDrxLt'})[0].text
            except:
                job["job_type"] = None

            try:
                date = soup.find('time').get('datetime')
                dt_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

                date = dt_obj.date().isoformat()
                job["job_date"] = date
            except:
                now = datetime.now()
                job["job_date"] = now.strftime("%Y-%m-%d")
            
            
            List_job.append(job)
            
            print(i,'Jobs read',end="\r")
        except:
            pass
    return pd.DataFrame(List_job)


def get_datas(Keywords):
    data = pd.DataFrame()
    for key in Keywords:
        df = get_data(key)
        data = pd.concat([data,df], axis=0)
    print('Done')
    return data