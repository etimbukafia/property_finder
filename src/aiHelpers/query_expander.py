import json
from models import Result
import logging

app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

def query_expansion(client, query, number=5):
    messages=[
        {"role": "system", 
         "content": 
         f"""
        You are part of a real estate information system that processes user queries.

        Your task is to expand a given real estate query into {number} related queries. These expanded queries should be similar in meaning to the original query but offer different perspectives or keywords or keyword synonyms.

        Structure:

        Follow the structure shown below in examples to generate expanded queries.

        Examples:

        Example Query 1: "affordable 2-bedroom apartments"
        Example Expanded Queries: ["budget-friendly two-bedroom flats", "inexpensive two-bedroom apartments for rent", "cheap two-bedroom flats available"]

        Example Query 2: "beautiful houses with a garden and swimming pool"
        Example Expanded Queries: ["lovely properties with a backyard and private swimming pool", "villas featuring a landscaped garden and a sparkling swimming pool", "fine detached houses with outdoor space and a well-maintained pool"]

        Example Query 3: "penthouse apartments with stunning views"
        Example Expanded Queries: ["luxury penthouses with panoramic city views", "high-rise apartments overlooking the ocean", "exclusive penthouses with breathtaking mountain vistas"]

        Example Query 4: "commercial properties for sale"
        Example Expanded Queries: ["office spaces available for sale in prime business districts", "retail properties for purchase in high-traffic areas", "commercial real estate listings with excellent investment potential"]

        Example Query 5: "rental properties near schools"
        Example Expanded Queries: ["apartments or houses located within walking distance of top-rated schools", "properties in safe neighborhoods with easy access to educational institutions", "rental listings near universities or colleges"]
                
        Return the output as a JSON array.

        Your Task:

        Query: "{query}"
        Example Expanded Queries(JSON array):
        """,
        },
        {"role": "user", "content": query}
        ]
    
    response = client.chat.completions.create(
        model="accounts/fireworks/models/firefunction-v1",
        response_format={
            "type": "json_object", 
            "schema": Result.model_json_schema()
        },
        messages=messages
    )

    response_content = response.choices[0].message.content
    app_logger.info(f"response is: {response_content}")
    parsed_response = json.loads(response_content)
    app_logger.info(f"parsed response is: {parsed_response}")
    return parsed_response
