import base64
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import random
import requests
import streamlit as st
import string
import time
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from newspaper import Article
import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def get_urls_from_google(query, publisher, num_results, start_date=None, end_date=None):
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run the browser in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)
    
    # Navigate to Google
    driver.get("https://www.google.co.id")
    
    # Find the search input field and enter the query
    search_input = driver.find_element("name", "q")
    search_input.send_keys(f"{query} site:{publisher}")
    search_input.send_keys(Keys.RETURN)
    
    urls = []

    while len(urls) < num_results:
        # Wait for the page to load
        time.sleep(3)
        
        # Find all search results links
        result_links = driver.find_elements("class name", "tF2Cxc")
        
        # Extract URLs from the links
        for link in result_links:
            url = link.find_element("tag name", "a").get_attribute("href")
            urls.append(url)
        
        # Scroll down to load more results
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        
    # Close the WebDriver
    driver.quit()
    
    return urls


def filter_links(urls, publisher):
    filtered_links = []
    for url in urls:
        if f"{publisher}/tag/" not in url and f"{publisher}/topic/" not in url:
            filtered_links.append(url)
    return filtered_links

def scrape_articles(filtered_urls):
    rows = []
    for filtered_url in tqdm(filtered_urls):
        try:
            a = Article(filtered_url,language='id')
            a.download()
            a.parse()
            
            date = a.publish_date
            title = a.title
            text = a.text
            
            key = Fernet.generate_key()
            unique_identifier = base64.urlsafe_b64encode(key).rstrip(b'=').hex()[:16]
            
            row = {'Datetime':date,
                   'Title':title,
                   'Text':text,
                   'URL':filtered_url,
                   'TextID': unique_identifier,
                   'Publication': publisher}
    
            rows.append(row)
        except Exception as e:
            print(e)
            row = {'Datetime':'N/A',
                   'Title':'N/A',
                   'Text':'N/A',
                   'URL':filtered_url,
                   'TextID': 'N/A',
                   'Publication': publisher}               
            
            rows.append(row)      
    df = pd.DataFrame(rows)
    return df

def load_data(file):
    data = pd.read_csv(file, usecols=['Datetime', 'Title', 'Text', 'URL', 'TextID', "Publication"])
    return data