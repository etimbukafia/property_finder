from dotenv import load_dotenv
from utils import llm
import streamlit as st
import io,json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from db_connect import Database
import logging
import os
load_dotenv()

async def search_house(description) -> dict:
    collection = await Database.connect()

    with io.open("descriptions.txt","r",encoding="utf-8")   as f1:
        descriptions=f1.read()
    
    with io.open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    query_with_prompt = PromptTemplate(
        template=prompt,
        input_variables=["question", "descriptions"]
    )

    llmchain = LLMChain(llm=llm, prompt=query_with_prompt, verbose=False)

    if description:
        # Invoke the LLM Chain
        response = llmchain.invoke({
            "question": description,
            "sample": descriptions
        })
        
        query = json.loads(response["text"])
        print((f"Generated Query: {query}"))

        results = collection.aggregate(query)

        try:
            found_results = []
            async for result in results:
                found_results.append(result)
            
            if not found_results:
                return {"message": "No houses found that match your description."}
            return {"results": found_results}
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print("An error occurred")