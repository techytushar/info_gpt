import os
from typing import Literal

from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.vectorstores import Chroma

from info_gpt import constants


def get_db(embedding_function):
    return Chroma(
        embedding_function=embedding_function,
        collection_name=constants.DB_COLLECTION_NAME,
        client_settings=constants.CHROMA_SETTINGS,
    )


def get_db_with_embedding(embedding_type: Literal["HuggingFace", "OpenAI"] = "OpenAI"):
    if embedding_type == "HuggingFace":
        embeddings = HuggingFaceEmbeddings(
            model_name=constants.EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
        )
    elif embedding_type == "OpenAI":
        embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    else:
        error = "Embedding type not supported."
        raise Exception(error)
    return get_db(embeddings)
