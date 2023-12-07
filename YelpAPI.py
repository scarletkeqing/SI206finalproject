# Gather data from Yelp API
# Gather data from Yelp API
import requests
import sqlite3
import json 
import re 

yelp_searches = 'https://api.yelp.com/v3/businesses/search?location=Ann%20Arbor'
yelp_reviews = 'https://api.yelp.com/v3/businesses/{id}/reviews'

yelp_api = 'olWZg2mrP64E83paLsch77dR1jZLQ4jrMq271D_Kqt-gqf2qw1xlukFYMqVtK6s5TzKNqY-6lH7S1RWFeSjWt0cLdYSxkdK4UNCtK1lcEbOrO8rqDzO3oCBNv7RqZXYx'

YELP_DB = "Yelp.db"

# def save_address_to_db():

def create_yelp_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS YelpData (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rating REAL,
            address_id INTEGER, 
            reviews TEXT, 
            address TEXT)
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS YelpAddresses (
        id INTEGER PRIMARY KEY,
        street_name TEXT)
    """)

    conn.commit()
    conn.close()

def gather_yelp_data(keyword): 
    rows = 100 
    yelp_fetch_limit = 25 
    unique_name = set() 

    for offset in range(0, rows, yelp_fetch_limit): 
        parameter = {
            'term': keyword,
            'categories': 'restaurants',
            'limit': yelp_fetch_limit, 
            'offset': offset, 
            'api_key': yelp_api,
        }

        response = requests.get(yelp_searches, headers={'Authorization': f'Bearer {yelp_api}'}, params=parameter)
        data = response.json() 

        print(data)

        print(f"Offset: {offset}, Businesses received: {len(data.get('businesses'))}") 

        for restaurant in data.get('businesses'): 
            name = restaurant.get('name') 
            if name not in unique_name: 
                restaurant_id = restaurant.get('id')
                restaurant_address = restaurant.get('display_address')
                street_name = restaurant.get('display_address')

                if street_name: 
                    street = re.search('r\b(\w+?\sSt\b)', street_name[0])
                
                reviews_response = requests.get(yelp_reviews.format(id=restaurant_id), headers={'Authorization': f'Bearer {yelp_api}'})
                reviews_data = reviews_response.json()

                unique_name.add(name)
                save_data_to_db('yelp_data', restaurant, reviews_data.get('reviews'), restaurant_address)



def save_data_to_db(source, restaurant_data, reviews_data):
    conn = sqlite3.connect(YELP_DB)
    cur = conn.cursor()

    if source == 'yelp_data':
        name = restaurant_data.get('name')
        rating = restaurant_data.get('rating')
        restaurant_address = restaurant_data.get('display_address')
        reviews = []
        if reviews_data:
            for review in reviews_data:
                review_text = review.get('text')
                if review_text:
                    reviews.append(review_text)
            if name and rating:
                cur.execute('INSERT INTO YelpData (name, rating, reviews, restaurant_address) VALUES (?, ?, ?, ?)', (name, rating, json.dumps(reviews), restaurant_address))
                conn.commit()

    conn.close()

def main():
    create_yelp_db("Yelp.db")
    gather_yelp_data('restaurants')  # You can specify a different keyword here if needed

main()