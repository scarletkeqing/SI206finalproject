import json
import requests
import sqlite3

google_maps_api_key = "AIzaSyCscZnjFAw0hMEEVNngPDU_iaufa_NX9_g"
url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=food+in+ann+arbor&key={google_maps_api_key}"

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

def get_foursquare_data(url):
    response = requests.get(url)
    data = response.json()
    for restaurant in data["results"]:
        name = restaurant.get("name")
        rating = restaurant.get("rating")
        total_ratings = restaurant.get("user_ratings_total")
        input_google_maps_data_in_db(name, rating, total_ratings)

def main():
    create_google_maps_db()
    get_foursquare_data(url)

main()


