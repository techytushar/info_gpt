import streamlit as st
from dotenv import load_dotenv

from embeddings import init_embeddings_object
from model import QASystem
from utils import format_docs, split_document_into_chunks
from vector_store import ChromaSearch

load_dotenv()

st.set_page_config(page_title="PDF QA Tool", page_icon=":magic_wand:", layout="centered")

st.title(" :magic_wand: peak-genie: PDF Question-Answering Tool")
st.caption("peak-genie is an AI-powered PDF QA tool that enables you to easily upload and analyze PDF documents"
           " with advanced question-answering capabilities. "
           " peak-genie goes beyond traditional keyword-based search "
           " and utilizes vector embeddings and semantic search "
           "to deliver precise and efficient results"
           " from your PDFs to improve your workflow efficiency.")
st.divider()


def run_app():
    uploader = QaApp()

    uploader.load_content()

    uploader.create_embeddings()

    if "run_qa" not in st.session_state:
        st.session_state.run_qa = False

    if not st.session_state.run_qa:
        if st.button("Run Question-Answering Task"):
            st.session_state.run_qa = True
    else:
        uploader.run_qa()
        if uploader.show_qa:
            uploader.display_result()
        if st.button("Clear", key="qa_clear_button"):
            st.session_state.run_qa = False


class QaApp:
    def __init__(self):
        # self.file_path = None
        self.pages = None
        self.texts = None
        self.file_key = "test"
        self.question = None
        self.result = None
        self.vector_store = None
        self.embeddings = None
        self.use_pinecone = st.secrets["USE_PINECONE"] == "false"
        self.run_qa_with_source = st.secrets["QA_WITH_SOURCE"] == "true"
        self.show_qa = False

    def load_content(self):
        self.file_path = st.file_uploader("Upload PDF", type="pdf")
        if self.file_path:
            if self.file_path.type == "application/pdf":
                print("PDF uploaded successfully.")
                st.write(":white_check_mark: PDF uploaded successfully.")
                # self.pages = load_document_pages(self.file_path) #Todo: refer from confluence.py
                self.texts = split_document_into_chunks(self.pages)
            else:
                st.error("Please upload a PDF file.")

    def get_search_strategy(self):
        print("Using Chroma search strategy")
        search_strategy = ChromaSearch()
        return search_strategy


    def create_embeddings(self):
        if self.texts:
            self.embeddings = init_embeddings_object()
            search_strategy = self.get_search_strategy()
            self.vector_store = search_strategy.push_documents(self.texts, self.embeddings)
            st.write(":white_check_mark: PDF text uploaded to vector store.")


    def run_qa(self):
        if self.vector_store:
            qa_system = QASystem()
            self.question = st.text_input("Enter your question:", key='textbox', placeholder="Enter your question here")
            if st.button("Ask"):
                print(f"use source? {self.run_qa_with_source}")
                if self.run_qa_with_source:
                    self.result = qa_system.retrieve_document(self.vector_store, self.question)
                else:
                    self.result = qa_system.qa_without_sources(self.vector_store, self.question)
                self.show_qa = True
        else:
            st.warning("Please upload a PDF file and click on Ask button.")

    @staticmethod
    def clear_callback():
        st.session_state["textbox"] = ""

    def display_result(self):
        if self.result:
            st.write(f":question: Question: {self.question}")
            st.write(f":zap: Answer: {self.result['result']}")
            if self.run_qa_with_source:
                with st.expander("Show Source"):
                    st.write("The relevant source documents are:")
                    source = format_docs(self.result['source_documents'])
                    st.write(f"Source: {source}")
            if st.button("Clear", on_click=self.clear_callback):
                self.question = None
                self.result = None
                self.show_qa = False
        else:
            st.warning("Please run the question-answering task first.")


if __name__ == '__main__':
    run_app()
