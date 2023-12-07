import json
import requests
import sqlite3

google_maps_api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
restaurant_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
location_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

#create a table
def create_google_maps_table():
    conn = sqlite3.connect("GoogleMaps.db")
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS GoogleMapsData
        (name TEXT PRIMARY KEY,
        rating FLOAT,
        total_ratings INT,
        price_range INT)'''
    )
    conn.commit()
    conn.close()

# grab ann arbor neighborhoods and their latitudes and longitudes
def get_ann_arbor_locations(url, api_key):
    location_dict = {}
    parameters = {
            'radius': "1000",
            'query': "neighborhoods in ann arbor",
            'key': api_key
        }
    response = requests.get(url, params=parameters)
    data = response.json()
    for location in data['results']:
        neighborhood = location.get('name')
        coord = (location.get('geometry').get('location'))
        location_dict[neighborhood] = coord
    return location_dict

# using the neighborhood data with their latitudes and longitudes, 
# find the nearest restaurants in those areas
def get_googlemap_data(url, api_key, location_dict):
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
        response = requests.get(url, params=parameters)
        data = response.json()
        for restaurant in data["results"]:
            name = restaurant.get("name")
            if name not in restaurant_dict:
                rating = restaurant.get("rating")
                total_ratings = restaurant.get("user_ratings_total")
                price_level = restaurant.get("price_level")
                restaurant_dict[name] = {"rating": rating, "total_ratings": total_ratings, "price_level": price_level}
    return restaurant_dict

# put restaurant data into table
def put_restaurant_dict_into_table(restaurant_dict):
    conn = sqlite3.connect("GoogleMaps.db")
    cur = conn.cursor()
    for restaurant in restaurant_dict:
        name = restaurant
        rating = restaurant_dict[restaurant].get("rating")
        total_ratings = restaurant_dict[restaurant].get("total_ratings")
        price_level = restaurant_dict[restaurant].get("price_level")
        cur.execute(
            '''INSERT OR IGNORE INTO GoogleMapsData (name, rating, total_ratings, price_range)
            VALUES (?, ?, ?, ?)''',
            (name, rating, total_ratings, price_level)
        )
    conn.commit()
    conn.close()

def main():
    create_google_maps_table()
    locations = get_ann_arbor_locations(location_url, google_maps_api_key)
    data = get_googlemap_data(restaurant_url, google_maps_api_key, locations)
    put_restaurant_dict_into_table(data)

main()