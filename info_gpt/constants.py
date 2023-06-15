import logging
import os

from chromadb.config import Settings

READ_TIMEOUT = 60

# DB settings
CHROMA_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=os.environ.get("DB_DIRECTORY", ".db"),
    anonymized_telemetry=False,
)
DB_COLLECTION_NAME = os.environ.get("DB_COLLECTION_NAME", "hackathon")

# Model settings
MODEL_TYPE = os.environ.get(
    "MODEL_TYPE",
    "OpenAI",
)  # LlamaCpp or GPT4All or OpenAI supported
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    "./models/ggml-gpt4all-j-v1.3-groovy.bin",
)  # https://gpt4all.io/index.html
MODEL_N_CTX = int(os.environ.get("MODEL_N_CTX", 128))
TEMPERATURE = float(os.environ.get("TEMPERATURE", 0.2))

# Embeddings settings
EMBEDDING_MODEL_NAME = os.environ.get(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
)  # https://www.sbert.net/docs/pretrained_models.html

# Chat app settings
STREAMING_OUTPUT = int(os.environ.get("STREAMING_OUTPUT", 0))  # 0 or 1
logging.basicConfig(level=logging.INFO)
