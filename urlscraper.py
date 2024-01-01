import base64
import pandas as pd
import streamlit as st
from newspaper import Article
import uuid
from tqdm import tqdm
from urllib.parse import urlparse

# Function to scrape articles from URLs with a progress bar
def scrape_articles_from_urls_with_progress(url_file):
    rows = []

    with open(url_file, 'r') as file:
        url_list = [line.strip() for line in file]

    # Create a placeholder for the progress bar
    progress_bar = st.progress(0)

    # Use st.empty() to create a container for updates
    progress_text = st.empty()

    # Loop through URLs
    for i, url in enumerate(url_list):
        try:
            a = Article(url, language='id')
            a.download()
            a.parse()

            date = a.publish_date
            title = a.title
            text = a.text

            # Remove line breaks from the 'Text' column
            text = text.replace('\n', ' ')

            unique_identifier = str(uuid.uuid4())[:16]

            # Extract only the root domain name from the URL
            domain = urlparse(url).netloc.split('.')[-2] + '.' + urlparse(url).netloc.split('.')[-1]

            row = {
                'Datetime': date,
                'Title': title,
                'Text': text,
                'URL': url,
                'TextID': unique_identifier,
                'Publication': domain
            }

            rows.append(row)

        except Exception as e:
            print(e)
            row = {
                'Datetime': 'N/A',
                'Title': 'N/A',
                'Text': 'N/A',
                'URL': url,
                'TextID': 'N/A',
                'Publication': 'N/A'
            }

            rows.append(row)

        # Update progress bar and text
        progress_percentage = (i + 1) / len(url_list)
        progress_bar.progress(progress_percentage)
        progress_text.text(f"Scraping progress: {int(progress_percentage * 100)}%")

    # Close the progress bar
    progress_bar.empty()

    df = pd.DataFrame(rows)
    return df