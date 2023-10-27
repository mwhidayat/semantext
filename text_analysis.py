import collections
import pandas as pd
import string
import streamlit as st
import re
import stanza
import pandas as pd
import os
import time
from tqdm import tqdm
from typing import List
from collections import Counter

script_dir = os.path.dirname(os.path.abspath(__file__))
stopwords_file_path = os.path.join(script_dir, 'stopwords.txt')

with open(stopwords_file_path, 'r') as file:
    stop_words = file.read().split('\n')
    stop_words = set(stop_words)

# Define a function to remove stop words
def stopwords_removal(words):
    # Remove punctuation characters
    table = str.maketrans('', '', string.punctuation)
    words = [w.translate(table) for w in words]

    # Remove stop words
    return [word for word in words if word.lower() not in stop_words]

# Define a function to plot a bar chart of most frequent words
def plot_n_most_frequent_words(dataframe, column_name, n=10):
    # Concatenate all the text data in the specified column
    text = " ".join(dataframe[column_name].astype(str).tolist()).lower()

    # Use Counter to count the frequency of each word in the text
    word_counts = Counter(text.split())

    # Get the n most common words and their respective counts
    top_n_words = word_counts.most_common(n)
    top_n_words.reverse()  # Reverse the order to display most frequent words on top

    return top_n_words

# Define a function to extract collocations
def extract_collocations(corpus, progress):
    # create a Stanza pipeline for Indonesian
    nlp = stanza.Pipeline('id')

    # Initialize empty lists to store the collocations, pos patterns, and frequencies
    collocations = []
    pos_patterns = []
    frequencies = []

    # Iterate through the rows in the dataframe
    progress = st.progress(0)
    # Iterate through the rows in the dataframe
    start_time = time.time()
    for index, row in tqdm(corpus.iterrows(), total=corpus.shape[0]):
        # Extract the collocations using the Stanza library
        doc = nlp(row['Text'])
        for sent in doc.sentences:
            for i, word in enumerate(sent.words):
                # If the word is a noun and there is a next word, check if it is an adjective or noun
                if word.pos == 'NOUN' and i < len(sent.words) - 1:
                    if sent.words[i + 1].pos == 'ADJ':
                        collocations.append(f"{word.text} {sent.words[i + 1].text}")
                        pos_patterns.append('NOUN + ADJ')
                        frequencies.append(1)
                    elif sent.words[i + 1].pos == 'NOUN':
                        collocations.append(f"{word.text} {sent.words[i + 1].text}")
                        pos_patterns.append('NOUN + NOUN')
                        frequencies.append(1)
                # If the word is a verb and there is a next word, check if it is a noun
                elif word.pos == 'VERB' and i < len(sent.words) - 1:
                    if sent.words[i + 1].pos == 'NOUN':
                        collocations.append(f"{word.text} {sent.words[i + 1].text}")
                        pos_patterns.append('VERB + NOUN')
                        frequencies.append(1)

        # Update the progress bar with elapsed time
        elapsed_time = time.time() - start_time
        progress.progress((index + 1) / corpus.shape[0], f"Processed {index+1} articles in {elapsed_time:.2f} seconds")


    # Create a new dataframe with the collocations, pos patterns, and frequencies
    collocations_df = pd.DataFrame({'collocations': collocations, 'pos_pattern': pos_patterns, 'frequency': frequencies})
    collocations_df = collocations_df.groupby(['collocations', 'pos_pattern']).sum().reset_index()
    collocations_df.sort_values(by='frequency', ascending=False, inplace=True)

    return collocations_df

# N-gram extraction without external libraries
def extract_ngrams(corpus, n):
    # Initialize an empty dictionary to store n-gram frequencies
    ngram_counter = {}

    # Create a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)

    # Iterate through the rows in the corpus
    for index, row in tqdm(corpus.iterrows(), total=corpus.shape[0]):
        text = row['Text']
        
        # Remove punctuation
        text = text.translate(translator)
        
        words = text.split()

        # Extract n-grams
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i + n])
            if ngram in ngram_counter:
                ngram_counter[ngram] += 1
            else:
                ngram_counter[ngram] = 1

    # Convert the dictionary to a DataFrame with n-grams and frequencies
    ngrams_df = pd.DataFrame({'ngram': list(ngram_counter.keys()), 'frequency': list(ngram_counter.values())})

    # Sort by frequency in descending order
    ngrams_df = ngrams_df.sort_values(by='frequency', ascending=False)

    return ngrams_df

# Create a function to generate Concordance - Key Words in Context
def generate_concordance(text, keyword, context_size=50):
    lines = text.split('\n')
    concordance = []
    for i, line in enumerate(lines):
        match = re.search(rf"\b{keyword}\b", line, re.IGNORECASE)
        if match:
            start = max(0, match.start() - context_size)
            end = min(len(line), match.end() + context_size)
            context = line[start:end]
            context = re.sub(rf"\b{keyword}\b", f"[{keyword}]", context, flags=re.IGNORECASE)
            concordance.append((i, context))
    return concordance

def display_concordance(data: pd.DataFrame, col: str, keyword: str, window_size: int = 7) -> pd.DataFrame:
    concordance_lines = []
    
    for index, row in data.iterrows():
        text = row[col]
        words = text.split()
        
        for i, word in enumerate(words):
            if word == keyword:
                start = max(0, i - window_size)
                end = min(len(words), i + window_size + 1)
                left_context = ' '.join(words[start:i])
                keyword_in_context = ' '.join(words[i:i+1])  # keyword in context is just the keyword itself
                right_context = ' '.join(words[i+1:end])
                
                concordance_lines.append({
                    "Left context": left_context,
                    "KWIC": keyword_in_context,
                    "Right context": right_context,
                    "Publication": row["Publication"],
                    "Title": row["Title"]

                })
                
    concordance_df = pd.DataFrame(concordance_lines)
    return concordance_df