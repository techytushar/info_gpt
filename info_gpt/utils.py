import textwrap

from langchain.text_splitter import RecursiveCharacterTextSplitter


def format_docs(docs):
    """
    Formats a list of documents and returns a well-formatted string.

    Args:
        docs (list): A list of documents where each document is a dictionary with keys 'page_content'
                     and 'metadata'.

    Returns:
        str: A well-formatted string.
    """
    output = ""
    for doc in docs:
        output += "=" * 50 + "\n"
        output += f"Source: {doc.metadata['source']}\n\n"
        output += textwrap.fill(doc.page_content, width=80) + "\n\n"
    return output


def split_document_into_chunks(pages):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len)
    texts = text_splitter.split_documents(pages)

    num_texts = len(texts)
    print(f"The documents have been split into {num_texts} chunks")

    return texts
