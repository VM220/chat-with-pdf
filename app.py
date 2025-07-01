import streamlit as st
import tempfile
import os
from pathlib import Path
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import chromadb
import time
import hashlib
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure page
st.set_page_config(
    page_title="PDF Q&A Bot with RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None
if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0

def setup_gemini_api():
    """Setup Gemini API configuration"""
    # Try to get API key from multiple sources
    api_key = None
    
    # Try Streamlit secrets first
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass
    
    # Try environment variable
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    # Ask user to input if not found
    if not api_key:
        st.error("🔑 Google API Key Required")
        st.info("Please set your Google API key in one of these ways:")
        st.code("1. Create .streamlit/secrets.toml with: GOOGLE_API_KEY = 'your-key'")
        st.code("2. Set environment variable: GOOGLE_API_KEY=your-key")
        
        # Allow manual input
        api_key = st.text_input("Or enter your Google API key here:", type="password")
        if not api_key:
            st.stop()
    
    genai.configure(api_key=api_key)
    return api_key

def process_pdf(uploaded_file, api_key):
    """Process uploaded PDF and create vector store"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Load PDF
        with st.spinner("📄 Loading PDF..."):
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            
        st.success(f"✅ Loaded {len(documents)} pages from PDF")

        # Split documents
        with st.spinner("✂️ Splitting document into chunks..."):
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            texts = text_splitter.split_documents(documents)
            
        st.success(f"✅ Split into {len(texts)} text chunks")

        # Create embeddings
        with st.spinner("🧠 Creating embeddings..."):
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )

        # Create vector store with telemetry disabled
        with st.spinner("🗄️ Creating vector database..."):
            # Create a unique collection name
            collection_name = f"pdf_collection_{hash(uploaded_file.name) % 10000}"
            
            # Configure ChromaDB client with telemetry disabled
            chroma_client = chromadb.Client(chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            ))
            
            vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory="./chroma_db",
                client=chroma_client
            )
            
        st.success("✅ Vector database created successfully!")

        # Create QA chain with custom prompt
        prompt_template = """
        You are a helpful AI assistant that answers questions based on the provided context from a PDF document.
        
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
        Be specific and provide detailed answers when possible.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        # Updated LLM configuration without deprecated parameters
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return vectorstore, qa_chain, len(texts)
        
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        return None, None, 0

def get_answer(question, qa_chain):
    """Get answer from QA chain using the new invoke method"""
    try:
        with st.spinner("🤔 Thinking..."):
            # Use invoke instead of __call__ to avoid deprecation warning
            result = qa_chain.invoke({"query": question})
            return result["result"], result.get("source_documents", [])
    except Exception as e:
        st.error(f"❌ Error getting answer: {str(e)}")
        return None, []

def display_sources(sources, message_id):
    """Display sources with unique keys"""
    if sources:
        with st.expander("📖 View Sources", expanded=False):
            for i, source in enumerate(sources):
                st.markdown(f"**Source {i+1}:**")
                
                # Create unique key for each text area
                unique_key = f"source_{message_id}_{i}_{hash(source.page_content[:50]) % 1000}"
                
                st.text_area(
                    f"Content {i+1}:",
                    source.page_content[:500] + "..." if len(source.page_content) > 500 else source.page_content,
                    height=100,
                    key=unique_key
                )
                if hasattr(source, 'metadata') and source.metadata:
                    st.caption(f"📄 Page: {source.metadata.get('page', 'Unknown')}")
                st.markdown("---")

def main():
    # Setup API
    api_key = setup_gemini_api()
    
    # Header
    st.title("📚 PDF Q&A Bot with RAG")
    st.markdown("Upload a PDF and ask questions about its content using AI-powered Retrieval Augmented Generation")
    
    # Show current model info
    st.info("🤖 Using Google Gemini 2.0 Flash with RAG technology")
    
    # Main layout - Upload section and Instructions side by side
    upload_col, instructions_col = st.columns([1, 1])
    
    # Left column - PDF Upload
    with upload_col:
        st.header("📄 Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF file to analyze and ask questions about"
        )
        
        if uploaded_file is not None:
            st.success(f"📁 File uploaded: {uploaded_file.name}")
            st.info(f"📊 File size: {uploaded_file.size / 1024:.1f} KB")
            
            # Process PDF button
            if st.button("🔄 Process PDF", type="primary", use_container_width=True):
                vectorstore, qa_chain, num_chunks = process_pdf(uploaded_file, api_key)
                if vectorstore and qa_chain:
                    st.session_state.vectorstore = vectorstore
                    st.session_state.qa_chain = qa_chain
                    st.session_state.processed_file = uploaded_file.name
                    st.session_state.messages = []  # Clear previous messages
                    st.session_state.message_counter = 0  # Reset counter
                    st.balloons()
                    st.success(f"🎉 PDF processed! Created {num_chunks} text chunks.")
        
        # Display current file status
        if st.session_state.processed_file:
            st.info(f"📋 Current file: {st.session_state.processed_file}")
    
    # Right column - Instructions
    with instructions_col:
        st.header("💡 How to use")
        st.markdown("""
        **Step 1:** 📤 Upload a PDF file using the file uploader
        
        **Step 2:** 🔄 Click 'Process PDF' to analyze the document
        
        **Step 3:** 💬 Ask questions about the content in the chat below
        
        **Step 4:** 🎯 Get AI-powered answers with source citations
        """)
        
        # Show features
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🤖 **AI-Powered**: Google Gemini 2.0 Flash
        - 🔍 **RAG Technology**: Retrieval Augmented Generation
        - 📚 **Vector Search**: ChromaDB similarity search
        - 📖 **Source Citations**: Shows relevant document sections
        - 💬 **Natural Language**: Ask questions naturally
        - 🎯 **Accurate Answers**: Context-based responses
        """)
    
    # Sample Questions Section (full width)
    st.markdown("---")
    st.header("🤔 Sample Questions")
    
    # Create columns for sample questions
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    
    sample_questions = [
        "What is the main topic?",
        "Summarize the key points",
        "What are the conclusions?",
        "List the important findings"
    ]
    
    columns = [q_col1, q_col2, q_col3, q_col4]
    
    for i, (question, col) in enumerate(zip(sample_questions, columns)):
        with col:
            if st.button(f"💬 {question}", key=f"sample_{question}", use_container_width=True):
                if st.session_state.qa_chain:
                    st.session_state.message_counter += 1
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": question,
                        "id": st.session_state.message_counter
                    })
                    answer, sources = get_answer(question, st.session_state.qa_chain)
                    if answer:
                        st.session_state.message_counter += 1
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "sources": sources,
                            "id": st.session_state.message_counter
                        })
                    st.rerun()
                else:
                    st.warning("⚠️ Please upload and process a PDF first!")

    # Chat Interface Section (full width)
    st.markdown("---")
    st.header("💬 Chat with your PDF")
    
    # Check if PDF is processed
    if not st.session_state.qa_chain:
        st.warning("⚠️ Please upload and process a PDF file first!")
        st.info("👆 Use the upload section above to get started")
    else:
        # Chat container
        chat_container = st.container()
        
        # Display chat messages
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # Show sources for assistant messages
                    if message["role"] == "assistant" and "sources" in message:
                        display_sources(message["sources"], message.get("id", 0))

        # Chat input
        if prompt := st.chat_input("Ask a question about your PDF..."):
            # Add user message
            st.session_state.message_counter += 1
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt,
                "id": st.session_state.message_counter
            })
            
            # Display user message immediately
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Generating response..."):
                    answer, sources = get_answer(prompt, st.session_state.qa_chain)
                
                if answer:
                    st.write(answer)
                    
                    # Add to session state
                    st.session_state.message_counter += 1
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources,
                        "id": st.session_state.message_counter
                    })
                    
                    # Show sources
                    display_sources(sources, st.session_state.message_counter)
        
        # Statistics and controls
        st.markdown("---")
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            st.metric("💬 Messages", len(st.session_state.messages))
        
        with stats_col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.message_counter = 0
                st.rerun()
        
        with stats_col3:
            if st.button("📊 Show Stats", use_container_width=True):
                st.info(f"📄 File: {st.session_state.processed_file}")

if __name__ == "__main__":
    main()
