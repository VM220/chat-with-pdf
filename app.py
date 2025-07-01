import streamlit as st
from logic.api_setup import setup_gemini_api
from logic.pdf_processor import process_pdf
from logic.qa_engine import create_qa_chain, get_answer
from logic.utils import display_sources

# Page configuration
st.set_page_config(
    page_title="PDF Q&A Bot with RAG",
    page_icon="📚",
    layout="wide"
)

# Session state initialization
if 'messages' not in st.session_state: st.session_state.messages = []
if 'qa_chain' not in st.session_state: st.session_state.qa_chain = None
if 'processed_file' not in st.session_state: st.session_state.processed_file = None
if 'message_counter' not in st.session_state: st.session_state.message_counter = 0

# Initialize API
api_key = setup_gemini_api()

# Title and Info
st.title("📚 PDF Q&A Bot with RAG")
st.info("🤖 Powered by Google Gemini 2.0 Flash + ChromaDB (RAG)")

# Upload and Instructions
upload_col, instructions_col = st.columns([1, 1])

with upload_col:
    st.header("📄 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file:
        st.success(f"📁 Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        if st.button("🔄 Process PDF", use_container_width=True):
            vectorstore, num_chunks = process_pdf(uploaded_file, api_key)
            if vectorstore:
                qa_chain = create_qa_chain(vectorstore, api_key)
                st.session_state.qa_chain = qa_chain
                st.session_state.processed_file = uploaded_file.name
                st.session_state.messages = []
                st.session_state.message_counter = 0
                st.balloons()
                st.success(f"✅ Processed {num_chunks} chunks from PDF!")

    if st.session_state.processed_file:
        st.info(f"📋 Current file: {st.session_state.processed_file}")

with instructions_col:
    st.header("💡 How to use")
    st.markdown("""
    **Step 1:** Upload your PDF  
    **Step 2:** Click "Process PDF"  
    **Step 3:** Ask questions below  
    **Step 4:** Get detailed AI answers with sources
    """)
    
    st.markdown("### ✨ Features")
    st.markdown("""
        - 🤖 **AI-Powered**: Google Gemini 2.0 Flash
        - 🔍 **RAG Technology**: Retrieval Augmented Generation
        - 📚 **Vector Search**: ChromaDB similarity search
        - 📖 **Source Citations**: Shows relevant document sections
        - 💬 **Natural Language**: Ask questions naturally
        - 🎯 **Accurate Answers**: Context-based responses
        """)

# Sample Questions
st.markdown("---")
st.header("🤔 Sample Questions")

sample_questions = [
    "What is the main topic?",
    "Summarize the key points",
    "What are the conclusions?",
    "List the important findings"
]
sample_cols = st.columns(4)

for col, question in zip(sample_cols, sample_questions):
    with col:
        if st.button(f"💬 {question}", key=question):
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
                st.warning("⚠️ Please process a PDF first!")

# Chat Interface
st.markdown("---")
st.header("💬 Chat with your PDF")

if not st.session_state.qa_chain:
    st.warning("⚠️ Please upload and process a PDF to begin chatting.")
else:
    with st.container():
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg["role"] == "assistant" and "sources" in msg:
                    display_sources(msg["sources"], msg["id"])

    if prompt := st.chat_input("Ask a question about your PDF..."):
        st.session_state.message_counter += 1
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "id": st.session_state.message_counter
        })
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                answer, sources = get_answer(prompt, st.session_state.qa_chain)
                if answer:
                    st.write(answer)
                    st.session_state.message_counter += 1
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "id": st.session_state.message_counter
                    })
                    display_sources(sources, st.session_state.message_counter)

# Chat Controls
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💬 Messages", len(st.session_state.messages))
with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.message_counter = 0
        st.rerun()
with col3:
    if st.button("📊 Show Stats", use_container_width=True):
        st.info(f"📄 File: {st.session_state.processed_file}")
