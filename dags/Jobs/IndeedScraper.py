from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import time
from DrissionPage import ChromiumPage, ChromiumOptions

def connect(sleep_time=15,url='https://fr.indeed.com'):
    options = ChromiumOptions()
    driver = ChromiumPage(options)
    driver.get(url)
    time.sleep(sleep_time)
    return driver


def get_links(keyword = "hadoop"):

    Links = []
    Posted = []

    driver= connect()
    url = f'https://fr.indeed.com/jobs?q={keyword}&l=France&fromage=1'
    while True:
        try:
            
            driver = connect(2,url)
            html = driver.html
            soup = BeautifulSoup(html, 'html.parser')

            td = soup.find_all('td',{'class':'resultContent'})
            link = []
            posted = []
            for i in td:
                link.append("https://fr.indeed.com/"+i.find('a',{'class':'jcs-JobTitle css-jspxzf eu4oa1w0'}).get('href'))
                posted.append(i.find('span',{'data-testid':'myJobsStateDate'}).text)

                if len(link) >= 20:
                    break
                
            Links.extend(link)
            Posted.extend(posted)
            try:
                url = 'https://fr.indeed.com' + soup.find('a', {'aria-label':'Next Page'}).get('href')
            except:
                break

            if len(Links) >= 20:
                break

        except:
            print("Error URL")
            break
    
    print(len(Links),"Jobs found for",keyword)
            
    driver.quit()
    return Links,Posted


def get_all_links(Keywords):
    Links = []
    Posted = []
    for key in Keywords:
        links, posted = get_links(key)
        Links.extend(links)
        Posted.extend(posted)
    return Links, Posted


def get_datas(Keywords):
    List_job = []
    Links, Posted = get_all_links(Keywords)
    for i in range(len(Links)):
        try:
            job = {}
            driver = connect()
            driver.get(Links[i])
            time.sleep(2)
            soup = BeautifulSoup(driver.html,'html.parser')
            try:
                job['job_link'] = Links[i]
            except:
                job['job_link'] = None

            try:
                job['job_name'] = soup.find('h1',{'class':'jobsearch-JobInfoHeader-title'}).text.strip()
            except:
                job['job_name'] = None
                
            try:
                job['job_text'] = soup.find('div',{'id':'jobDescriptionText'}).text.strip()
            except:
                job['job_text'] = None
                
            try:
                job['job_company'] = soup.find('div',{'data-testid' : 'inlineHeader-companyName'}).find('span').text.strip()
            except:
                job['job_company'] = "Not found"
                
            try:
                job['job_location'] = soup.find('div',{'id':'jobLocationText'}).text.strip()
            except:
                job['job_location'] = None
            try:
                job['job_type'] =  soup.find('div',{'id':"salaryInfoAndJobType"}).find('span',{'class':'css-k5flys eu4oa1w0'}).text.replace('-','').strip()
            except:
                job['job_type'] = None
                
            try:
                date = Posted[i]
                now = datetime.now()
                if 'instant' in date:
                    formatted_date = now.strftime("%Y-%m-%d")
                    job['job_date'] = formatted_date
                elif '1jour' in date.replace('\xa0', ''):
                    date = now - timedelta(days=1)
                    formatted_date = date.strftime("%Y-%m-%d")
                    job['job_date'] = formatted_date
            except:
                job['job_date'] = now.strftime("%Y-%m-%d")
                
        except:
            print("Error link")
            pass
        
        List_job.append(job)
        driver.quit()
        
        print(i+1,"jobs extracted!",end='\r')
    return pd.DataFrame(List_job)