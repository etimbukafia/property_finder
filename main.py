from pymongo import MongoClient
import os
from dotenv import load_dotenv
from utils import llm
import streamlit as st
import urllib,io,json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
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
        collection = db['austin_reduced']
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")

    st.title("Find you Dream House")
    st.write("what kind of house are you looking for?")
    user_input = st.text_area("enter your description here")


    with io.open("descriptions.txt","r",encoding="utf-8")   as f1:
        descriptions=f1.read()
        print(descriptions)
    

    with io.open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    query_with_prompt = PromptTemplate(
        template=prompt,
        input_variables=["question", "descriptions"]
    )

    llmchain = LLMChain(llm=llm, prompt=query_with_prompt, verbose=True)

    if user_input:
        if st.button("Submit"):
            try:
                # Invoke the LLM Chain
                response = llmchain.invoke({
                    "question": user_input,
                    "sample": descriptions
                })


                query = json.loads(response["text"])
                print((f"Generated Query: {query}"))

                results = collection.aggregate(query)

                print(f'{results} gotten')

                found_results = False
                for result in results:
                    found_results = True
                    st.write(result)
                if not found_results:
                    st.write("No houses found that match your description.")
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                st.error(f"An error occurred: {e}")