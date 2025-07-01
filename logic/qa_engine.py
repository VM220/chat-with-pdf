from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

def create_qa_chain(vectorstore, api_key):
    prompt_template = """
    You are a helpful AI assistant...
    Context:
    {context}
    Question: {question}
    Answer:"""

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.3
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain

def get_answer(question, qa_chain):
    try:
        with st.spinner("🤔 Thinking..."):
            result = qa_chain.invoke({"query": question})
            return result["result"], result.get("source_documents", [])
    except Exception as e:
        st.error(f"Error getting answer: {str(e)}")
        return None, []
