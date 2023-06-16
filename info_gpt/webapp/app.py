import streamlit as st
from dotenv import load_dotenv

from info_gpt.chat import ask, load_model

load_dotenv()

st.set_page_config(page_title="Doc QA Tool", page_icon=":magic_wand:", layout="centered")

st.title(" :magic_wand: peak-genie: Peak Knowledge Base Question-Answering Tool")
st.caption("peak-genie is an AI-powered Peak Knowledge Base QA tool that enables you to easily upload and analyze documents"
           " with advanced question-answering capabilities. "
           " peak-genie goes beyond traditional keyword-based search "
           " and utilizes vector embeddings and semantic search "
           "to deliver precise and efficient results"
           " from your PDFs to improve your workflow efficiency.")
st.divider()


class QaApp:
    def __init__(self):
        self.result = None
        self.query = None
        self.show_qa = False

    def run_qa(self):
        self.query = st.text_input("Enter your question:", key='textbox', placeholder="Enter your question here")
        print(self.query)
        if st.button("Ask"):
            self.result, self.source_documents = ask(self.query, load_model(), show_on_webapp=True)
            self.show_qa = True

    @staticmethod
    def clear_callback():
        st.session_state["textbox"] = ""

    def display_result(self):
        if self.result:
            st.write(f":question: Question: {self.query}")
            st.write(f":zap: Answer: {self.result}")

            with st.expander("Show Source"):
                st.write("The relevant source documents are:")
                source = self.source_documents
                st.write(f"Source: {source}")

            if st.button("Clear", on_click=self.clear_callback):
                self.question = None
                self.result = None
                self.show_qa = False
        else:
            st.warning("Please run the question-answering task first.")


def run_app():
    app = QaApp()

    if "run_qa" not in st.session_state:
        st.session_state.run_qa = False

    if not st.session_state.run_qa:
        if st.button("Run Question-Answering Task"):
            st.session_state.run_qa = True
    else:
        app.run_qa()
        if app.show_qa:
            app.display_result()
        if st.button("Clear", key="qa_clear_button"):
            st.session_state.run_qa = False


if __name__ == '__main__':
    run_app()
