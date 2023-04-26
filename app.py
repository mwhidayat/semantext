import streamlit as st
import requests
import time
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
from cryptography.fernet import Fernet
from tqdm import tqdm
import base64


def get_urls_from_google(query, publisher, num_scrolls, start_date=None, end_date=None):
    urls = []
    query_string = f"{query} site:{publisher}"
    if start_date:
        query_string += f" after:{start_date}"
    if end_date:
        query_string += f" before:{end_date}"
    url = f"https://www.google.co.id/search?q={query_string}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    while num_scrolls:
        results = soup.find_all("div", class_="g")
        for result in results:
            link = result.find("a")["href"]
            urls.append(link)
        try:
            next_button = soup.find("a", {"id": "pnnext"})["href"]
            url = f"https://www.google.co.id{next_button}"
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            time.sleep(2)  # Wait for new results to load
        except:
            break
        num_scrolls -= 1
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

def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="articles.csv">Export to CSV</a>'
    return href

def app():
    st.title("Indonesian news articles scraper")
    
    # Sidebar
    query = st.text_input("Enter your search query:")
    if not query:
        st.stop()
        
    publisher_options = ['bisnis.com', 'cnbcindonesia.com', 'detik.com', 'kompas.com', 'liputan6.com', 'merdeka.com', 'okezone.com', 'suara.com', 'tribunnews.com']
    publisher = st.radio("Select a publisher's domain:", publisher_options)
    if not publisher:
        st.stop()
    
    start_date = st.text_input("Enter the start date (yyyy-mm-dd) (optional):")
    end_date = st.text_input("Enter the end date (yyyy-mm-dd) (optional):")
    
    num_scrolls = st.text_input("Enter the number of pages to scrape (each page usually contains 10 articles):")
    if not num_scrolls:
        st.stop()
    num_scrolls = int(num_scrolls)
    
    # Get the URLs from Google search
    with st.spinner("Getting search results..."):
        urls = get_urls_from_google(query, publisher, num_scrolls, start_date, end_date)
    st.success(f"{len(urls)} URLs for '{query}' from '{publisher}' are found.")
    
    # Filter URLs
    with st.spinner("Filtering URLs..."):
        filtered_urls = filter_links(urls, publisher)
    st.success(f"If any tagging URLs and rows with null values are found, they will be removed.")
    
    # Scrape articles
    rows = []
    with st.spinner("Scraping articles..."):
        for filtered_url in tqdm(filtered_urls):
            try:
                a = Article(filtered_url, language='id')
                a.download()
                a.parse()

                date = a.publish_date
                title = a.title
                text = a.text

                key = Fernet.generate_key()
                unique_identifier = base64.urlsafe_b64encode(key).rstrip(b'=').hex()[:16]

                row = {'Datetime': date,
                       'Title': title,
                       'Text': text,
                       'URL': filtered_url,
                       'TextID': unique_identifier,
                       'Publication': publisher}

                rows.append(row)
            except Exception as e:
                print(e)
                row = {'Datetime': 'N/A',
                       'Title': 'N/A',
                       'Text': 'N/A',
                       'URL': filtered_url,
                       'TextID': 'N/A',
                       'Publication': publisher}

                rows.append(row)
    df = pd.DataFrame(rows)
    
    # drop the rows with NaN, null or None
    df.dropna(inplace=True)
    
    # Add progress bar
    with st.spinner("Processing data..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i+1)

    # Replace line breaks with spaces
    if 'Text' in df.columns:
        df['Text'] = df['Text'].str.replace('\n', '  ')

    # Show dataframe
    st.write(df)
    st.markdown(download_csv(df), unsafe_allow_html=True)

    # Add a footer with your name
    with st.container():
        st.markdown("---")
        st.markdown("Developed by [MW Hidayat](https://twitter.com/casecrit)")

# Run the Streamlit app
if __name__ == '__main__':
    st.set_page_config(page_title='Article Scraper', page_icon=':newspaper:')
    app()
