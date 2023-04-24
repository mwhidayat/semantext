## Indonesian News Article Scraper

The Indonesian News Article Scraper is a Python web scraping application that is built using the Streamlit framework, and is designed to retrieve news articles from a variety of Indonesian news publishers. The app uses Google Search as the primary search mechanism, and searches for news articles that are related to the user's query string. The user can specify the number of pages they want to scrape, and also provide optional start and end dates to filter results by date range.

## Features

* Retrieval of news article data from a number of popular Indonesian publishers
* Filtering of search results by date range (start and end dates)
* Export of data to CSV format for further analysis

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
7. Click the "Submit" button to start the scraping process.
8. Once the scraping process is complete, the resulting dataframe containing information on the publication date, title, text, URL, and publication name will be displayed.
9. If you wish to download the data as a CSV, click on the "Export to CSV" button located below the resulting dataframe.

## License

This project is licensed under the terms of the MIT license.