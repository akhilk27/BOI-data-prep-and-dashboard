from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import uuid


def save_movies_to_excel(movies, filename='movies3.xlsx'):
    # Check if the Excel file already exists
    if os.path.exists(filename):
        # Load the existing Excel file
        existing_data = pd.read_excel(filename)
    else:
        # If the file does not exist, initialize an empty DataFrame
        existing_data = pd.DataFrame()

    # Create a new DataFrame from the movies list
    new_data = pd.DataFrame(movies)

    # Create a set of existing columns for quick lookup
    existing_columns = set(existing_data.columns)

    # Prepare a list to hold new columns if they are missing
    new_columns = {}

    # Identify missing columns and fill new_columns
    for key in new_data.columns:
        if key not in existing_columns:
            new_columns[key] = [pd.NA] * len(existing_data)

    # Create new columns DataFrame from new_columns dictionary
    if new_columns:
        new_columns_df = pd.DataFrame(new_columns)
        # Concatenate the new columns DataFrame with the existing DataFrame
        existing_data = pd.concat([existing_data, new_columns_df], axis=1)

    # Concatenate the existing and new data
    existing_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Save the updated DataFrame to the Excel file
    existing_data.to_excel(filename, index=False)


# Function to fetch all relevant links from the provided pages
def fetch_movie_links(page_urls):
    all_links = []

    for url in page_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> elements with class "anchormob"
        anchor_tags = soup.find_all('a', class_='anchormob')

        for tag in anchor_tags:
            href = tag.get('href')
            full_link = f"https://www.boxofficeindia.com/{href}"  # Add prefix
            all_links.append(full_link)

    return all_links


# List of pages to scrape for links
page_urls = [
    'https://www.boxofficeindia.com/years.php?year=2020&pageId=4',
    'https://www.boxofficeindia.com/years.php?year=2021&pageId=4',
    'https://www.boxofficeindia.com/years.php?year=2022&pageId=4',
    'https://www.boxofficeindia.com/years.php?year=2023&pageId=4'
    # Add more pages as needed
]

# Fetch movie links from the provided pages
movie_links = fetch_movie_links(page_urls)

# List to store all movies
all_movies = []
ct = 1
# Process each movie link
for movie_url in movie_links:
    print(f"{ct}. Processing URL: {movie_url}")
    ct += 1

    # Request to fetch the page content
    response = requests.get(movie_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the container divs
    movie_boxes = soup.find_all('div', class_='movieboxsleftouter')

    if not movie_boxes:
        print(f"No movie boxes found for URL: {movie_url}")
        continue

    first_movie_box = movie_boxes[0]

    # Getting Movie Name
    movie_name = first_movie_box.find('div', class_='bl_tle_mvi blue_tlte').find('a').text.strip()

    # Extract the release date, runtime, and genre
    target_rdrg = first_movie_box.find_all('div', class_='movieboxssec')[0]
    text_string = target_rdrg.text.strip()

    # Clean up extra whitespace and newlines
    text = ' '.join(text_string.split())
    parts = text.split('|')

    release_date = parts[0].split(':')[1].strip()
    runtime = parts[1].split(':')[1].strip()
    genre = parts[2].split(':')[1].strip()

    # Extract the verdict
    verdict = first_movie_box.find('div', class_='mobileredverdictext').text.strip()
    screens = first_movie_box.find('td', string="Screens:").find_next_sibling('td').find_next_sibling('td').text.strip()
    first_day = first_movie_box.find('td', string="First Day:").find_next_sibling('td').find_next_sibling(
        'td').text.strip()
    opening_note = first_movie_box.find('td', string="Opening Note:").find_next_sibling('td').find_next_sibling(
        'td').text.strip()
    first_weekend = first_movie_box.find('td', string="First Weekend:").find_next_sibling('td').find_next_sibling(
        'td').text.strip()

    # Total Nett Gross
    gross_link = first_movie_box.find('a', string="Total Nett Gross")
    gross_div = gross_link.find_parent('div')
    total_nett_gross = gross_div.get_text(separator=" ", strip=True).split(":")[-1].strip()

    # Utilize second_movie_box
    movie_box_secs = soup.find_all('div', class_='movieboxssec')
    second_movie_box = movie_box_secs[3]


    # Define a function to extract table data based on a provided keyword
    def extract_value(body, text):
        anchor = body.find('a', string=text)
        if anchor:
            data_td = anchor.find_parent('td').find_next_sibling('td').find_next_sibling('td')
            return data_td.get_text(strip=True) if data_td else None
        return None


    # Extract values for each key field
    first_week = extract_value(second_movie_box, "First Week: ")
    budget = extract_value(second_movie_box, "Budget:")
    india_gross = extract_value(second_movie_box, "India Gross:")
    overseas_gross = extract_value(second_movie_box, "Overseas Gross:")
    worldwide_gross = extract_value(second_movie_box, "Worldwide Gross:")
    footfalls = extract_value(second_movie_box, "Footfalls:")
    adjusted_nett_gross = extract_value(second_movie_box, "Adjusted Nett Gross:")

    # Extract Weekly Territory URLs
    menu_container = soup.find('ul', id="menucontainer")
    weekly_territory_urls = [link['href'] for link in menu_container.find_all('a', href=True)]

    # ########################## Obtaining Weekly Data ########################################
    weekly_data = {}


    # Function to get weekly and territory collections for each URL
    def get_weekly_data(weekly_url, week_number):
        appended_url = 'https://boxofficeindia.com/' + weekly_url
        weekly_data_response = requests.get(appended_url)
        weekly_data_soup = BeautifulSoup(weekly_data_response.text, 'html.parser')

        sub_section = weekly_data_soup.find_all('div', class_='movieboxssec')[2]

        # Loop through each territory's collection for that week
        territories = sub_section.find_all('div', class_='movieim6')
        for territory in territories:
            territory_name = territory.find('a').get_text(strip=True).replace(" / ", "_").replace(" ", "_").lower()
            territory_collection = territory.find_all('td')[1].get_text(strip=True)

            # Store data with the week and territory prefix
            weekly_data[f"week{week_number}_{territory_name}"] = territory_collection


    # Iterate over each weekly URL and extract data
    for i, url in enumerate(weekly_territory_urls, start=1):
        get_weekly_data(url, week_number=i)


    # ############################################# Production Banner #################################################
    banner_div = soup.find('div', class_='movieim7')
    banners = [a.get_text(strip=True) for a in banner_div.find_all('a')]
    banner_names = ', '.join(banners)

    # ############################################## Cast and Crew ###################################################
    cast_crew = soup.find('div', class_="movieim8")
    actors = [actor.get_text(strip=True) for actor in cast_crew.find_all('td', width="87%")]

    crew_info = {}
    crew_table = cast_crew.find('table', class_='actrsmovie')

    # Extract roles and names for crew members
    for row in crew_table.find_all('tr'):
        role_cell, name_cell = row.find_all('td')
        role = role_cell.get_text(strip=True) or 'Producer'
        name = name_cell.get_text(strip=True)

        if role not in crew_info:
            crew_info[role] = []
        crew_info[role].append(name)

    crew_info = {role: ', '.join(names) for role, names in crew_info.items()}


    # ################################################ Final Revenue ######################################################
    total_collections = soup.find_all('div', class_='boxlisting2')
    collections_data = {}

    for coll in total_collections:
        region_name = coll.find('td').find('a').text.strip().replace(" ", "_").lower()
        totals = coll.find_all('td')[1].text.strip()

        # if "Total Nett:" in totals:
        #     nett = totals.split("Total Nett: ")[1].split(" | ")[0].strip()
        #     share = totals.split("Share: ")[1].split(" | ")[0].strip()
        #     collections_data[f"{region_name}_nett"] = nett
        #     collections_data[f"{region_name}_share"] = share

        # For India territories, extract nett and share
        if "Total Nett:" in totals:
            nett = totals.split("Total Nett: ")[1].split(" | ")[0].strip()
            share = totals.split("Share: ")[1].strip()
            collections_data[f"{region_name}_total_nett"] = nett.split("|")[0].strip()
            collections_data[f"{region_name}_share"] = share
        # For overseas territories, extract first weekend and total gross
        elif "First Weekend :" in totals:
            overseas_first_weekend = totals.split("First Weekend : ")[1].split(" | ")[0].strip()
            overseas_total_gross = totals.split("Total Gross: ")[1].strip()
            collections_data[f"{region_name}_overseas_first_weekend"] = overseas_first_weekend.split("|")[0].strip()
            collections_data[f"{region_name}_overseas_total_gross"] = overseas_total_gross


    # Merge all collected data into a single movie record
    movie_data = {
        'movie_id': str(uuid.uuid4()),
        'name': movie_name,
        'release_date': release_date,
        'runtime': runtime,
        'genre': genre,
        'verdict': verdict,
        'banners': banner_names,
        'actors': ', '.join(actors),
        'screens': screens,
        'first_day': first_day,
        'opening_note': opening_note,
        'budget': budget,
        'first_weekend': first_weekend,
        'first_week': first_week,
        'total_nett_gross': total_nett_gross,
        'india_gross': india_gross,
        'overseas_gross': overseas_gross,
        'worldwide_gross': worldwide_gross,
        'footfalls': footfalls,
        'adjusted_nett_gross': adjusted_nett_gross,
        **crew_info,
        **weekly_data,
        **collections_data,
    }

    # Append movie data to the all_movies list
    all_movies.append(movie_data)

# Save all movies data to Excel
save_movies_to_excel(all_movies)
