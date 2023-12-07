import os 
import sqlite3
from bs4 import BeautifulSoup
import glob

def create_table(cursor, conn):
    cursor.execute('''CREATE TABLE IF NOT EXISTS Bookings 
                      (id INTEGER PRIMARY KEY, restaurant_name TEXT, number_of_bookings INTEGER, address TEXT)''')
    conn.commit()

def insert_into_table(cursor, conn, name, num_of_bookings, address):
    cursor.execute("INSERT INTO Bookings (id, restaurant_name, number_of_bookings, address) VALUES (?, ?, ?)", (id, name, num_of_bookings, address))
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

            restaurant_names_list = []
            booking_number_list = []
            addresses_list = []

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

            for i in range(min(len(restaurant_names_list), len(booking_number_list), len(addresses_list))):
                insert_into_table(cursor, conn, restaurant_names_list[i], booking_number_list[i], addresses_list[i])
                current_items += 1

                if current_items >= max_items:
                    conn.close()
                    return 

get_daily_bookings("SI206finalproject/restaurant_bookings.db")
