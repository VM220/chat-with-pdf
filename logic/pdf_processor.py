import os
import tempfile
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import streamlit as st

def process_pdf(uploaded_file, api_key):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = splitter.split_documents(documents)

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )

        collection_name = f"pdf_collection_{hash(uploaded_file.name) % 10000}"
        chroma_client = chromadb.Client(chromadb.config.Settings(anonymized_telemetry=False))

        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory="./chroma_db",
            client=chroma_client
        )

        os.unlink(tmp_file_path)
        return vectorstore, len(texts)
    
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None, 0
