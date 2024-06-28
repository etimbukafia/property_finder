from pymongo import MongoClient
import os
from dotenv import load_dotenv
from utils import llm
import streamlit as st
import urllib,io,json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
load_dotenv()

password = os.environ['PASSWORD']
username = os.environ['USERNAME']
client = MongoClient("mongodb+srv://{username}:{password}@realestatecluster.kypuqxb.mongodb.net/?retryWrites=true&w=majority&appName=realEstateCluster")

db = client['listings']
collection = db['austin']

st.title("Find you Dream House")
st.write("what kind of house are you looking for?")
input=st.text_area("enter your description here")

with io.open("sample.txt","r",encoding="utf-8")as f1:
    sample=f1.read()
    f1.close()


