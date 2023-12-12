import os 
import sqlite3
from bs4 import BeautifulSoup
import glob
import re
import json

# Creates a table in the SQLite database if it doesn't already exist
def create_table(cursor, conn):
    cursor.execute('''CREATE TABLE IF NOT EXISTS OpenTable 
                      (id INTEGER PRIMARY KEY, 
                       restaurant_name TEXT, 
                       number_of_bookings INTEGER, 
                       address TEXT, 
                       phone_number TEXT)''')
    conn.commit()


# Extracts the booking number from a text string using regular expression
# Returns an integer representing the number of times booked
def extract_booking_number(text):
    match = re.search(r'Booked (\d+) times today', text)
    return int(match.group(1)) if match else 0


# Extracts the phone number from a text string using regular expression
# Returns a string representing the phone number
def extract_phone_number(text):
    phone_number_pattern = re.compile(r"\(\d{3}\) \d{3}-\d{4}")
    match = phone_number_pattern.search(text)
    return match.group() if match else 'none'


# Reads and returns a set of processed file names from a JSON file
# If the file doesn't exist, returns an empty set
def get_processed_files():
    try:
        with open('processed_files.json', 'r') as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()


# Saves a set of processed file names into a JSON file
def save_processed_files(processed_files_set):
    with open('processed_files.json', 'w') as file:
        json.dump(list(processed_files_set), file)


# Reads HTML files from a directory, extracts restaurant data, and 
# returns a dictionary with the extracted data and a set of processed files
# Only processes up to 25 new entries each run
def get_daily_bookings(db_name, processed_files_set):
    base_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_path, "html_files")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    create_table(cursor, conn)

    html_files = glob.glob(os.path.join(db_path, "*.html"))
    current_items = 0
    all_items_dict = {}

    for file_path in html_files:
        if file_path in processed_files_set:
            continue 

        if current_items >= 25:
            break

        with open(file_path, "r", encoding="utf-8-sig") as fp:
            listing_page_html = fp.read()
            soup = BeautifulSoup(listing_page_html, "html.parser")

            booking_descriptions_soup = soup.find_all("span", class_="Rv4uk4xWG5CqQmf74o1v cpEOy_DPrbjR6hnlY0ub")
            restaurant_names_soup = soup.find_all("h1", class_="eM9Li2wbkQvvjxZB11sV mPudeIT67bJGOcOfKy92")
            addresses_soup = soup.find_all("p", class_="aAmRZnL9EescJ80holSh")

            phone_number_pattern = re.compile(r'\(\d{3}\) \d{3}-\d{4}')
            phone_numbers_found = phone_number_pattern.findall(listing_page_html)

            restaurant_names_list = [name.get_text() for name in restaurant_names_soup]
            booking_number_set = set(extract_booking_number(booking.get_text()) for booking in booking_descriptions_soup)
            booking_number_list = list(booking_number_set)
            addresses_list = [address.get_text() for address in addresses_soup]

            for i in range(len(restaurant_names_list)):
                if current_items >= 25:
                    break

                phone_number = phone_numbers_found[0] if phone_numbers_found else 'none'
                all_items_dict[current_items] = {
                    'name': restaurant_names_list[i],
                    'bookings': booking_number_list[i % len(booking_number_list)] if booking_number_list else 0,
                    'address': addresses_list[i],
                    'phone_number': phone_number
                }
                current_items += 1

        processed_files_set.add(file_path) 

    conn.close()
    return all_items_dict, processed_files_set


# Inserts data from a dictionary into the OpenTable table in the SQLite database
# Ensures no duplicate data is inserted
def insert_into_table(cur, conn, all_items_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    for item in all_items_dict.values():
        cur.execute(
            '''SELECT id FROM OpenTable WHERE restaurant_name = ? AND address = ? AND phone_number = ?''',
            (item['name'], item['address'], item['phone_number'])
        )
        existing_id = cur.fetchone()

        if not existing_id:
            cur.execute(
                '''INSERT INTO OpenTable
                   (restaurant_name, number_of_bookings, address, phone_number)
                   VALUES (?, ?, ?, ?)''',
                (item['name'], item['bookings'], item['address'], item['phone_number'])
            )

    conn.commit()
    conn.close()

# for testing
# db_name = 'BaoBuddies.db'
# processed_files = get_processed_files()

# all_items, processed_files = get_daily_bookings(db_name, processed_files)
# save_processed_files(processed_files)  # Save the state of processed files

# conn = sqlite3.connect(db_name)
# cursor = conn.cursor()
# insert_into_table(cursor, conn, all_items, db_name)
# conn.close()

