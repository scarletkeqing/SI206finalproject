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
        "downtown": {"lat": "42.2807", "long": "-83.7463"},
        "central_campus":{"lat": "42.2766", "long": "-83.7426"},
        "north_campus": {"lat": "39.2184", "long": "-84.5508"},
        "kerrytown": {"lat": "42.2862", "long": "-83.7451"},
        "burns_park": {"lat": "42.2657", "long": "-83.7350"},
        "old_west_side": {"lat": "42.27518", "long": "-83.75667"},
        "northside": {"lat": "42.2981", "long": "83.7321"}
    }
    restaurant_dict = {}

    for area in ann_arbor_locations:
        lat = ann_arbor_locations.get(area)["lat"]
        long = ann_arbor_locations.get(area)["long"]
        parameters = {
            'location': f"{lat},{long}",
            'radius' : '500',
            'type': 'restaurant',
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
    print(len(restaurant_dict))

def main():
    create_google_maps_db()
    get_googlemap_data(url, google_maps_api_key)

main()