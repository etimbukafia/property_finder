from pymongo import MongoClient
import os
from dotenv import load_dotenv
from utils import llm
import streamlit as st
import urllib,io,json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging
load_dotenv()

password = os.environ['PASSWORD']
username = os.environ['USERNAME']

if not password or not username:
    st.error("Environment variables for MongoDB credentials are not set.")
else:
    # MongoDB Client
    try:
        client = MongoClient(f"mongodb+srv://{username}:{password}@realestatecluster.kypuqxb.mongodb.net/?retryWrites=true&w=majority&appName=realEstateCluster")
        db = client['listings']
        collection = db['austin']
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")

    st.title("Find you Dream House")
    st.write("what kind of house are you looking for?")
    user_input = st.text_area("enter your description here")


    with io.open("descriptions.txt","r",encoding="utf-8")as f1:
        sample=f1.read()
    

    with io.open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    query = PromptTemplate(
        template=prompt,
        input_variables=["question", "sample"]
    )

    llmchain = LLMChain(llm=llm, prompt=query, verbose=True)

    if user_input:
        button = st.button("Submit")
        if button:
            try:
                # Invoke the LLM Chain
                response = llmchain.invoke({
                    "question": user_input,
                    "sample": sample
                })
                query = json.loads(response["text"])
                results = collection.aggregate(f'({query})')

                print(f"Generated Query: {query}")
                print(f"Generated results: {results}")
                found_results = False
                for result in results:
                    found_results = True
                    st.write(result)
                if not found_results:
                    st.write("No houses found that match your description.")
            except Exception as e:
                logging.errror(f"An error occurred: {e}")