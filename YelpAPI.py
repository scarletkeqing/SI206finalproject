# Gather data from Yelp API

import requests
import sqlite3
import json 
import re 

yelp_searches = 'https://api.yelp.com/v3/businesses/search?location=Ann%20Arbor'
yelp_reviews = 'https://api.yelp.com/v3/businesses/{id}/reviews'

yelp_api = 'olWZg2mrP64E83paLsch77dR1jZLQ4jrMq271D_Kqt-gqf2qw1xlukFYMqVtK6s5TzKNqY-6lH7S1RWFeSjWt0cLdYSxkdK4UNCtK1lcEbOrO8rqDzO3oCBNv7RqZXYx' 

# yelp_api = 'nHn_p-LmYCONwOJaIlX6Ifi0sSl8i3OiH0gu0L95TEBwCa-4CwBgPN_4avbwgDwEFq82yNCT1jhMJFvcrFy0M3IFdqkVR__yu3Y7ShRSY-DZin0dbnMleSL0QK5yZXYx' 

# yelp_api = 'VBFj65-f5ZWK1StnqUsw0Rm0l71hXlPvWNAk-m8NnFpBCoCJOHlmgLqgsv9-yUj6iNmnTz1xEgE1ohT91t8vrltYiW_BOGaux_2sxrOK1iYcuDgEEkqbc6kZZUdzZXYx' 


YELP_DB = "Yelp.db"

# create yelp data table 
def create_yelp_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS YelpData (
            name TEXT PRIMARY KEY,
            rating REAL, 
            reviews TEXT, 
            restaurant_address TEXT, 
            number TEXT,
            word_count INTEGER 
        )
    """)
    conn.commit()
    cur.close()

def gather_yelp_data(keyword, conn, cur, db_name): 
    rows = 125 
    yelp_fetch_limit = 25 
    unique_name = set() 

    for offset in range(0, rows, yelp_fetch_limit): 
        parameter = {
            'term': keyword,
            'categories': 'restaurants',
            'limit': yelp_fetch_limit, 
            'offset': offset
        }

        response = requests.get(yelp_searches, headers={'Authorization': f'Bearer {yelp_api}'}, params=parameter)
        data = response.json() 

        for restaurant in data.get('businesses', []): 
            name = restaurant.get('name') 
            if name not in unique_name: 
                restaurant_id = restaurant.get('id')
                restaurant_address = restaurant.get('location').get('display_address')[0]
                restaurant_number = restaurant.get('display_phone') if restaurant.get('display_phone') else ''

                reviews_response = requests.get(yelp_reviews.format(id=restaurant_id), headers={'Authorization': f'Bearer {yelp_api}'})
                reviews_data = reviews_response.json()

                word_count = 0
                reviews = []
                for review in reviews_data.get('reviews', []):
                    review_text = review.get('text')
                    if review_text:
                        reviews.append(review_text) 
                        word_count += len(re.findall(r'\w+', review_text))

                if name and restaurant.get('rating'):
                    unique_name.add(name)
                    save_data_to_db(db_name,'yelp_data', restaurant, reviews, restaurant_address, restaurant_number, word_count)

    conn.commit()
    cur.close() 

def save_data_to_db(db_name, source, restaurant_data, reviews, restaurant_address, restaurant_number, word_count):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    if source == 'yelp_data':
        name = restaurant_data.get('name')
        rating = restaurant_data.get('rating')

        cur.execute('INSERT OR IGNORE INTO YelpData (name, rating, reviews, restaurant_address, number, word_count) VALUES (?, ?, ?, ?, ?, ?)', (name, rating, json.dumps(reviews), restaurant_address, restaurant_number, word_count))

    conn.commit()
    conn.close()

def main(): 
    conn = sqlite3.connect(YELP_DB) 
    cur = conn.cursor()
    create_yelp_db(YELP_DB)
    gather_yelp_data('restaurants', conn, cur, YELP_DB)
    cur.close() 
    conn.close()

if __name__ == "__main__":
    main()