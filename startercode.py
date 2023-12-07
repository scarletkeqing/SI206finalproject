# Names: Tiffany Tam, Kim Nguyen, Ke Qing Wong
# Uniqnames: itsteep@umich.edu, hkimngu@umich.edu, qscarlet@umich.edu

import requests
import sqlite3
import pandas as pd
import plotly.graph_objects as go 

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
        SELECT AVG((YelpData.rating + GoogleMapsData.rating) / 2) AS average_rating, Bookings.number_of_bookings
        FROM GoogleMapsData 
        JOIN Bookings ON GoogleMapsData.name = Bookings.restaurant_name
        JOIN YelpData ON GoogleMapsData.name = YelpData.name 
        GROUP BY GoogleMapsData.name 
        """
    )

    res = cur.fetchall() 
    avg_rating, bookings = zip(*res) 

    fig = go.Figure(data=[go.Scatter(name="Average Rating vs Bookings", x=avg_rating, y=bookings, mode='markers', marker_color='rgb(55,83,109)')])

    title_str = "Does rating affect number of bookings?" 

    fig.show() 
    conn.close() 

# visualization 2: 
# Word count vs. Yelp ratings



# visualization 3: 
# Average Ratings vs. Price range (num dollar signs)
def visualization_rating_vs_price_range():
    conn = sqlite3.connect("GoogleMaps.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT GoogleMapsData.name, GoogleMapsData.rating, GoogleMapsData.price_range
        FROM GoogleMapsData 
        
        """
    )
    data = cur.fetchall()
    rating_data = [row[1] for row in data]
    price_range_data = [row[2] for row in data]

    #plt.plot(price_range_data, rating_data)
    #plt.xlabel("Price Range")
    #plt.ylabel("Rating")
    #plt.show()