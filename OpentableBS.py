import os 
import sqlite3
from bs4 import BeautifulSoup
import glob
import re

def create_table(cursor, conn):

    cursor.execute('''CREATE TABLE IF NOT EXISTS OpenTable 
                      (id INTEGER PRIMARY KEY, restaurant_name TEXT, number_of_bookings INTEGER, address TEXT, phone_number TEXT)''')
    conn.commit()

def get_daily_bookings(db_name):
    base_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_path, "html_files")

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    create_table(cursor, conn)

    html_files = glob.glob(os.path.join(db_path, "*.html"))

    max_items = 25
    current_items = 0

    for file_path in html_files:
        with open(file_path, "r", encoding="utf-8-sig") as fp:
            listing_page_html = fp.read()
            soup = BeautifulSoup(listing_page_html, "html.parser")

            booking_descriptions_soup = soup.find_all("span", class_="Rv4uk4xWG5CqQmf74o1v cpEOy_DPrbjR6hnlY0ub")
            restaurant_names_soup = soup.find_all("h1", class_="eM9Li2wbkQvvjxZB11sV mPudeIT67bJGOcOfKy92")
            addresses_soup = soup.find_all("p", class_="aAmRZnL9EescJ80holSh")
            phone_numbers_soup = soup.find_all("a", class_="eC8GwYb0MZh6B5cGwcE3 TINDZVVXk9jAAtF9ckbR cpEOy_DPrbjR6hnlY0ub eAmYq9fA8T5DYh2x4An7")

            restaurant_names_list = []
            booking_number_list = []
            addresses_list = []
            phone_numbers_list = []

            all_items_dict = {}

            for name_soup in restaurant_names_soup:
                text = name_soup.get_text()
                if text not in restaurant_names_list:
                    restaurant_names_list.append(text)

            for booking_description_soup in booking_descriptions_soup:
                text = booking_description_soup.get_text()
                for char in text:
                    if char.isdigit():
                        booking_number_list.append(int(char))

            for address_soup in addresses_soup:
                text = address_soup.get_text()
                if text not in addresses_list:  
                    addresses_list.append(text)

            phone_number_pattern = re.compile(r"\(\d{3}\) \d{3}-\d{4}")

            for phone_number_soup in phone_numbers_soup:
                text = phone_number_soup.get_text()
                if not text:
                    phone_numbers_list.append("none")
                else:
                    match = phone_number_pattern.search(text)
                    if match:
                        phone_number = match.group()
                        if phone_number not in phone_numbers_list:
                            phone_numbers_list.append(phone_number)
            
            for i in range(len(booking_descriptions_soup)):
                all_items_dict[current_items] = {
                    'name': restaurant_names_list[i],
                    'bookings': booking_number_list[i],
                    'address': addresses_list[i],
                    'phone_number': phone_numbers_list[i]
                }
                current_items += 1
    return all_items_dict


def insert_into_table(cur, conn, all_items_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    cur_id = cur.execute("SELECT MAX(id) FROM OpenTable").fetchone()[0]
    for i in range(25):
        if cur_id == None:
            cur_id = -1
        
        cur_id += 1

        if cur_id == len(all_items_dict):
            break

        name = all_items_dict[str(cur_id)].get("name")
        bookings =  all_items_dict[str(cur_id)].get("bookings")
        address = all_items_dict[str(cur_id)].get("address")
        phone_number = all_items_dict[str(cur_id)].get("phone_number")
        
        cur.execute(
            '''INSERT OR IGNORE INTO OpenTable
            (id, restaurant_name, number_of_bookings, address, phone_number)
            VALUES (?, ?, ?, ?, ?)''',
            (cur_id, name, bookings, address, phone_number)
        )   
    conn.commit()

#get_daily_bookings("SI206finalproject/OpenTable.db")
