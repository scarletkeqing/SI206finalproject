# Names: Tiffany Tam, Kim Nguyen, Ke Qing Wong
# Uniqnames: itsteep@umich.edu, hkimngu@umich.edu, qscarlet@umich.edu



# # join tables 
# def save_data_to_BaoBuddies(cur, conn): 
#     cur.execute(
#         """
#         INSERT INTO FinalData (name, google_rating, total_ratings_google, opentable_num_bookings, yelp_rating, reviews)
#         SELECT 
#             GoogleMapsData.name, 
#             GoogleMapsData.rating, 
#             GoogleMapsData.total_ratings, 
#             Bookings.number_of_bookings, 
#             YelpData.rating, 
#             YelpData.reviews 

#         FROM GoogleMapsData 
#         JOIN Bookings ON GoogleMapsData .name = Bookings.restaurant_name 
#         JOIN YelpData ON GoogleMapsData .name = YelpData.name;
#         """
#     )

#     conn.commit() 

# # graphs/charts using plotly 

# # visualization 1: 
# # How many times a table has been booked vs ratings for the average of both (google and Yelp) 
# # Scatterplot 
# # Is there ​​any correlation between the booking frequency and the average ratings?

# def visualization_bookings_vs_ratings(cur, conn): 
#     cur.execute(
#         """
#         SELECT AVG((YelpData.rating + GoogleMapsData.rating) / 2) AS average_rating, Bookings.number_of_bookings
#         FROM GoogleMapsData 
#         JOIN Bookings ON GoogleMapsData.name = Bookings.restaurant_name
#         JOIN YelpData ON GoogleMapsData.name = YelpData.name 
#         GROUP BY GoogleMapsData.name 
#         """
#     )

#     res = cur.fetchall() 
#     avg_rating, bookings = zip(*res) 

#     fig = go.Figure(data=[go.Scatter(name="Average Rating vs Bookings", x=avg_rating, y=bookings, mode='markers', marker_color='rgb(55,83,109)')])

#     title_str = "Does rating affect number of bookings?" 

#     fig.show() 
#     conn.close() 

# # visualization 2: 
# # Word count vs. Yelp ratings



# # visualization 3: 
# # Average Ratings vs. Price range (num dollar signs)
# def visualization_rating_vs_price_range(db_name):
#     conn = sqlite3.connect(db_name)
#     cur = conn.cursor()

#     cur.execute(
#         """
#         SELECT GoogleMapsData.name, GoogleMapsData.rating, GoogleMapsData.price_range
#         FROM GoogleMapsData 
        
#         """
#     )
#     data = cur.fetchall()
#     rating_data = [row[1] for row in data]
#     price_range_data = [row[2] for row in data]

#     #plt.plot(price_range_data, rating_data)
#     #plt.xlabel("Price Range")
#     #plt.ylabel("Rating")
#     #plt.show()

# import requests
# import sqlite3
# import pandas as pd
# import plotly.graph_objects as go 

# # create final database
# def create_tables(final_db_name): 
#     conn = sqlite3.connect(final_db_name)
#     cur = conn.cursor() 

#     cur.execute( 
#         """
#         CREATE TABLE IF NOT EXISTS Yelp (
#             id INTEGER PRIMARY KEY,
#             name TEXT PRIMARY KEY, 
#             rating FLOAT 
#             address_id INTEGER PRIMARY KEY,  
#             reviews TEXT 
#             full_address TEXT PRIMARY KEY
#         )"""
#     )

#     cur.execute( 
#         """
#         CREATE TABLE IF NOT EXISTS Yelp Address ID (
#             address_id INTEGER PRIMARY KEY,
#             street_name TEXT PRIMARY KEY, 
#         )"""
#     )
    

#     cur.execute( 
#         """
#         CREATE TABLE IF NOT EXISTS Google Maps (
#             full_address TEXT PRIMARY KEY,
#             total_ratings FLOAT, 
#             average_rating FLOAT,
#             total_dollar_signs INTEGER,
#             average_dollar_signs INTEGER,
#             daily_bookings
#         )"""
#     )




#     conn.commit() 
#     conn.close() 


# #
import requests
import sqlite3
import pandas as pd
import plotly.graph_objects as go 
from OpentableBS import create_table, insert_into_table, get_daily_bookings
from GoogleMapsAPI import create_google_maps_table, get_ann_arbor_locations, get_googlemap_data, put_restaurant_dict_into_table
# from YelpAPI import create_yelp_db, gather_yelp_data

def create_db():
    conn = sqlite3.connect("BaoBuddies.db")
    cursor = conn.cursor()

    #put GoogleMaps data in database
    create_google_maps_table("SI206finalproject/BaoBuddies.db")
    locations = get_ann_arbor_locations()
    data = get_googlemap_data(locations)
    put_restaurant_dict_into_table(data, "SI206finalproject/BaoBuddies.db")

    #put Opentable data in database
    get_daily_bookings("SI206finalproject/BaoBuddies.db")

    #put Yelp data in database
    #create_yelp_db("SI206finalproject/BaoBuddies.db")
    #gather_yelp_data('restaurants')


    


    # create Yelp Address ID table
    cursor.execute( 
        """
        CREATE TABLE IF NOT EXISTS Yelp Address ID (
            address_id INTEGER PRIMARY KEY,
            street_name TEXT, 
        )"""
    )

    # create Yelp vs. Google Maps table
    cursor.execute( 
        """
        CREATE TABLE IF NOT EXISTS Yelp vs. Google Maps (
            full_address TEXT PRIMARY KEY,
            total_ratings FLOAT, 
            average_rating FLOAT,
            total_dollar_signs INTEGER,
            average_dollar_signs FLOAT,
            daily_bookings INTEGER
        )"""
    )      """"
    )

    # create Yelp vs. Google Maps vs. Opentable table
    cursor.execute( 
        """
        CREATE TABLE IF NOT EXISTS Yelp vs. Google Maps vs. Opentable (
            full_address TEXT PRIMARY KEY,
            total_ratings FLOAT, 
            average_rating FLOAT,
            total_dollar_signs INTEGER,
            average_dollar_signs FLOAT,
            daily_bookings INTEGER
        )"""
    )

    conn.commit()
    conn.close()

create_db()