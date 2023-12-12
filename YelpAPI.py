# Gather data from Yelp API

import requests
import sqlite3
import json 
import re 

yelp_searches = 'https://api.yelp.com/v3/businesses/search?location=Ann%20Arbor'
yelp_reviews = 'https://api.yelp.com/v3/businesses/{id}/reviews'

# Many APIs because Yelp only allows us a client is limited to 500 API calls per 24 hours

# yelp_api = 'olWZg2mrP64E83paLsch77dR1jZLQ4jrMq271D_Kqt-gqf2qw1xlukFYMqVtK6s5TzKNqY-6lH7S1RWFeSjWt0cLdYSxkdK4UNCtK1lcEbOrO8rqDzO3oCBNv7RqZXYx' 

yelp_api = 'nHn_p-LmYCONwOJaIlX6Ifi0sSl8i3OiH0gu0L95TEBwCa-4CwBgPN_4avbwgDwEFq82yNCT1jhMJFvcrFy0M3IFdqkVR__yu3Y7ShRSY-DZin0dbnMleSL0QK5yZXYx' 

# yelp_api = 'VBFj65-f5ZWK1StnqUsw0Rm0l71hXlPvWNAk-m8NnFpBCoCJOHlmgLqgsv9-yUj6iNmnTz1xEgE1ohT91t8vrltYiW_BOGaux_2sxrOK1iYcuDgEEkqbc6kZZUdzZXYx' 

# yelp_api = 'YnYkRVaOVxPm4OK0ZfrhuHX9KY3OlmkddtXUd0LVdy9yrUzbGVx3joEHUMN5dfdzfSngxiyGnpvGSB3A3Usd4YMSB-Ly5ayu1mZg9tK4n3Nz_VyDv2zpHGodzG53ZXYx' 

# kim # 1 
# yelp_api = '7mMOTu9IugW2-TPOvZXTjr987BrwTi8JVJK8fITuP1N0_nUcTr_gdHfXOkMtSgs55MRjfiLHg0nibRE7PgCKYPRPsXuTyBskRYV0PRXbRKMMSHnrlmuD-5OrmHp3ZXYx'

# kim # 2 
# yelp_api = 'Si8jAzR_Sf0XScGPD4LNxryrSm3na3exz_TQ-fTSYa9S0DxyVeG86hs9TWe5EMvraT6s32VWN6dGgHFelvscZW-1i7IB6ihsD8-2_kNCmjit28BC8_FfyIDRIYN3ZXYx'

# scarlet # 1 
# yelp_api = 'Twi7MjnUNzHCdbpUkUdRoQ0_rY3ZAbogSM0pU9099DGFyWJyDu1APWpNELU3-aoTt6wtNXQUUoFCf4Fo4kywrgZDh8HetB_hWhLbzL4EF8UKixhX0sGikIR7_oJ3ZXYx'

YELP_DB = "Yelp.db"

# create yelp data table 
def create_yelp_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS YelpData (
            id INTEGER PRIMARY KEY, 
            name TEXT,
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
    # get a max of 125 restaurants total 
    rows = 200 
    # get 25 restaurants in each API call 
    yelp_fetch_limit = 25
    yelp_dict = {}
    cur_id = 0
    break_outer_loop = False

    # gets the names of already fetched restaurants
    cur.execute('SELECT name FROM YelpData')
    fetched_names = set(row[0] for row in cur.fetchall())

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
            if name not in fetched_names:
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
                    fetched_names.add(name)

                    yelp_dict[cur_id] = {
                        'name': name,
                        'rating': restaurant.get('rating'),
                        'reviews': json.dumps(reviews),
                        'restaurant_address': restaurant_address,
                        'number': restaurant_number,
                        'word_count': word_count
                    }

                    cur_id += 1
                    if cur_id == 25:
                        break_outer_loop = True
                        break

        if break_outer_loop:
            break

    # save the fetched data to the database 
    for record_id, record in yelp_dict.items():
        save_data_to_db(db_name, 'yelp_data', record)

    conn.commit()
    cur.close() 

def save_data_to_db(db_name, source, restaurant_data):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor() 

    if source == 'yelp_data':
        name = restaurant_data.get('name')
        rating = restaurant_data.get('rating')

        cur.execute('INSERT OR IGNORE INTO YelpData (name, rating, reviews, restaurant_address, number, word_count) VALUES (?, ?, ?, ?, ?, ?)', (name, rating, restaurant_data.get('reviews'), restaurant_data.get('restaurant_address'), restaurant_data.get('number'), restaurant_data.get('word_count'))) 

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
