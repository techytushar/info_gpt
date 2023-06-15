"""Module for scrapping and ingesting data into the DB."""
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

    async def load_github(self, organization: str, file_extension: str) -> None:
        """Ingest scrapped data from GitHub into the DB.

        Parameters
        ----------
        organization : str
            GitHub organization name.
        file_extension : str
            Extension of the files to fetch.
        """
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

    def load_confluence(
        self,
        base_url: str,
        exclude_spaces: list[str] | None = None,
    ) -> None:
        """Ingest scrapped data from confluence pages into the DB.

        Parameters
        ----------
        base_url : str
            Base URL of Confluence in the following format: https://{org}.atlassian.net/wiki/
        exclude_spaces : list[str] | None
            List of space names to exclude. Includes all pages by default.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=20,
            length_function=len,
        )
        for pages in confluence.read_all_pages(base_url, exclude_spaces):
            documents = [
                Document(
                    page_content=page_info[0],
                    metadata={"source": page_info[1]},
                )
                for page_info in pages
            ]
            try:
                self.db.add_documents(text_splitter.split_documents(documents))
            except Exception:
                logging.exception(f"Failed to process {len(pages)} page.")
