from pymongo import MongoClient
import csv
import os
from dotenv import load_dotenv
load_dotenv()

password = os.environ['PASSWORD']
username = os.environ['USERNAME']
client = MongoClient("mongodb+srv://{username}:{password}@realestatecluster.kypuqxb.mongodb.net/?retryWrites=true&w=majority&appName=realEstateCluster")

db = client['listings']
collection = db['austin']  # Use 'db' to select the collection

csv_file = 'austinHousingData.csv'

try:
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)  # Read all rows into a list

    if rows:
        collection.insert_many(rows)  # Insert all rows at once

    if collection.count_documents({}) > 0:
        print('CSV imported successfully')
    else:
        print('Something went wrong')
except Exception as e:
    print(f"An error occurred: {e}")