import json
import requests
import sqlite3

#create a table
def create_google_maps_table(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS GoogleMapsData
        (name TEXT PRIMARY KEY,
        rating FLOAT,
        total_ratings INT,
        price_range INT,
        address TEXT)'''
    )
    conn.commit()
    conn.close()

# grab ann arbor neighborhoods and their latitudes and longitudes
def get_ann_arbor_locations():
    location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
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

# using the neighborhood data with their latitudes and longitudes, 
# find the nearest restaurants in those areas
def get_googlemap_data(location_dict):
    restaurant_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
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
                total_ratings = restaurant.get("user_ratings_total")
                price_level = restaurant.get("price_level")
                address = restaurant.get("vicinity")
                restaurant_dict[name] = {"rating": rating, "total_ratings": total_ratings, "price_level": price_level, "address": address}
    return restaurant_dict

# put restaurant data into table
def put_restaurant_dict_into_table(restaurant_dict, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    for restaurant in restaurant_dict:
        name = restaurant
        rating = restaurant_dict[restaurant].get("rating")
        total_ratings = restaurant_dict[restaurant].get("total_ratings")
        price_level = restaurant_dict[restaurant].get("price_level")
        address = restaurant_dict[restaurant].get("address")
        cur.execute(
            '''INSERT OR IGNORE INTO GoogleMapsData (name, rating, total_ratings, price_range, address)
            VALUES (?, ?, ?, ?, ?)''',
            (name, rating, total_ratings, price_level, address)
        )
    conn.commit()
    conn.close()