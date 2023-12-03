import json
import requests
import sqlite3

def create_zomato_db():
    conn = sqlite3.connect("Zomato.db")
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXIST ZomatoData
        (id INT PRIMARY KEY,
        name TEXT,
        rating FLOAT)'''
    )
    conn.commit()
    conn.close()

#def get_zomato_data():

#def input_zomato_data_in_db():
