import base64
import pandas as pd
import plotly.express as px
import random
import requests
import streamlit as st
import string
import time
from collections import Counter
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from scraping import scrape_articles, get_urls_from_google, filter_links
from text_analysis import plot_n_most_frequent_words, stopwords_removal, extract_ngrams, extract_collocations, display_concordance
from urlscraper import scrape_articles_from_urls_with_progress
import os

def app():
    st.title("SemanText")

    # Features
    option = st.sidebar.selectbox("Select a feature", ["URL Scraper", "Most common words", "N-gram", 
                                                       "Rule-Based Collocation", "Key Words in Context"])

    # Article scraping from URLs
    if option == "URL Scraper": 
        st.markdown("---")
        st.subheader("URL Scraper")
        uploaded_urls = st.file_uploader("Upload a text file with one URL per line", type=["txt"])

        if st.button("Scrape the URLs"):
            if uploaded_urls is not None:
                with st.spinner("Scraping in progress..."):
                    with open("temp_url_file.txt", "wb") as temp_file:
                        temp_file.write(uploaded_urls.read())

                    # Scrape articles from the URLs with progress
                    scraped_df = scrape_articles_from_urls_with_progress("temp_url_file.txt")

                    st.success("Scraping complete!")

                    # Display the scraped data
                    st.write(scraped_df)

                    # Remove the temporary URL file
                    os.remove("temp_url_file.txt")

                    # Download the scraped articles
                    def download_corpus(scraped_df):
                        csv = scraped_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="corpus_by_semantext.csv">Export to CSV</a>'
                        return href
                    st.markdown(download_corpus(scraped_df), unsafe_allow_html=True)
                    
                    st.markdown("---")


    elif option == "Most common words":
        st.markdown("---")
        st.subheader("Most common words")
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
            publication_counts.columns = ["Publication", "Count"] 
            st.write("Articles by Publication:")
            st.table(publication_counts)
            st.markdown("---")
            st.markdown("Merged dataframe")
            st.write(corpus)

        # Create a table for the most frequent words
        if 'corpus' in locals() and st.button("Display most frequent words"):
            n_words = st.text_input("Maximum words", "30")
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
            words_freq = words_freq.sort_values(by="Frequency", ascending=False)
            st.table(words_freq)
            st.set_option('deprecation.showPyplotGlobalUse', False)

            # Download the most frequent words
            def download_mostfrequentwords(words_freq):
                csv = words_freq.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="mostcommonwords_by_semantext.csv">Export to CSV</a>'
                return href
            st.markdown(download_mostfrequentwords(words_freq), unsafe_allow_html=True)

            st.markdown("---")

            # Create a horizontal bar chart using Plotly
            fig = px.bar(
                words_freq,
                x='Frequency',
                y='Word',
                orientation='h',
                labels={'y': 'Word', 'x': 'Frequency'}
            )
            fig.update_layout(
                title=f"Most common words",
                xaxis_title="Frequency",
                yaxis_title="Word",
                autosize=False,
                width=800,
                height=500
            )
            st.plotly_chart(fig)
            st.set_option('deprecation.showPyplotGlobalUse', False)


    elif option == "Rule-Based Collocation":
        st.markdown("---")
        st.subheader("Rule-Based Collocation")
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
            publication_counts.columns = ["Publication", "Count"] 
            st.write("Articles by Publication:")
            st.table(publication_counts)
            st.markdown("---")
            st.markdown("Merged dataframe")
            st.write(corpus)

        # Save collocations as CSV
        def download_collocations(collocations_df):
            csv = collocations_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="collocations_by_semantext.csv">Export to CSV</a>'
            return href

        st.markdown("---")        


        # Extract the possible collocations
        if 'corpus' in locals() and st.button("Extract collocations"):
                # Show a spinner while the collocations are being extracted
                with st.spinner("Extracting collocations..."):
                    collocations_df = extract_collocations(corpus, st)

                # Hide the spinner and display the top collocations and their frequencies in a table
                st.success("Collocations extracted!")
                st.write("Top collocations:")
                st.dataframe(collocations_df.head(50))
                st.markdown(download_collocations(collocations_df), unsafe_allow_html=True)

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

    elif option == "N-gram":
        st.markdown("---")
        st.subheader("N-gram")
        n_value = st.number_input("Enter the value of 'n' for n-grams", min_value=2, step=1, value=2)

        # Add a file uploader for the CSV files
        uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])

        # Merge the uploaded CSV files into a single DataFrame
        if uploaded_files:
            corpus = pd.DataFrame()  # Initialize an empty DataFrame to hold the merged corpus
            total_words = 0  # Initialize a variable to hold the total number of words
            for file in uploaded_files:
                file.seek(0)  # Reset the file pointer to the beginning of the file
                data = pd.read_csv(file)
                corpus = pd.concat([corpus, data], ignore_index=True)
                total_words += data["Text"].str.split().str.len().sum()  # Compute the number of words for the current file

            # Display the total number of rows and words
            st.write(f"Total articles: {len(corpus)}")
            st.write(f"Total words: {total_words}")

        # Extract n-grams
        if 'corpus' in locals() and st.button("Extract n-grams"):
            # Show a spinner while n-grams are being extracted
            with st.spinner("Extracting n-grams..."):
                ngrams_df = extract_ngrams(corpus, n=n_value)

            # Hide the spinner and display the n-grams in a table
            st.success("N-grams extracted!")
            st.write(f"Top {n_value}-grams:")
            st.dataframe(ngrams_df.head(50))

            # Download the extracted n-grams
            def download_ngram(ngrams_df):
                csv = ngrams_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="n_gram_by_semantext.csv">Export to CSV</a>'
                return href
            st.markdown(download_ngram(ngrams_df), unsafe_allow_html=True)

            st.markdown("---")


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
            publication_counts.columns = ["Publication", "Count"] 
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
    
    # Footer
    with st.container():
        st.markdown("---")
        st.markdown("Developed by MW Hidayat. Find me on [Twitter](https://twitter.com/casecrit)")

# Run the Streamlit app
if __name__ == '__main__':
    st.set_page_config(page_title='SemanText', page_icon=':newspaper:')
    app()
