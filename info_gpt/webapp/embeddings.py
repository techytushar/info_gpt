import streamlit
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()


def init_embeddings_object():
    openai_api_key = streamlit.secrets["OPENAI_API_KEY"]
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    return embeddings
