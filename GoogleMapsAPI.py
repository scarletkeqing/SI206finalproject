import sqlite3
import json
import requests
import re
import os

# Function to write a dictionary from a file
# Parameters: a dict, the name of the file that will be written (as a str)
# Returns: none
def write_dict_into_file(a_dict, filename):
    base_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_path, filename)
    with open(file_path, 'w') as file:
        file.write(json.dumps(a_dict))

# Function to read a dictionary from a file
# Parameters: the name of the file that would be read (as a str)
# Returns: a dict that was read from the file
def read_dict_from_file(filename):
    base_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_path, filename)
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to grab Ann Arbor neighborhoods and their latitudes and longitudes
# Is used to get locations for get_googlemap_data
# Parameters: none
# Returns: a dict with the locations in ann arbor 
def get_ann_arbor_locations():
    location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    #api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    api_key = "AIzaSyAlwKaR-BubU6fgsvlx72Hv-yL7bqGF4gM"
    location_dict = {}
    parameters = {
        'radius': "1000",
        'query': "most popular neighborhoods in ann arbor",
        'key': api_key
    }
    response = requests.get(location_url, params=parameters)
    data = response.json()

    for i in range(10):
        neighborhood = data['results'][i].get('name')
        coord = data['results'][i].get('geometry').get('location')
        location_dict[neighborhood] = coord
    return location_dict

# Function to get street and phone number from restaurant
# Is used in get_google_data to get phone number and street
# Parameters: a place_id (a str, found in get_googlemap_data)
# Returns: a lst with the address and phone number of the location from place_id
def get_restaurant_details(place_id):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json?"
    #api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    api_key = "AIzaSyAlwKaR-BubU6fgsvlx72Hv-yL7bqGF4gM"
    detail_parameters = {
        'place_id': place_id,
        'key': api_key
    }
    detail_response = requests.get(details_url, params=detail_parameters)
    detail_data = detail_response.json()

    address = detail_data['result'].get('formatted_address', None)
    phone = detail_data['result'].get('formatted_phone_number', None)

    return [address, phone]

# Function to find the nearest restaurants in Ann Arbor areas and place their info into a dict and written as a .txt file
# Is used to get data for the database table GoogleMapsData
# Uses get_restaurant_details and write_dict_into_file
# Parameters: location_dict (found from get_ann_arbor_locations)
# Returns: none (writes restaurant_dict (a dict with unique restaurants) into a .txt file)
def get_googlemap_data(location_dict):
    restaurant_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    #api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    api_key = "AIzaSyAlwKaR-BubU6fgsvlx72Hv-yL7bqGF4gM"
    restaurant_dict = {}
    count = 0

    for neighborhood in location_dict:
        lat = location_dict[neighborhood]["lat"]
        lng = location_dict[neighborhood]["lng"]
        parameters = {
            'location': f"{lat},{lng}",
            'type': 'restaurant',
            'rankby': 'distance',
            'key': api_key
        }
        response = requests.get(restaurant_url, params=parameters)
        data = response.json()

        for restaurant in data["results"]:
            name = restaurant.get("name")
            rating = restaurant.get("rating")
            price_level = restaurant.get("price_level")
            place_id = restaurant.get("place_id")

            address_phone = get_restaurant_details(place_id)
            pattern = "\d+\s+([NSWE]?[^,]+)"
            street_suffixes = ["St", "Ave", "Dr", "Pkwy", "St", "Cir", "Rd", "Hwy", "Blvd", "Ct", "Heights", "Plaza", "Road"]
            match = re.findall(pattern, address_phone[0])
            if match:
                street_match = match[0].split()
                while street_match != [] and street_match[-1] not in street_suffixes:
                    street_match.pop()
                street = " ".join(street_match)
            restaurant_info = {
                "name": name,
                "rating": rating, 
                "price_level": price_level, 
                "phone": address_phone[1],
                "street_name": street 
            }
            if restaurant_info not in restaurant_dict.values():
                restaurant_dict[count] = restaurant_info
                count += 1
            else:
                continue
    write_dict_into_file(restaurant_dict, "googlemaps_api_data.txt")

# Function to make a dictionary of all the streets in restaurant_dict
# Is used to get info for StreetID table in database
# Parameters: restaurant_dict (from .txt file)
# Returns: street_dict (a dict with all unique streets)
def get_street_dict(restaurant_dict):
    street_dict = {}
    count = 0
    for restaurant in restaurant_dict.values():
        street = restaurant.get("street_name")
        if street not in street_dict.values():
            street_dict[count] = street
            count += 1
    return street_dict

# Function to create a Google Maps data table
# Parameters: database name (as a str)
# Returns: none
def create_google_maps_table(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS GoogleMapsData
        (id INT PRIMARY KEY,
        name TEXT,
        rating FLOAT,
        price_range INT,
        phone_num TEXT,
        street_id INT)'''
    )
    conn.commit()
    conn.close()

# Function to create a Street ID table
# Parameters: database name (as a str)
# Returns: none
def create_street_id_table(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS StreetID
           (id INT PRIMARY KEY,
            street TEXT)'''
    )
    conn.commit()
    conn.close()

# Function to insert data into the Street ID table
# Parameters: street_dict (dict of unique street names), database name (as a str)
# Returns: none
def insert_into_street_id_table(street_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur_id = cur.execute("SELECT MAX(id) FROM StreetID").fetchone()[0]
    for i in range(25):
        if cur_id == None:
            cur_id = -1
        
        cur_id += 1

        if cur_id == len(street_dict):
            break

        street = street_dict.get(cur_id)
        cur.execute(
            '''INSERT OR IGNORE INTO StreetID (id, street)
               VALUES (?, ?)''',
            (cur_id, street)
        )

    conn.commit()
    conn.close()

# Function to put restaurant data into Google Maps table
# Parameters: restaurant_dict (dict of unique restaurants in .txt file), database name (as a str)
# Returns: none
def insert_into_google_maps_table(restaurant_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur_id = cur.execute("SELECT MAX(id) FROM GoogleMapsData").fetchone()[0]
    for i in range(25):
        if cur_id == None:
            cur_id = -1
        
        cur_id += 1

        if cur_id == len(restaurant_dict):
            break

        name = restaurant_dict[str(cur_id)].get("name")
        rating =  restaurant_dict[str(cur_id)].get("rating")
        price_level = restaurant_dict[str(cur_id)].get("price_level")
        phone = restaurant_dict[str(cur_id)].get("phone")
        street_name = restaurant_dict[str(cur_id)].get("street_name")
        cur.execute(
            "SELECT id, street FROM StreetID WHERE street = ?",
            (street_name,)
        )
        street_id = cur.fetchone()
        if street_id:
            street_id = street_id[0]
        else:
            street_id = None

        cur.execute(
            '''INSERT OR IGNORE INTO GoogleMapsData
            (id, name, rating, price_range, phone_num, street_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (cur_id, name, rating, price_level, phone, street_id)
        )   
    conn.commit()

# for testing
# db_name = "test.db"
# filename = "googlemaps_api_data.txt"

# if os.path.exists(filename):
#     data = read_dict_from_file(filename)
# else:
#     locations = get_ann_arbor_locations()
#     get_googlemap_data(locations)
#     data = read_dict_from_file(filename)

# street_data = get_street_dict(data)
# create_street_id_table(db_name)
# create_google_maps_table(db_name)
# insert_into_street_id_table(street_data, db_name)
# insert_into_google_maps_table(data, db_name)