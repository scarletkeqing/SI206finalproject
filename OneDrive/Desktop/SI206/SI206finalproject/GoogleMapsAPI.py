import json
import requests
import sqlite3
import re

#create a googlemaps table
def create_google_maps_table(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS GoogleMapsData
        (name TEXT PRIMARY KEY,
        rating FLOAT,
        price_range INT,
        phone_num TEXT,
        street_id INT)'''
    )
    conn.commit()
    conn.close()

# grab ann arbor neighborhoods and their latitudes and longitudes
def get_ann_arbor_locations():
    location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    #api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
    api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    location_dict = {}
    parameters = {
            'radius': "1000",
            'query': "neighborhoods in ann arbor",
            'key': api_key
        }
    response = requests.get(location_url, params=parameters)
    data = response.json()
    for location in data['results']:
        neighborhood = location.get('name')
        coord = (location.get('geometry').get('location'))
        location_dict[neighborhood] = coord
    return location_dict

# get street and phone number from restaurant
# used in get_googlemap_data
def get_restaurant_details(place_id):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json?"
    #api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
    api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    detail_parameters = {
                    'place_id': place_id,
                    'key': api_key
                }
    detail_response = requests.get(details_url, params=detail_parameters)
    detail_data = detail_response.json()
    if 'formatted_address' in detail_data['result']:
        address = detail_data['result']['formatted_address']
    else:
        address = None
    if 'formatted_phone_number' in detail_data['result']:        
        phone = detail_data['result']['formatted_phone_number']
    else:
        phone = None
    address_phone = [address, phone]
    return address_phone

# using the neighborhood data with their latitudes and longitudes, 
# find the nearest restaurants in those areas and place their info into a dict
def get_googlemap_data(location_dict):
    restaurant_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    #api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
    api_key = "AIzaSyB2LEgv98plD1dwVoXA_fYStO58c4Z_HvA"
    restaurant_dict = {}
    for neighborhood in location_dict:
        lat = location_dict[neighborhood]["lat"]
        long = location_dict[neighborhood]["lng"]
        parameters = {
            'location': f"{lat},{long}",
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
                pattern = "\d+\s+([NSW]?[^,]+)"
                match = re.findall(pattern, address_phone[0])
                street_match = (match[0]).split()
                street = ""
                if len(street_match) > 3:
                    if len(street_match[0]) == 1:
                        street_match = street_match[:3]
                        street = " ".join(street_match)
                    else:
                        street_match = street_match[:2]
                        street = " ".join(street_match)
                elif len(street_match) == 3:
                    if len(street_match[0]) == 1:
                        street = " ".join(street_match)  
                    else:
                        street_match = street_match[:2]
                        street = " ".join(street_match)
                else:
                    street = " ".join(street_match)     

                restaurant_dict[name] = {
                    "rating": rating, 
                    "price_level": price_level, 
                    "phone": address_phone[1],
                    "street_name": street 
                }
    return restaurant_dict

# creates Street ID table
def create_street_id_table(restaurant_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS StreetID
        (id INT PRIMARY KEY,
        street TEXT)'''
    )
    street_list = []
    for restaurant in restaurant_dict:
        street = restaurant_dict[restaurant]["street_name"]
        if street not in street_list: 
            street_list.append(street)
            cur.execute(
                '''INSERT OR IGNORE INTO StreetID (id, street)
                VALUES (?, ?)''',
                (street_list.index(street), street)
            )
    conn.commit()
    conn.close()

# put restaurant data into table
def put_restaurant_dict_into_table(restaurant_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    for restaurant in restaurant_dict:
        name = restaurant
        rating = restaurant_dict[restaurant].get("rating")
        price_level = restaurant_dict[restaurant].get("price_level")
        phone = restaurant_dict[restaurant].get("phone")
        street_name = restaurant_dict[restaurant].get("street_name")
        cur.execute(
            "SELECT id, street FROM StreetID WHERE street = ?",
            (street_name,)
        )
        street_id_list = cur.fetchall()
        street_id_tup = street_id_list[0]
        street_id = street_id_tup[0]
        cur.execute(
            '''INSERT OR IGNORE INTO GoogleMapsData (name, rating, price_range, phone_num, street_id)
            VALUES (?, ?, ?, ?, ?)''',
            (name, rating, price_level, phone, street_id)
        )
    conn.commit()
    conn.close()

#locations = get_ann_arbor_locations()
#data = get_googlemap_data(locations)
#put_restaurant_dict_into_table(data, "test.db")

# create_google_maps_table("test.db")
# locations = get_ann_arbor_locations()
# data = get_googlemap_data(locations)
# create_street_id_table(data, "test.db")
# put_restaurant_dict_into_table(data, "test.db")