from pymongo import MongoClient
import csv
import os
from dotenv import load_dotenv
load_dotenv()

password = os.environ['PASSWORD']
username = os.environ['USERNAME']
client = MongoClient(f"mongodb+srv://{username}:{password}@realestatecluster.kypuqxb.mongodb.net/?retryWrites=true&w=majority&appName=realEstateCluster")

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


collection.aggregate([
    {
        '$set': {
            'latitude': {'$convert': {'input': '$latitude', 'to': 'double', 'onError': None}},
            'longitude': {'$convert': {'input': '$longitude', 'to': 'double', 'onError': None}},
            'propertyTaxRate': {'$convert': {'input': '$propertyTaxRate', 'to': 'double', 'onError': None}},
            'latestPrice': {'$convert': {'input': '$latestPrice', 'to': 'double', 'onError': None}},
            'lotSizeSqFt': {'$convert': {'input': '$lotSizeSqFt', 'to': 'double', 'onError': None}},
            'livingAreaSqFt': {'$convert': {'input': '$livingAreaSqFt', 'to': 'double', 'onError': None}},
            'avgSchoolDistance': {'$convert': {'input': '$avgSchoolDistance', 'to': 'double', 'onError': None}},
            'avgSchoolRating': {'$convert': {'input': '$avgSchoolRating', 'to': 'double', 'onError': None}},
            'garageSpaces': {'$convert': {'input': '$garageSpaces', 'to': 'int', 'onError': None}},
            'parkingSpaces': {'$convert': {'input': '$parkingSpaces', 'to': 'int', 'onError': None}},
            'yearBuilt': {'$convert': {'input': '$yearBuilt', 'to': 'int', 'onError': None}},
            'numPriceChanges': {'$convert': {'input': '$numPriceChanges', 'to': 'int', 'onError': None}},
            'latest_salemonth': {'$convert': {'input': '$latest_salemonth', 'to': 'int', 'onError': None}},
            'latest_saleyear': {'$convert': {'input': '$latest_saleyear', 'to': 'int', 'onError': None}},
            'numOfPhotos': {'$convert': {'input': '$numOfPhotos', 'to': 'int', 'onError': None}},
            'numOfAccessibilityFeatures': {'$convert': {'input': '$numOfAccessibilityFeatures', 'to': 'int', 'onError': None}},
            'numOfAppliances': {'$convert': {'input': '$numOfAppliances', 'to': 'int', 'onError': None}},
            'numOfParkingFeatures': {'$convert': {'input': '$numOfParkingFeatures', 'to': 'int', 'onError': None}},
            'numOfPatioAndPorchFeatures': {'$convert': {'input': '$numOfPatioAndPorchFeatures', 'to': 'int', 'onError': None}},
            'numOfSecurityFeatures': {'$convert': {'input': '$numOfSecurityFeatures', 'to': 'int', 'onError': None}},
            'numOfWaterfrontFeatures': {'$convert': {'input': '$numOfWaterfrontFeatures', 'to': 'int', 'onError': None}},
            'numOfWindowFeatures': {'$convert': {'input': '$numOfWindowFeatures', 'to': 'int', 'onError': None}},
            'numOfCommunityFeatures': {'$convert': {'input': '$numOfCommunityFeatures', 'to': 'int', 'onError': None}},
            'numOfPrimarySchools': {'$convert': {'input': '$numOfPrimarySchools', 'to': 'int', 'onError': None}},
            'numOfElementarySchools': {'$convert': {'input': '$numOfElementarySchools', 'to': 'int', 'onError': None}},
            'numOfMiddleSchools': {'$convert': {'input': '$numOfMiddleSchools', 'to': 'int', 'onError': None}},
            'numOfHighSchools': {'$convert': {'input': '$numOfHighSchools', 'to': 'int', 'onError': None}},
            'avgSchoolSize': {'$convert': {'input': '$avgSchoolSize', 'to': 'int', 'onError': None}},
            'MedianStudentsPerTeacher': {'$convert': {'input': '$MedianStudentsPerTeacher', 'to': 'int', 'onError': None}},
            'numOfBathrooms': {'$convert': {'input': '$numOfBathrooms', 'to': 'double', 'onError': None}},
            'numOfBedrooms': {'$convert': {'input': '$numOfBedrooms', 'to': 'int', 'onError': None}},
            'numOfStories': {'$convert': {'input': '$numOfStories', 'to': 'int', 'onError': None}},
            'latest_saledate': {'$convert': {'input': '$latest_saledate', 'to': 'date', 'onError': None}}
        }
    },
    {
        '$merge': {
            'into': 'austin',
            'whenMatched': 'merge',
            'whenNotMatched': 'discard'
        }
    }
])

