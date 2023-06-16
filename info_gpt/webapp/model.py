import streamlit
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

load_dotenv()


class QASystem:
    @staticmethod
    def qa_without_sources(vector_store, query):
        openai_api_key = streamlit.secrets["OPENAI_API_KEY"]

        llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        chain = load_qa_chain(llm, chain_type="stuff")
        print(f"Loaded QA chain: {chain}")

        docs = vector_store.similarity_search(query, include_metadata=True)
        num_docs = len(docs)
        print(f"Found {num_docs} documents similar to the query: {query}")

        result = chain.run(input_documents=docs, question=query)
        print(f"Answer found: {result}")

        return result


    @staticmethod
    def retrieve_document(vector_store, query):
        llm = OpenAI()
        retriever = vector_store.as_retriever()
        should_return_source_documents = streamlit.secrets["QA_WITH_SOURCE"] == 'true'
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                         retriever=retriever, return_source_documents=should_return_source_documents)
        result = qa({"query": query})
        if should_return_source_documents:
            return {"result": result["result"], "source_documents": result["source_documents"]}

        return {"result": result["result"]}
