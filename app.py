import streamlit as st
import requests
import time
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
from cryptography.fernet import Fernet
from tqdm import tqdm
import base64
import streamlit as st
import pandas as pd
import string
from text_analysis import plot_n_most_frequent_words
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from text_analysis import stopwords_removal
from text_analysis import extract_collocations
from text_analysis import display_concordance
import random
import time


"""
def get_urls_from_google(query, publisher=None, num_pages=1):
    urls = []
    query_string = f"{query}"
    if publisher:
        query_string += f" site:{publisher}"
    url = f"https://www.google.com/search?q={query_string}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    for page in range(num_pages):
        page_url = url + f"&start={page * 10}"
        page = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all("div", class_="MjjYud")
        for result in results:
            link = result.find("a")["href"]
            urls.append(link)

    return urls

def filter_links(urls, publisher):
    filtered_links = []
    for url in urls:
        if f"{publisher}/tag/" not in url and f"{publisher}/topic/" not in url:
            filtered_links.append(url)
    return filtered_links

https://www.google.com/search?q={query_string}
"""
import requests
from bs4 import BeautifulSoup

def get_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = [url.strip() for url in file.read().split(',')]

    return urls

def filter_links(urls, publisher):
    filtered_links = []
    for url in urls:
        if f"{publisher}/tag/" not in url and f"{publisher}/topic/" not in url:
            filtered_links.append(url)
    return filtered_links

def main():
    file_path = input("Enter the path to the text file containing URLs: ")
    publisher = input("Enter the publisher: ")
    urls = get_urls_from_file(file_path)
    filtered_urls = filter_links(urls, publisher)
    
    for idx, url in enumerate(filtered_urls, start=1):
        print(f"{idx}. {url}")

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

def app():
    st.title("SemanText")

    # Features
    option = st.sidebar.selectbox("Select a feature", ["Scraper", "Wordlist and Wordcloud", "Collocation", "Key Words in Context"])
    if option == "Scraper":
        st.markdown("---") 
        st.subheader("Scraper")       
        query = st.text_input("Enter your search query:")
        if not query:
            st.stop()
            
        publisher_options = ['bisnis.com', 'cnbcindonesia.com', 'cnnindonesia.com', 'detik.com', 'kompas.com', 'liputan6.com',  'merdeka.com', 'okezone.com', 'suara.com', 'tribunnews.com']
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
        start_time = time.time()
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
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        print(f"Scraping {len(rows)} articles took {duration} seconds.")
        
        df = pd.DataFrame(rows)
        
        # drop the rows with N/A, NaN, null or None
        df = df[~df.isin(['N/A']).any(axis=1)]
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

        # Show scraping duration
        st.success(f"Scraping {len(rows)} articles took {duration} seconds.")

        # Download the scraped articles
        def download_csv(df):
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="corpus_{query}_{publisher}.csv">Export to CSV</a>'
            return href
        st.markdown(download_csv(df), unsafe_allow_html=True)

    elif option == "Wordlist and Wordcloud":
        st.markdown("---")
        st.subheader("Wordlist and Wordcloud")
        # Add a file uploader for the CSV files
        uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])

        # Merge the uploaded CSV files into a single DataFrame
        if uploaded_files:
            corpus = pd.DataFrame() # Initialize an empty DataFrame to hold the merged corpus
            total_words = 0 # Initialize a variable to hold the total number of words
            for file in uploaded_files:
                file.seek(0) # Reset the file pointer to the beginning of the file
                data = pd.read_csv(file)
                corpus = pd.concat([corpus, data], ignore_index=True)
                total_words += data["Text"].str.split().str.len().sum() # Compute the number of words for the current file
            
           
            # Display the total number of rows and words
            st.write(f"Total articles: {len(corpus)}")
            st.write(f"Total words: {total_words}")
            
            # Display an overview of the number of rows per value of the Publication column
            publication_counts = corpus["Publication"].value_counts().to_frame().reset_index()
            publication_counts.columns = ["Publication", "Count"] # Rename the columnsz
            st.write("Articles by Publication:")
            st.table(publication_counts)
            st.markdown("---")
            st.markdown("Merged dataframe")
            st.write(corpus)

        # Create a table for the most frequent words
        if 'corpus' in locals() and st.button("Show most frequent words"):
            n_words = st.text_input("Maximum words", "20")
            try:
                n_most_common = int(n_words)
            except ValueError:
                st.write("Please enter a valid integer for the number of words.")
            
            # Remove stop words and punctuation from the corpus
            corpus['Text'] = corpus['Text'].apply(lambda x: stopwords_removal(x.lower().split()))

            top_n_words = plot_n_most_frequent_words(corpus, "Text", n=n_most_common)

            # Create a table for the most frequent words
            words_freq = pd.DataFrame(top_n_words, columns=["Word", "Frequency"])
            # Remove apostrophes and commas from the words in the table
            words_freq["Word"] = words_freq["Word"].str.replace("'", "").str.replace(",", "")
            # Remove the row that contains an empty string in the Word column
            words_freq = words_freq[words_freq["Word"] != ""]
            st.table(words_freq)
            st.set_option('deprecation.showPyplotGlobalUse', False)

            # Create a horizontal bar chart using Plotly
            fig = px.bar(
                words_freq,
                x='Frequency',
                y='Word',
                orientation='h',
                labels={'y': 'Word', 'x': 'Frequency'}
            )
            fig.update_layout(
                title=f"Most frequent words",
                xaxis_title="Frequency",
                yaxis_title="Word",
                autosize=False,
                width=800,
                height=500
            )
            st.plotly_chart(fig)
            st.set_option('deprecation.showPyplotGlobalUse', False)

        # Generate the word cloud
        if 'corpus' in locals() and st.button("Generate word cloud"):
            # Filter out any empty or NaN values from the corpus
            corpus = corpus.dropna(subset=['Text'])
            corpus = corpus[corpus['Text'] != '']

            # Remove stop words and punctuation from the corpus
            corpus['Text'] = corpus['Text'].apply(lambda x: stopwords_removal([word.translate(str.maketrans('', '', string.punctuation)).replace("'", "") for word in x.lower().split()]))
            text = " ".join(corpus["Text"].astype(str).tolist()).lower()

            # Generate the word cloud
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text.replace("'", ""))

            # Display the word cloud
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            st.pyplot()
            st.set_option('deprecation.showPyplotGlobalUse', False)

    elif option == "Collocation":
        st.markdown("---")
        st.subheader("Collocation")
        # Add a file uploader for the CSV files
        uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])

        # Merge the uploaded CSV files into a single DataFrame
        if uploaded_files:
            corpus = pd.DataFrame() # Initialize an empty DataFrame to hold the merged corpus
            total_words = 0 # Initialize a variable to hold the total number of words
            for file in uploaded_files:
                file.seek(0) # Reset the file pointer to the beginning of the file
                data = pd.read_csv(file)
                corpus = pd.concat([corpus, data], ignore_index=True)
                total_words += data["Text"].str.split().str.len().sum() # Compute the number of words for the current file
            
           
            # Display the total number of rows and words
            st.write(f"Total articles: {len(corpus)}")
            st.write(f"Total words: {total_words}")
            
            # Display an overview of the number of rows per value of the Publication column
            publication_counts = corpus["Publication"].value_counts().to_frame().reset_index()
            publication_counts.columns = ["Publication", "Count"] # Rename the columns
            st.write("Articles by Publication:")
            st.table(publication_counts)
            st.markdown("---")
            st.markdown("Merged dataframe")
            st.write(corpus)

        # Save collocations as CSV
        def download_csv(collocations_df):
            csv = collocations_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="collocations.csv">Export to CSV</a>'
            return href


        # Extract the possible collocations
        if 'corpus' in locals() and st.button("Extract collocations"):
                # Show a spinner while the collocations are being extracted
                with st.spinner("Extracting collocations..."):
                    collocations_df = extract_collocations(corpus, st)

                # Hide the spinner and display the top collocations and their frequencies in a table
                st.success("Collocations extracted!")
                st.write("Top collocations:")
                st.dataframe(collocations_df.head(50))
                st.markdown(download_csv(collocations_df), unsafe_allow_html=True)

                st.markdown("---")

                st.write("Collocations with POS pattern 'NOUN + ADJ':")
                noun_adj_df = collocations_df[collocations_df['pos_pattern'] == 'NOUN + ADJ']
                st.dataframe(noun_adj_df)
                st.write("Collocations with POS pattern 'NOUN + NOUN':")
                noun_noun_df = collocations_df[collocations_df['pos_pattern'] == 'NOUN + NOUN']
                st.dataframe(noun_noun_df)
                st.write("Collocations with POS pattern 'VERB + NOUN':")
                verb_noun_df = collocations_df[collocations_df['pos_pattern'] == 'VERB + NOUN']
                st.dataframe(verb_noun_df)


    elif option == "Key Words in Context":
        st.markdown("---")
        st.subheader("Key Words in Context")
        # Add a file uploader for the CSV files
        uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])

        # Merge the uploaded CSV files into a single DataFrame
        if uploaded_files:
            corpus = pd.DataFrame() # Initialize an empty DataFrame to hold the merged corpus
            total_words = 0 # Initialize a variable to hold the total number of words
            for file in uploaded_files:
                file.seek(0) # Reset the file pointer to the beginning of the file
                data = pd.read_csv(file)
                corpus = pd.concat([corpus, data], ignore_index=True)
                total_words += data["Text"].str.split().str.len().sum() # Compute the number of words for the current file
            
           
            # Display the total number of rows and words
            st.write(f"Total articles: {len(corpus)}")
            st.write(f"Total words: {total_words}")
            
            # Display an overview of the number of rows per value of the Publication column
            publication_counts = corpus["Publication"].value_counts().to_frame().reset_index()
            publication_counts.columns = ["Publication", "Count"] # Rename the columns
            st.write("Articles by Publication:")
            st.table(publication_counts)
            st.markdown("---")
            st.markdown("Merged dataframe")
            st.write(corpus)
            st.markdown("---")
            col = st.selectbox("Select a column to search:", options=data.columns)

        # Let the user choose the column to search and the keyword to search for
        keyword = st.text_input("Enter a keyword to search for:")
        
        # Generate and display the concordance
        if st.button("Generate Concordance"):
            concordance_df = display_concordance(data, col, keyword)
            for index, row in concordance_df.iterrows():
                kwic = row['KWIC'].replace(keyword, keyword)
                concordance_df.at[index, 'KWIC'] = kwic
            st.write(concordance_df)


    # Add a footer with your name
    with st.container():
        st.markdown("---")
        st.markdown("Developed by MW Hidayat. Find me on [Twitter](https://twitter.com/casecrit)")

# Run the Streamlit app
if __name__ == '__main__':
    st.set_page_config(page_title='SemanText', page_icon=':newspaper:')
    app()
