# Names: Tiffany Tam, Kim Nguyen, Ke Qing Wong
# Uniqnames: itsteep@umich.edu, hkimngu@umich.edu, qscarlet@umich.edu

from OpentableBS import get_daily_bookings, insert_into_table
from GoogleMapsAPI import read_dict_from_file, get_ann_arbor_locations, get_googlemap_data, get_street_dict, create_street_id_table, create_google_maps_table, insert_into_street_id_table, insert_into_google_maps_table
from YelpAPI import create_yelp_db, gather_yelp_data
import requests
import sqlite3
import pandas as pd
import os 

def create_db():
    conn = sqlite3.connect("BaoBuddies.db")
    cursor = conn.cursor()

    #put GoogleMaps data in database
    if os.path.exists("googlemaps_api_data.txt"):
        data = read_dict_from_file("googlemaps_api_data.txt")
    else:
        locations = get_ann_arbor_locations()
        get_googlemap_data(locations)
        data = read_dict_from_file("googlemaps_api_data.txt")

    street_data = get_street_dict(data)
    create_street_id_table("BaoBuddies.db")
    create_google_maps_table("BaoBuddies.db")
    insert_into_street_id_table(street_data, "BaoBuddies.db")
    insert_into_google_maps_table(data, "BaoBuddies.db")

    #put Opentable data in database
    get_daily_bookings("BaoBuddies.db")
    insert_into_table(cursor, conn, get_daily_bookings("BaoBuddies.db"))
    
    #put Yelp data in database
    create_yelp_db("BaoBuddies.db")
    gather_yelp_data('restaurants', conn, cursor, "BaoBuddies.db")

def create_ratings_and_num_bookings_table(cur, conn): 
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS RatingNumBookings (
                phone_number TEXT PRIMARY KEY, 
                yelp_name TEXT, 
                yelp_rating FLOAT, 
                opentable_bookings INTEGER
            )
        """) 

        cur.execute(
            """
            INSERT OR IGNORE INTO RatingNumBookings 
                (phone_number, yelp_name, yelp_rating, opentable_bookings) 
            SELECT 
                COALESCE(YelpData.number, OpenTable.phone_number) AS phone_number, 
                YelpData.name AS yelp_name, 
                AVG(YelpData.rating) AS yelp_rating, 
                SUM(OpenTable.number_of_bookings) AS opentable_num_bookings 
            FROM YelpData 
            LEFT JOIN OpenTable ON YelpData.number = OpenTable.phone_number 
            GROUP BY YelpData.number
            HAVING AVG(YelpData.rating) IS NOT NULL AND 
                   SUM(OpenTable.number_of_bookings) IS NOT NULL
            """
        )

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.commit() 

conn = sqlite3.connect("BaoBuddies.db")
cursor = conn.cursor()

# Create database tables
create_db()
create_ratings_and_num_bookings_table(cursor, conn) 

conn.commit()
conn.close()