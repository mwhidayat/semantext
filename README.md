## SemanText

SemanText is a linguistic tool for the Indonesian corpus developed using the Streamlit framework. It is designed to simplify the analysis of news articles sourced from popular Indonesian news publishers. Whether you're a linguist, researcher, or language enthusiast, SemanText offers a suite of features tailored to enhance your exploration and understanding of textual data.

## Phase 1 (Done)

- [x] **URL Scraper:** Effortlessly scrape articles by providing a list of URLs saved in a .txt file, each separated by a line break.
- [x] **Multiple CSV Files:** Seamlessly manage and handle multiple CSV files for efficient data organization.
- [x] **Most Frequent Words:** Quickly identify and analyze the most frequently occurring words in the corpus.
- [x] **N-gram Extraction - Frequency:** Uncover insights through the extraction and frequency analysis of N-grams.
- [x] **Rule-Based Collocation Extraction - Frequency:** Utilizing the Stanza library, leverage three distinct patterns of Part-of-Speech tags grounded in the Universal Dependencies model for Indonesian:
  
  1. **NOUN + ADJ:** Discover meaningful collocations where a noun is paired with an adjective.
  2. **NOUN + NOUN:** Uncover insights into frequent noun pairings.
  3. **VERB + NOUN:** Explore the dynamic interplay between verbs and nouns.

- [x] **Key Word in Context/Concordance:** Gain contextual understanding by exploring the occurrence of specific keywords within the corpus.
- [x] **Export Data to CSV Format:** Easily export analyzed data to CSV format for further in-depth analysis.

## Phase 2 (To Do)

- [ ] **Statistical Measures for Collocation Extraction:** Calculate and display statistical measures, such as Pointwise Mutual Information (PMI), to identify and interpret collocations better, instead of plain frequency.
- [ ] **CONLL-U File Analysis:** Read and parse CONLL-U file, which are a standard format for representing linguistic annotations.
- [ ] **Keyword-Based Collocation Extraction:** Extract collocations that include a certain keyword.

## Phase 3 (Backlog)

- [ ] **Scraper - Google Search:** Retrieve articles based on specific queries for Google Search.
- [ ] **Machine Learning - Topic Modelling:** Identify and group similar articles based on their content using unsupervised machine learning algorithms.


## System Requirements

- **Python 3.7 or Higher:** Ensure your Python version is 3.7 or higher for compatibility.

## Installation

1. **Clone the Repository:** Copy the repository to your local machine.
2. **Install Dependencies:** Run the command `pip install -r requirements.txt` to install the required dependencies.

## Demo

Experience the tool firsthand by exploring the demo [here](https://semantext.streamlit.app/).

## License

This project is licensed under the terms of the MIT license. Feel free to contribute and enhance the capabilities of SemanText. Your feedback and contributions are highly appreciated!
