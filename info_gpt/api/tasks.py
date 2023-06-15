"""Celery long running tasks."""
import requests
from celery.app import Celery
from celery.utils.log import get_task_logger

from info_gpt.api import constants
from info_gpt.chat import ask, load_model
from info_gpt.db import get_db_with_embedding

celery_app = Celery(__name__, broker=constants.REDIS_URL, backend=constants.REDIS_URL)
logger = get_task_logger(__name__)


@celery_app.task
def send_top_k(query: str, response_url: str, k: int = 3):
    """Send top k matching documents from the DB.

    Parameters
    ----------
    query : str
        Query for which similar documents need to be fetched.
    response_url : str
        Slack response url to send POST the final result to.
    k : int
        Number of similar documents to fetch.
    """
    retriever = get_db_with_embedding().as_retriever(search_kwargs={"k": k})
    docs = retriever.get_relevant_documents(query)
    answer = "Here are the top 3 relevant results:\n"
    for i, doc in enumerate(docs):
        answer += f"{i+1}. {doc.page_content} ({doc.metadata['source']})\n"
    response = requests.post(response_url, json={"text": answer}, timeout=10)
    if response.status_code != 200:
        logger.error(f"Failed to send final response for query {query}")


@celery_app.task
def get_answer_from_llm(query: str, response_url: str):
    """Fetch top documents and get a summarized answer from the LLM.

    Parameters
    ----------
    query : str
        Query from the user.
    response_url : str
        Slack URL to POST the final answer to.
    """
    answer = ask(query, load_model())
    response = requests.post(response_url, json={"text": answer}, timeout=10)
    if response.status_code != 200:
        logger.error(
            f"Failed to send final response for query {query}. {response.content}",
        )
