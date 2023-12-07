import os
from bs4 import BeautifulSoup

def get_daily_bookings():
    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, "third_page.html")

    list = []

    with open(full_path, "r", encoding="utf-8-sig") as fp:
        listing_page_html = fp.read()
        soup = BeautifulSoup(listing_page_html, "html.parser")
        restaurant_names = soup.find_all("h6", class_="tfljo0SQq0JS3FOxpvxL")   
        for name in restaurant_names:
            names = (name.get_text())
            list.append(names)
        print(list)

get_daily_bookings()
