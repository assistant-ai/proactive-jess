from openai import OpenAI
import pinecone
import os
import json
import uuid
from dotenv import load_dotenv
from .jess_extension import jess_extension


load_dotenv()


PINECONE_KEY = os.getenv('PINECONE_KEY')
USER_ID = os.getenv('USER_ID')

client = OpenAI()


pinecone.init(api_key=PINECONE_KEY, environment='gcp-starter')


class Memory(object):

    def __init__(self, user_id, index):
        self.user_id = user_id
        self.index = index
    
    def _embed_text_with_openai(self, text):
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    @jess_extension(
        description="Store a new memory/fact about a user so you can retrive it later",
        param_descriptions={
            "fact": "A memory or a fact to store about the user"
        }
    )
    def store_in_long_term_memory(self, fact: str):
        # Generate a unique identifier for the fact (e.g., UUID)
        fact_id = str(uuid.uuid4())

        # Generate the fact vector
        fact_vector = self._embed_text_with_openai(fact)

        # Store the fact with user ID in the metadata
        self.index.upsert(vectors=[{
            "id": fact_id, 
            "values": fact_vector, 
            "metadata": {
                "user_id": self.user_id,
                "fact": fact
            }
        }])
        return "DONE"

    @jess_extension(
        description="Retrive relevant memory/facts about user by askin a questiont",
        param_descriptions={
            "question": "Query/question to use to retrieve relevant memory/facts about user",
            "count": "Amount of facts/memories to return (sorted by relevance), default is 5"
        }
    )
    def query_from_long_term_memory(self, question: str, count: int):
        if count <= 0:
            count = 5
        # Assuming 'query_vector' is the vector representation of your query
        query_vector = self._embed_text_with_openai(question)

        # Define a filter to only include keys that start with the user's ID
        query_filter = {
            "user_id": self.user_id
        }

        # Perform the query
        return json.dumps(self._extract_sorted_facts(self.index.query(filter=query_filter, top_k=count, vector=query_vector, include_metadata=True)))

    def _extract_sorted_facts(self, results_dict):
        # Extracting the facts and their scores
        facts_with_scores = [(match['metadata']['fact'], match['score']) for match in results_dict['matches']]

        # Sorting the facts by score in descending order
        sorted_facts = sorted(facts_with_scores, key=lambda x: x[1], reverse=True)

        # Extracting only the facts from the sorted tuples
        sorted_fact_strings = [fact for fact, score in sorted_facts]
        return sorted_fact_strings

    @staticmethod
    def create_memory_extension():
        index_name = 'user-facts-index'
        index = None
        try:
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(index_name, dimension=1536)  # Adjust dimension based on the model
            index = pinecone.Index(index_name)
        except:
            pass
        return Memory(USER_ID, index)
    