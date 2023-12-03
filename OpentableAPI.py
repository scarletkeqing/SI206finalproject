import os 
import sqlite3
from bs4 import BeautifulSoup
import shutil

def create_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS Bookings 
                      (restaurant_name TEXT, number_of_bookings INTEGER)''')

def insert_data(cursor, restaurant_name, number_of_bookings):
    cursor.execute('''INSERT INTO Bookings (restaurant_name, number_of_bookings) 
                      VALUES (?, ?)''', (restaurant_name, number_of_bookings))

def get_daily_bookings(html_files: list, database_name: str):
    base_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_path, database_name)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    create_table(cursor)
    
    try:
        for html_file in html_files:
            full_path = os.path.join(base_path, html_file)

            with open(full_path, "r", encoding='utf-8') as file:
                html_content = file.read()

                soup = BeautifulSoup(html_content, "html.parser")

                booking_descriptions = soup.find_all("span", class_="phReGjtGv9RByOnBEYKd izPsIMkDXFT6DHsiAQCY")
                restaurant_names = soup.find_all("h6", class_="tfljo0SQq0JS3FOxpvxL")

                booking_number_list = []
                names_list = []

                for booking_description in booking_descriptions:
                    text = booking_description.get_text()
                    for char in text:
                        if char.isdigit():
                            booking_number_list.append(int(char))

                for restaurant_name in restaurant_names:
                    text = restaurant_name.get_text()
                    names_list.append(text)


                # Insert data into the table
                for name, booking_count in zip(names_list, booking_number_list):
                    insert_data(cursor, name, booking_count)


        # Commit changes and close connection
        conn.commit()
        conn.close()

        return "Data inserted into database."

    except Exception as e:
        print("Error occurred:", e)

# Call the function with a list of your HTML files and specify the database name
get_daily_bookings(["first_page.html", "second_page.html"], "restaurant_bookings.db")


        





