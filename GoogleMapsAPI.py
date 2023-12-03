import json
import requests
import sqlite3

google_maps_api_key = "AIzaSyB_Qkf_TqHrHoFlzzBGgdW5DGaKxdFJnPA"
url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=food%20ann%20&key={google_maps_api_key}"

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

def get_googlemap_data(url):
    response = requests.get(url)
    data = response.json()
    print(data)
    for restaurant in data["results"]:
        name = restaurant.get("name")
        rating = restaurant.get("rating")
        total_ratings = restaurant.get("user_ratings_total")
        input_google_maps_data_in_db(name, rating, total_ratings)

def main():
    create_google_maps_db()
    get_googlemap_data(url)

main()