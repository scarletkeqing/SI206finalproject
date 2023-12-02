# Gather data from Open Food Facts API
import json
import requests
import sqlite3 
import pandas as pd 

import os

DBNAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'OpenFoodFacts.db')

DBNAME = 'OpenFoodFacts.db'
    
def create_food_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # Creating food details' table
    create_foods_tbl = '''
        CREATE TABLE IF NOT EXISTS 'Foods' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'Brand' TEXT,
            'EcoScore' INTEGER
        );
    '''
    cur.execute(create_foods_tbl)

    conn.commit()
    conn.close()

def add_food_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    base_url = "https://world.openfoodfacts.org/api/v0/product/"
    
    # Sample product barcodes
    product_barcodes = ['3017620422003', '3502110009449', '87157215', '8000500037560']

    for barcode in product_barcodes:
        params = {'barcode': barcode}
        response = requests.get(base_url + barcode + '.json', params=params)
        result = response.json()
        
        if 'product' in result:
            product = result['product']
            name = product['product_name'] if 'product_name' in product else "No Data"
            brand = product['brands'] if 'brands' in product else "No Data"
            eco_score = product['ecoscore_grade'] if 'ecoscore_grade' in product else "No Data"

            insertion = (None,name,brand,eco_score)

            statement = 'INSERT INTO "Foods"'
            statement += 'VALUES (?,?,?,?)'
            cur.execute(statement, insertion)

    conn.commit()
    conn.close()

def get_food_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = "SELECT Name, Brand, EcoScore FROM Foods"
    cur.execute(statement)

    data = cur.fetchall()
    
    return data

# Creating DB & Tables
def main():
    create_food_db()

# Populating tables with data from openfoodfacts API
    add_food_data() 

# Retrieveing and printing data from the table
    get_food_data()

main()





