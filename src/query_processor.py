from langchain_core.messages import HumanMessage, SystemMessage
import re

def prompt_message(llm, query):
    messages = [
        SystemMessage(content="""
            You are an expert entity extractor for real estate queries. Given a user query, your task is to:
            
            - Extract only the important entities such as property types, amenities, and other relevant details mentioned in the query.
            - Return these entities in a simplified form.

            **Output Format:**
            - "query": {user_query}
            - 'entities': {extracted_entities}
            - "processed_query": {concatenated_entities}

            **Examples:**
            - "query": "Seeking a 4-bedroom house with a cozy fireplace, hardwood floors, and a large deck overlooking a scenic view"
            'entities': ["4-bedroom house", "cozy fireplace", "hardwood floors", "large deck overlooking a scenic view"]
            "processed_query": "4-bedroom house, cozy fireplace, hardwood floors, large deck overlooking a scenic view"
            
            - "query": "A property with a home office, walk-in closets, and a gourmet kitchen"
            'entities': ["home office", "walk-in closets", "gourmet kitchen"]
            "processed_query": "home office", "walk-in closets", "gourmet kitchen"
                      
            - "query": "Looking for a family-friendly neighborhood with easy access to public transportation and nearby hiking trails"
            'entities': ["family-friendly neighborhood", "easy access to public transportation", "hiking trails"]
            "processed_query": "family-friendly neighborhood", "easy access to public transportation", "hiking trails"

            Now, please process the following query.
        """),
        HumanMessage(content=query)
    ]

    response = llm.invoke(messages)
    return response


def extract_from_response(content):
    """
    Extracts the query, entities, and processed query from the response content.

    Args:
        content (str): The response content from the LLM.

    Returns:
        dict: A dictionary containing the extracted query, entities, and processed_query.
    """
    # Corrected regex patterns to match the actual response content format
    query_pattern = r'"query":\s*"([^"]*)"'
    entities_pattern = r"'entities':\s*\[(.*?)\]"
    processed_query_pattern = r'"processed_query":\s*"([^"]*)"'

    # Extracting the matched content
    query_match = re.search(query_pattern, content)
    entities_match = re.search(entities_pattern, content)
    processed_query_match = re.search(processed_query_pattern, content)

    # Extracting and processing the entities list
    entities = entities_match.group(1) if entities_match else ""
    entities_list = [entity.strip().strip("'") for entity in entities.split(",") if entity.strip()]

    return {
        "query": query_match.group(1) if query_match else None,
        "entities": entities_list,
        "processed_query": processed_query_match.group(1) if processed_query_match else None
    }