import os
from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
import certifi

#Connent database
url =os.getenv("DB_URL")
client = MongoClient(url, tlsCAFile=certifi.where())

#create database and collection
db=client["ai_news_agent"]
news_collection = db["news"]

