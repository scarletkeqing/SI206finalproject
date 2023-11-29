# Gather data from Open Food Facts API
import requests
import sqlite3 
import pandas as pd 

def gather_open_food_data(barcode):
    open_food_url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}" # Input barcode to fetch data dynamically
    response = requests.get(open_food_url)
    data = response.json()
    save_data_to_db('open_food', [data.get('product', {})])

def save_data_to_db(source, data):
    conn = sqlite3.connect('fastfood.sqlite')
    cur = conn.cursor()

    if source == 'open_food':
        for product in data:
            product_name = product.get('product_name')
            ecoscore = product.get('ecoscore_grade')
            if product_name and ecoscore:  # we want both fields to be not None
                cur.execute('INSERT INTO OpenFood (product_name, ecoscore) VALUES (?, ?)', (product_name, ecoscore))

def main():
    barcodes = ['3017624010701', '737628064502'] # list of barcodes to be fetched
    for barcode in barcodes:
        gather_open_food_data(barcode)

main()