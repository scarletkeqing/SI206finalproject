import json
import requests
import sqlite3

google_maps_api_key = "AIzaSyCsKZblWthpw-MxkuF4drKL9TZQRwfGIXE"
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

def create_google_maps_db():
    conn = sqlite3.connect("GoogleMaps.db")
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS GoogleMapsData
        (name TEXT PRIMARY KEY,
        rating FLOAT,
        total_ratings INT)'''
    )
    conn.commit()
    conn.close()

def input_google_maps_data_in_db(name, rating, total_ratings):
    conn = sqlite3.connect("GoogleMaps.db")
    cur = conn.cursor()

    cur.execute(
            '''INSERT OR IGNORE INTO GoogleMapsData (name, rating, total_ratings)
            VALUES (?, ?, ?)''',
            (name, rating, total_ratings)
        )
    conn.commit()
    conn.close()

def get_googlemap_data(url, api_key):
    ann_arbor_locations = {
        "central_campus":{"lat": "42.2766", "long": "-83.7426"},
        "downtown": {"lat": "42.2807", "long": "-83.7463"},
        "kerrytown": {"lat": "42.2862", "long": "-83.7451"},
        "north_campus": {"lat": "39.2184", "long": "-84.5508"},
        "northside": {"lat": "42.2981", "long": "-83.7321"},
        "old_west_side": {"lat": "42.27518", "long": "-83.75667"},
    }
    restaurant_dict = {}

    for area in ann_arbor_locations:
        lat = ann_arbor_locations.get(area)["lat"]
        long = ann_arbor_locations.get(area)["long"]
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
                restaurant_dict[name] = {"rating": rating, "total_ratings": total_ratings}
    return restaurant_dict

def put_restaurant_dict_into_db(restaurant_dict):
    for restaurant in restaurant_dict:
        name = restaurant
        rating = restaurant_dict[restaurant].get("rating")
        total_rating = restaurant_dict[restaurant].get("total_ratings")
        input_google_maps_data_in_db(name, rating, total_rating)

def main():
    create_google_maps_db()
    data = get_googlemap_data(url, google_maps_api_key)
    put_restaurant_dict_into_db(data)

main()