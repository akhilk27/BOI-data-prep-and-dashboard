# BOI-data-prep-and-dashboard

Dashboard link: https://public.tableau.com/app/profile/akhilesh.reddy4076/viz/BO_Dashboard/BOOverview

In this project, I implemented a web scraping solution using Python's BeautifulSoup and Requests libraries to collect detailed information about movies from Box Office India. I extracted various attributes for each movie, including release date, runtime, genre, verdict, budget, and box office collections across different territories. The scraped data was then organized into a structured format and stored in an CSV file, allowing for easy analysis and visualization.

Then, I developed a comprehensive data processing and analysis pipeline using PySpark to manage and analyze movie data. The pipeline ingested the raw movie dataset, performed data cleansing and transformation to ensure accuracy and consistency, and integrated various metrics such as actor performance, box office earnings, and genre success. 

I then visualized the processed data through an interactive Tableau dashboard, enabling users to filter and analyze trends based on actor, release year, genre, and region. This project aims to assist movie distributors in evaluating distribution rights and help producers make informed budget decisions by leveraging historical performance insights.


#### Code Files

1. `boi_web_scrapping.py`: Python script to extract required data from the website pages.
2. `Movies_BO_Dataset_Cleaning.ipynb`: Python notebook containing all the code required to preprocess the raw data using PySpark.

#### Data Files

1. `movies6.csv` : Raw dataset containing the data from web scrapping performed in `boi_web_scrapping.py`.
2. `movies_corrected_1.csv`: Preprocessed dataset obtained after running the data processing file in `Movies_BO_Dataset_Cleaning.ipynb`.
3. `conversion_rate.csv`: Contains year-by-year details for converting the overseas data into INR.
