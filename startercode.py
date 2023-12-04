# Names: Tiffany Tam, Kim Nguyen, Ke Qing Wong
# Uniqnames: itsteep@umich.edu, hkimngu@umich.edu, qscarlet@umich.edu

import requests
import sqlite3
import pandas as pd
# using plotly [will insert stuff later] 

# Gather data from Yelp API

# Gather data from Nutritionix API

# Gather data from Open Food Facts API

# create final database 
def create_final_database(): 
    conn = sqlite3.connect("BaoBuddies.db") 
    cur = conn.cursor() 

    cur.execute( 
        """
        CREATE TABLE IF NOT EXISTS FinalData (
            name TEXT PRIMARY KEY, 
            google_rating FLOAT 
            total_ratings_google INTEGER, 
            opentable_num_bookings INTEGER, 
            yelp_rating REAL, 
            reviews TEXT 
        )"""
    )
    conn.commit() 
    conn.close() 

# join tables 
def save_data_to_BaoBuddies(cur, conn): 
    cur.execute(
        """
        INSERT INTO FinalData (name, google_rating, total_ratings_google, opentable_num_bookings, yelp_rating, reviews)
        SELECT 
            GoogleMapsData.name, 
            GoogleMapsData.rating, 
            GoogleMapsData.total_ratings, 
            Bookings.number_of_bookings, 
            YelpData.rating, 
            YelpData.reviews 

        FROM GoogleMapsData 
        JOIN Bookings ON GoogleMapsData .name = Bookings.restaurant_name 
        JOIN YelpData ON GoogleMapsData .name = YelpData.name;
        """
    )

    conn.commit() 

# graphs/charts using plotly 

# visualization 1: 
# How many times a table has been booked vs ratings for the average of both (google and Yelp) 
# Scatterplot 
# Is there ​​any correlation between the booking frequency and the average ratings?

def visualization_bookings_vs_ratings(cur, conn): 
    cur.execute(
        """
        SELECT GoogleMapsData.name, GoogleMapsData.rating AS google_rating, Bookings.number_of_bookings
        FROM GoogleMapsData 
        JOIN Bookings ON GoogleMapsData.name = Bookings.restaurant_name
        """
    )



# visualization 2: 
# The number of ratings for each star (no rounding) 
# Bar chart (1 star, 2 stars, etc.) 
# Look at how many of each star there are in MI/AA


# visualization 3: 
# The number of words in each rating vs the number of stars (higher wording = more stars, vice versa?) 
# Box plot 
# Is there a correlation between the length of the review vs the number of stars? 
