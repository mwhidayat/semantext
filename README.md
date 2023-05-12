## SemanText

SemanText is an Indonesian corpus linguistic tool developed using the Streamlit framework. It provides a wide range of features specifically designed to facilitate the analysis of news articles from popular Indonesian news publishers. With SemanText, you can easily retrieve news articles based on your queries, specify the desired number of pages to scrape, and conduct corpus linguistic analysis using its built-in features.

## Features

* Retrieval of news article data from a number of popular Indonesian publishers
* Filtering of search results by date range (start and end dates)
* Export of data to CSV format for further analysis
* Collocation extraction
* Most frequent words plot and wordcloud
* Key Word in Context / Concordance

## System Requirements

* Python 3.7 or higher
* Internet connection for scraping news article data

## Installation

1. Clone the repository to your local machine.
2. Install the required dependencies by running the command `pip install -r requirements.txt`

## Usage

1. Navigate to the directory where the app is stored.
2. Run the app by executing the command `streamlit run app.py`.
3. In the app interface, enter a search query keyword or phrase in the text input box provided.
4. Select the publisher's domain where you want to search for news from the available options in the radio button.
5. (Optional) Enter the start and end date in the provided text input boxes to scrape articles within a specific date range. The format should be in yyyy-mm-dd.
6. Enter the number of pages to scrape in the text input box provided. Each page usually contains 10 articles.
7. Once the scraping process is complete, the resulting dataframe containing information on the publication date, title, text, URL, and publication name will be displayed.
8. If you wish to download the data as a CSV, click on the "Export to CSV" button located below the resulting dataframe.

## Demo

You can play around with the demo here: https://mwhidayat-indonesian-news-scraper-app-2x53nz.streamlit.app/


## License

This project is licensed under the terms of the MIT license.
