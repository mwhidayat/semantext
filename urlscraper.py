import base64
import pandas as pd
from newspaper import Article
from cryptography.fernet import Fernet

def scrape_articles_from_urls(url_file):
    rows = []

    with open(url_file, 'r') as file:
        url_list = [line.strip() for line in file]

    for url in url_list:
        try:
            a = Article(url, language='id')
            a.download()
            a.parse()

            date = a.publish_date
            title = a.title
            text = a.text

            # Remove line breaks from the 'Text' column
            text = text.replace('\n', ' ')

            key = Fernet.generate_key()
            unique_identifier = base64.urlsafe_b64encode(key).rstrip(b'=').hex()[:16]

            row = {
                'Datetime': date,
                'Title': title,
                'Text': text,
                'URL': url,
                'TextID': unique_identifier,
                'Publication': 'Online' 
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
                'Publication': 'Online' 
            }

            rows.append(row)

    df = pd.DataFrame(rows)
    return df
