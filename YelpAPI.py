# Gather data from Yelp API
# Gather data from Yelp API
import requests
import sqlite3
import json 
import re 

yelp_searches = 'https://api.yelp.com/v3/businesses/search?location=Ann%20Arbor'
yelp_reviews = 'https://api.yelp.com/v3/businesses/{id}/reviews'

# yelp_api = 'olWZg2mrP64E83paLsch77dR1jZLQ4jrMq271D_Kqt-gqf2qw1xlukFYMqVtK6s5TzKNqY-6lH7S1RWFeSjWt0cLdYSxkdK4UNCtK1lcEbOrO8rqDzO3oCBNv7RqZXYx' 

# yelp_api = 'nHn_p-LmYCONwOJaIlX6Ifi0sSl8i3OiH0gu0L95TEBwCa-4CwBgPN_4avbwgDwEFq82yNCT1jhMJFvcrFy0M3IFdqkVR__yu3Y7ShRSY-DZin0dbnMleSL0QK5yZXYx' 

yelp_api = 'VBFj65-f5ZWK1StnqUsw0Rm0l71hXlPvWNAk-m8NnFpBCoCJOHlmgLqgsv9-yUj6iNmnTz1xEgE1ohT91t8vrltYiW_BOGaux_2sxrOK1iYcuDgEEkqbc6kZZUdzZXYx' 


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
            number TEXT 
            )
    """)

    # cur.execute("""
    # CREATE TABLE IF NOT EXISTS YelpAddresses (
    #     id INTEGER PRIMARY KEY,
    #     street_name TEXT)
    # """)

    conn.commit()
    cur.close()

def gather_yelp_data(keyword, conn, cur): 
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
                restaurant_address = restaurant.get('location').get('display_address')[0]
                if restaurant.get('display_phone'): 
                    restaurant_number = restaurant.get('display_phone')
                # street_name = restaurant.get('location').get('address1')
                print(restaurant_address)
                print(restaurant.get('location')) 
                print(restaurant_number)
                # print(restaurant_id)

                # if street_name: 
                #     street = re.search('\d+\s+(?:[NSEW]\s*)?(.*?)\s', street_name) 
                #     if street: 
                #         street_result = street.group(1) 
                #         print(street_result)
                #         cur.execute('INSERT INTO YelpAddresses (id, street_name) VALUES (?, ?)', (num_id, street_result))
                #         num_id += 1 

                reviews_response = requests.get(yelp_reviews.format(id=restaurant_id), headers={'Authorization': f'Bearer {yelp_api}'})
                reviews_data = reviews_response.json()

                unique_name.add(name)
                save_data_to_db('yelp_data', restaurant, reviews_data.get('reviews'), restaurant_address, restaurant_number)

    conn.commit()
    cur.close() 

def save_data_to_db(source, restaurant_data, reviews_data, restaurant_address, restaurant_number):
    conn = sqlite3.connect(YELP_DB)
    cur = conn.cursor()
    address_id = 0 
    if source == 'yelp_data':
        name = restaurant_data.get('name')
        rating = restaurant_data.get('rating')
        restaurant_address = restaurant_data.get('location').get('display_address')[0]
        restaurant_number = restaurant_data.get('display_phone')
        reviews = []
        if reviews_data:
            for review in reviews_data:
                review_text = review.get('text')
                if review_text:
                    reviews.append(review_text)

            if name and rating:
                address_id += 1
                cur.execute('INSERT OR IGNORE INTO YelpData (name, rating, reviews, restaurant_address, number) VALUES (?, ?, ?, ?, ?)', (name, rating, json.dumps(reviews), restaurant_address, restaurant_number))

                conn.commit()
                conn.close()

def main(): 
    conn = sqlite3.connect(YELP_DB) 
    cur = conn.cursor()
    create_yelp_db("Yelp.db")
    gather_yelp_data('restaurants', conn, cur)  # You can specify a different keyword here if needed
    conn.commit() 
    cur.close() 
main()