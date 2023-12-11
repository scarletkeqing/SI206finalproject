import sqlite3
import json
import requests
import re
import os

# Function to grab Ann Arbor neighborhoods and their latitudes and longitudes
def get_ann_arbor_locations():
    location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
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
def get_restaurant_details(place_id):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json?"
    api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    detail_parameters = {
        'place_id': place_id,
        'key': api_key
    }
    detail_response = requests.get(details_url, params=detail_parameters)
    detail_data = detail_response.json()

    address = detail_data['result'].get('formatted_address', None)
    phone = detail_data['result'].get('formatted_phone_number', None)

    return [address, phone]

# Function to find the nearest restaurants in Ann Arbor areas and place their info into a dict
def get_googlemap_data(location_dict):
    restaurant_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
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
            if name not in restaurant_dict:
                rating = restaurant.get("rating")
                price_level = restaurant.get("price_level")
                place_id = restaurant.get("place_id")

                address_phone = get_restaurant_details(place_id)
                if address_phone[0]:
                    pattern = "\d+\s+([NSW]?[^,]+)"
                    street_suffixes = ["St", "Ave", "Dr", "Pkwy", "St", "Cir", "Rd", "Hwy", "Blvd", "Ct", "Heights", "Plaza", "Road"]
                    match = re.findall(pattern, address_phone[0])
                    if match:
                        street_match = match[0].split()
                        while street_match != [] and street_match[-1] not in street_suffixes:
                            street_match.pop()
                        street = " ".join(street_match)
                    else:
                        street = None
                else:
                    street = None

                restaurant_dict[count] = {
                    "name": name,
                    "rating": rating, 
                    "price_level": price_level, 
                    "phone": address_phone[1],
                    "street_name": street 
                }
                count += 1

    return restaurant_dict

# Function to read a dictionary from a file
def read_dict_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to make a dictionary of all the streets in restaurant_dict
def get_street_dict(restaurant_dict):
    street_dict = {}
    count = 0
    for restaurant in restaurant_dict.values():
        street = restaurant.get("street_name")
        if street and street not in street_dict.values():
            street_dict[count] = street
            count += 1
    return street_dict

# Function to create a Google Maps data table
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
def insert_into_street_id_table(street_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    for id, street in street_dict.items():
        cur.execute(
            '''INSERT OR IGNORE INTO StreetID (id, street)
               VALUES (?, ?)''',
            (id, street)
        )
    conn.commit()
    conn.close()

# Function to put restaurant data into Google Maps table
def insert_into_google_maps_table(restaurant_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    for id, restaurant in restaurant_dict.items():
        name = restaurant["name"]
        rating = restaurant["rating"]
        price_level = restaurant["price_level"]
        phone = restaurant["phone"]
        street_name = restaurant["street_name"]
        cur.execute(
            "SELECT id FROM StreetID WHERE street = ?",
            (street_name,)
        )
        street_id = cur.fetchone()
        if street_id:
            street_id = street_id[0]
        else:
            street_id = None

        cur.execute(
            "SELECT name FROM GoogleMapsData WHERE name = ?",
            (name,)
        )
        is_in_table = cur.fetchone()
        if is_in_table == None:
            cur.execute(
                '''INSERT OR IGNORE INTO GoogleMapsData
                (id, name, rating, price_range, phone_num, street_id)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (id, name, rating, price_level, phone, street_id)
            )
        else:
            continue
            
    conn.commit()
    conn.close()

# # Main execution
# if __name__ == "__main__":
#     db_name = "test.db"
#     file_path = "googlemaps_api_data.txt"

#     if os.path.exists(file_path):
#         data = read_dict_from_file(file_path)
#     else:
#         locations = get_ann_arbor_locations()
#         data = get_googlemap_data(locations)
#         with open(file_path, 'w') as file:
#             file.write(json.dumps(data))

#     street_data = get_street_dict(data)
#     create_street_id_table(db_name)
#     create_google_maps_table(db_name)
#     insert_into_street_id_table(street_data, db_name)
#     insert_into_google_maps_table(data, db_name)