# Gather data from Yelp API
# Gather data from Yelp API
import requests
import sqlite3
import json

yelp_searches = 'https://api.yelp.com/v3/businesses/search?location=Ann%20Arbor'
yelp_reviews = 'https://api.yelp.com/v3/businesses/{id}/reviews'

yelp_api = 'olWZg2mrP64E83paLsch77dR1jZLQ4jrMq271D_Kqt-gqf2qw1xlukFYMqVtK6s5TzKNqY-6lH7S1RWFeSjWt0cLdYSxkdK4UNCtK1lcEbOrO8rqDzO3oCBNv7RqZXYx'

YELP_DB = "Yelp.db"

def create_yelp_db():
    conn = sqlite3.connect(YELP_DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS YelpData (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rating REAL,
            reviews TEXT)
    """)
    conn.commit()
    conn.close()

def gather_yelp_data(keyword):
    parameter = {
        'term': keyword,
        'categories': 'restaurants',
        'limit': 50,
        'api_key': yelp_api,
    }

    response = requests.get(yelp_searches, headers={'Authorization': f'Bearer {yelp_api}'}, params=parameter)
    data = response.json()

    for restaurant in data.get('businesses', []):
        restaurant_id = restaurant.get('id')
        reviews_response = requests.get(yelp_reviews.format(id=restaurant_id), headers={'Authorization': f'Bearer {yelp_api}'})
        reviews_data = reviews_response.json()

        save_data_to_db('yelp_data', restaurant, reviews_data.get('reviews', []))

def save_data_to_db(source, restaurant_data, reviews_data):
    conn = sqlite3.connect(YELP_DB)
    cur = conn.cursor()

    if source == 'yelp_data':
        name = restaurant_data.get('name')
        rating = restaurant_data.get('rating')
        reviews = []
        for review in reviews_data:
            review_text = review.get('text')
            if review_text:
                reviews.append(review_text)
        if name and rating:
            cur.execute('INSERT INTO YelpData (name, rating, reviews) VALUES (?, ?, ?)', (name, rating, json.dumps(reviews)))
            conn.commit()

    conn.close()

def main():
    create_yelp_db()
    gather_yelp_data('restaurants')  # You can specify a different keyword here if needed

main()