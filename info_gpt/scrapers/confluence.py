import logging
import os

from chromadb.config import Settings
from langchain.document_loaders import ConfluenceLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Document Loader
loader = ConfluenceLoader(
    url="https://peak-bi.atlassian.net/wiki",
    username="devang.grewal@peak.ai",
    api_key=os.environ["CONFLUENCE_PASSWORD"],
)

EMBEDDINGS = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

logger.info("Starting document scraping")
documents = loader.load(
    space_key="KBS",
    include_attachments=False,
    limit=1000,
    include_archived_content=False,
    include_comments=False,
    include_restricted_content=False,
)
logger.info(f"Loaded {len(documents)} documents")

vector_store = Chroma(
    embedding_function=EMBEDDINGS,
    collection_name="hackathon",
    client_settings=Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=os.environ.get("DB_DIRECTORY", ".db"),
        anonymized_telemetry=False,
    ),
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=20,
    length_function=len,
)

logger.info("Inserting documents into DB...")
vector_store.add_documents(text_splitter.split_documents(documents))
