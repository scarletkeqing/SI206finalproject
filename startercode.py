# Names: Tiffany Tam, Kim Nguyen, Ke Qing Wong
# Uniqnames: itsteep@umich.edu, hkimngu@umich.edu, qscarlet@umich.edu

from OpentableBS import get_daily_bookings
from GoogleMapsAPI import read_dict_from_file, get_ann_arbor_locations, get_googlemap_data, get_street_dict, create_street_id_table, create_google_maps_table, insert_into_street_id_table, insert_into_google_maps_table
from YelpAPI import create_yelp_db, gather_yelp_data
import requests
import sqlite3
import pandas as pd
import os 
import plotly.graph_objects as go 

def create_db():
    conn = sqlite3.connect("BaoBuddies.db")
    cursor = conn.cursor()

    #put GoogleMaps data in database
    if os.path.exists("googlemaps_api_data.txt"):
        data = read_dict_from_file("googlemaps_api_data.txt")
    else:
        locations = get_ann_arbor_locations()
        data = get_googlemap_data(locations)

    street_data = get_street_dict(data)
    create_street_id_table("BaoBuddies.db")
    create_google_maps_table("BaoBuddies.db")
    insert_into_street_id_table(street_data, "BaoBuddies.db")
    insert_into_google_maps_table(data, "BaoBuddies.db")

    #put Opentable data in database
    get_daily_bookings("BaoBuddies.db")

    #put Yelp data in database
    create_yelp_db("BaoBuddies.db")
    gather_yelp_data('restaurants', conn, cursor, "BaoBuddies.db")
    
    
def visualization_googlemaps_vs_streetid(cur, conn):
    #put GoogleMaps and StreetID in table
    cursor.execute( 
        """
        CREATE TABLE IF NOT EXISTS GoogleMapsData_VS_StreetID (
            street TEXT PRIMARY KEY,
            number_of_restaurants INT
        )"""
    )
    cursor.execute( 
        """
        SELECT name, street FROM GoogleMapsData JOIN StreetID
        ON GoogleMapsData.street_id = StreetID.id
        """
    )
    street_count_dict = {}
    for row in cursor:
        if row[1] not in street_count_dict:
            street_count_dict[row[1]] = 1
        else:
            street_count_dict[row[1]] += 1
    for street in street_count_dict:
        cursor.execute( 
            """
            INSERT OR IGNORE INTO GoogleMapsData_VS_StreetID (street, number_of_restaurants)
            VALUES (?, ?)
            """,
            (street, street_count_dict[street])
        )
    conn.commit()
    
    try:
        cur.execute(
            """
            SELECT street, number_of_restaurants
            FROM GoogleMapsData_VS_StreetID 
            ORDER BY number_of_restaurants 
            """
        )
        result = cur.fetchall()
        if not result:
            print("No data found.")
            return
        
        labels_list = []
        values_list = []

        for i in range(6):
            labels_list.append(result[i][0])
            values_list.append(result[i][0])

        fig = go.Figure(data=[go.Pie(labels=labels_list, values=values_list, color_discrete_sequence=["red", "orange", "yellow", "green", "blue", "purple"])])

        title_str = "Streets with the Most Restaurants"
        fig.update_layout(title=title_str)

        fig.show()

        # Save the figure
        fig.write_html("streets_with_the_most_restaurants.html")  # Save as interactive HTML
        fig.write_image("streets_with_the_most_restaurants.png")  # Save as static image (PNG)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.commit() 

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
            INSERT INTO RatingNumBookings 
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


def visualization_yelp_ratings_vs_num_bookings(cur, conn): 
    try:
        cur.execute(
            """
            SELECT yelp_rating, opentable_bookings
            FROM RatingNumBookings 
            """
        )
        res = cur.fetchall()
        if not res:
            print("No data found.")
            return

        yelp_rating, opentable_bookings = zip(*res) 

        fig = go.Figure() 

        fig.add_trace(go.Scatter(x=yelp_rating, y=opentable_bookings, mode='markers', name='Yelp Ratings', marker=dict(size = 12)))

        title_str = "Yelp Ratings vs Number of Bookings"
        fig.update_layout(title=title_str, xaxis_title="Yelp Rating", yaxis_title="Number of Bookings")

        fig.show()

        # Save the figure
        fig.write_html("yelp_ratings_vs_num_bookings.html")  # Save as interactive HTML
        fig.write_image("yelp_ratings_vs_num_bookings.png")  # Save as static image (PNG)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.commit() 

# create Yelp vs. Google Maps table
# cursor.execute( 
#     """
#     CREATE TABLE IF NOT EXISTS YelpVSGoogleMaps (
#         phone_num TEXT PRIMARY KEY,
#         total_ratings FLOAT, 
#         average_rating FLOAT,
#         total_dollar_signs INTEGER,
#         average_dollar_signs FLOAT
#     )"""
# )    
# cursor.execute(
#     '''SELECT name, rating, price_range FROM YelpData JOIN GoogleMapsData
#     ON YelpData.number = GoogleMapsData.phone_num
#     '''
# )
# for row in cursor:
#     print(row)

#     # create Yelp vs. Google Maps vs. Opentable table
#     cursor.execute( 
#         """
#         CREATE TABLE IF NOT EXISTS YelpVSGoogleMapsVSOpentable (
#             full_address TEXT PRIMARY KEY,
#             total_ratings FLOAT, 
#             average_rating FLOAT,
#             total_dollar_signs INTEGER,
#             average_dollar_signs FLOAT,
#             daily_bookings INTEGER
#         )"""
#     )

#     conn.commit()
#     conn.close() 

def calculate_rating_frequencies(cur, table_name, rating_column):
    rating_ranges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    frequencies = []

    for lower, upper in rating_ranges:
        query = f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE {rating_column} >= ? AND {rating_column} < ?
        """
        cur.execute(query, (lower, upper))
        count = cur.fetchone()[0]
        frequencies.append(count)

    return frequencies

def visualization_rating_frequencies(cur, conn):
    yelp_freq = calculate_rating_frequencies(cur, "YelpData", "rating")
    google_maps_freq = calculate_rating_frequencies(cur, "GoogleMapsData", "rating")

    rating_labels = ["0-1", "1-2", "2-3", "3-4", "4-5"]

    fig = go.Figure(data=[
        go.Bar(name='Yelp', x=rating_labels, y=yelp_freq),
        go.Bar(name='Google Maps', x=rating_labels, y=google_maps_freq)
    ])

    # Change the bar mode
    fig.update_layout(barmode='group', title="Rating Frequencies in Yelp and Google Maps",
                      xaxis_title="Rating Range", yaxis_title="Frequency")

    fig.show()

    # Optionally save the figure
    fig.write_html("rating_frequencies.html")
    fig.write_image("rating_frequencies.png")



def visualization_yelp_ratings_vs_word_count(cur, conn):
    try:
        cur.execute(
            """
            SELECT rating, word_count 
            FROM YelpData 
            WHERE word_count IS NOT NULL 
            """
        )
        res = cur.fetchall()
        if not res:
            print("No data found.")
            return

        ratings, word_counts = zip(*res)

        fig = go.Figure(data=[go.Scatter(name="Yelp Ratings vs. Word Count", x=ratings, y=word_counts, mode='markers', marker_color='rgb(55,83,109)')])

        title_str = "Yelp Ratings vs. Word Count"
        fig.update_layout(title=title_str, xaxis_title="Yelp Ratings", yaxis_title="Word Count")

        fig.show()

        # Save the figure
        fig.write_html("yelp_ratings_vs_word_count.html")  # Save as interactive HTML
        fig.write_image("yelp_ratings_vs_word_count.png")  # Save as static image (PNG)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.commit() 

conn = sqlite3.connect("BaoBuddies.db")
cursor = conn.cursor()
create_db()
#visualization_yelp_ratings_vs_word_count(cursor, conn)
#visualization_googlemaps_vs_streetid(cursor, conn) 
# visualization_average_ratings_vs_num_bookings(cursor, conn) 
# create_ratings_and_num_bookings_table(cursor, conn) 
# visualization_yelp_ratings_vs_num_bookings(cursor, conn)
visualization_rating_frequencies(cursor, conn)
conn.close()