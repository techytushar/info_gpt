import requests
from celery.app import Celery
from celery.utils.log import get_task_logger

from info_gpt.api import constants
from info_gpt.db import get_db_with_embedding

celery_app = Celery(__name__, broker=constants.REDIS_URL, backend=constants.REDIS_URL)
logger = get_task_logger(__name__)


@celery_app.task
def send_top_k(query: str, response_url: str):
    retriever = get_db_with_embedding().as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(query)
    answer = "Here are the top 3 relevant results:\n"
    for i, doc in enumerate(docs):
        answer += f"{i+1}. {doc.page_content} ({doc.metadata['source']})\n"
    response = requests.post(response_url, json={"text": answer}, timeout=10)
    if response.status_code != 200:
        logger.error(f"Failed to send final response for query {query}")
