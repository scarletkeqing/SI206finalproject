import json
import sqlite3
import plotly.graph_objects as go 

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

        fig.write_html("yelp_ratings_vs_word_count.html")  
        fig.write_image("yelp_ratings_vs_word_count.png")

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

        fig.write_html("yelp_ratings_vs_num_bookings.html")  
        fig.write_image("yelp_ratings_vs_num_bookings.png") 

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.commit()  

def calculate_num_restarants_in_street(cur):
    cur.execute( 
        """
        SELECT name, street FROM GoogleMapsData JOIN StreetID
        ON GoogleMapsData.street_id = StreetID.id
        """
    )
    street_count_dict = {}
    for row in cur:
        if row[1] not in street_count_dict:
            street_count_dict[row[1]] = 1
        else:
            street_count_dict[row[1]] += 1
    
    sorted_results = dict(sorted(street_count_dict.items(), key=lambda x:x[1], reverse=True))
    return sorted_results

def visualization_googlemaps_vs_streetid(cur):
    sorted_results = calculate_num_restarants_in_street(cur)

    labels_list = []
    values_list = []

    count = 0
    for street in sorted_results:
        if count == 6:
            break
        labels_list.append(street)
        values_list.append(sorted_results[street])
        count += 1
        

    fig = go.Figure(data=[go.Pie(labels=labels_list, values=values_list, hole=.3)])

    title_str = "Streets with the Most Restaurants"
    fig.update_layout(title=title_str)

    fig.show()

    # Save the figure
    fig.write_html("streets_with_the_most_restaurants.html")  # Save as interactive HTML
    fig.write_image("streets_with_the_most_restaurants.png")  # Save as static image (PNG)

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

def visualization_rating_frequencies(cur):
    yelp_freq = calculate_rating_frequencies(cur, "YelpData", "rating")
    google_maps_freq = calculate_rating_frequencies(cur, "GoogleMapsData", "rating")

    rating_labels = ["0-1", "1-2", "2-3", "3-4", "4-5"]

    fig = go.Figure(data=[
        go.Bar(name='Yelp', x=rating_labels, y=yelp_freq),
        go.Bar(name='Google Maps', x=rating_labels, y=google_maps_freq)
    ])

    fig.update_layout(barmode='group', title="Rating Frequencies in Yelp and Google Maps",
                      xaxis_title="Rating Range", yaxis_title="Frequency")

    fig.show()

    fig.write_html("rating_frequencies.html")
    fig.write_image("rating_frequencies.png")


def create_json_file(cur):
    restaurant_freq = calculate_num_restarants_in_street(cur)
    yelp_freq = calculate_rating_frequencies(cur, "YelpData", "rating")
    google_maps_freq = calculate_rating_frequencies(cur, "GoogleMapsData", "rating")

    rating_labels = ["0-1", "1-2", "2-3", "3-4", "4-5"]
    rating_data = {
        "Yelp": dict(zip(rating_labels, yelp_freq)),
        "Google Maps": dict(zip(rating_labels, google_maps_freq))
    }

    json_data = {"rating_frequencies": rating_data,
                 "streets_with_most_restaurants": restaurant_freq}
    
    # Write to JSON file
    with open("calculations.json", 'w') as file:
        json.dump(json_data, file, indent=4)


conn = sqlite3.connect("BaoBuddies.db")
cur = conn.cursor()

# Create the JSON file
create_json_file(cur)

# Visualizations
visualization_yelp_ratings_vs_word_count(cur, conn)
visualization_googlemaps_vs_streetid(cur) 
visualization_yelp_ratings_vs_num_bookings(cur, conn)
visualization_rating_frequencies(cur)

# Close the database connection
conn.close()
