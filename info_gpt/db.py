from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from info_gpt import constants


def get_db(embedding_function):
    return Chroma(
        embedding_function=embedding_function,
        collection_name=constants.DB_COLLECTION_NAME,
        client_settings=constants.CHROMA_SETTINGS,
    )


def get_db_with_embedding():
    embeddings = HuggingFaceEmbeddings(model_name=constants.EMBEDDING_MODEL_NAME)
    return get_db(embeddings)
