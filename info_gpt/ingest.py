import logging

from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

from info_gpt import constants
from info_gpt.db import get_db
from info_gpt.scrapers import confluence, github


class Ingest:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=constants.EMBEDDING_MODEL_NAME,
        )
        self.db = get_db(self.embeddings)
        self.lang_extension_map = {
            ".cpp": Language.CPP,
            ".go": Language.GO,
            ".java": Language.JAVA,
            ".js": Language.JS,
            ".php": Language.PHP,
            ".py": Language.PYTHON,
            ".rst": Language.RST,
            ".rb": Language.RUBY,
            ".rs": Language.RUST,
            ".sc": Language.SCALA,
            ".swift": Language.SWIFT,
            ".md": Language.MARKDOWN,
            ".tex": Language.LATEX,
            ".html": Language.HTML,
        }

    async def load_github(self, organization, file_extension):
        text_splitter = RecursiveCharacterTextSplitter.from_language(
            self.lang_extension_map[file_extension],
        )
        async for files in github.read_all_files_in_org(organization, file_extension):
            documents = [
                Document(
                    page_content=file["content"],
                    metadata={"source": file["url"]},
                )
                for file in files
            ]
            logging.info(f"Ingesting {len(documents)} documents in DB")
            try:
                self.db.add_documents(text_splitter.split_documents(documents))
            except Exception:
                logging.exception(f"Failed to process {len(files)} files")

    def load_confluence(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=256,
            chunk_overlap=16,
            length_function=len,
        )
        for pages in confluence.read_all_pages():
            documents = [
                Document(
                    page_content=page[0],
                    metadata={"source": page[1]},
                )
                for page in pages
            ]
            try:
                self.db.add_documents(text_splitter.split_documents(documents))
            except Exception:
                logging.exception(f"Failed to process {len(pages)} page.")
