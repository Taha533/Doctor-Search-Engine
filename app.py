import json
import os
import streamlit as st
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Step 1: Load the cleaned data from JSON
def load_documents(json_file='dataset/cleaned_data.json'):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        for entry in data:
            # Create a document from the entry, with metadata
            doc_content = f"Doctor: {entry['title']}, Specialty: {entry['specialty']}, Location: {entry['location']}"
            metadata = {
                'source': entry['url'],
                'name': entry['title'],
                'specialty': entry['specialty'],
                'location': entry['location']
            }
            documents.append({
                'page_content': doc_content,
                'metadata': metadata
            })
        
        from langchain_core.documents import Document
        return [Document(page_content=d['page_content'], metadata=d['metadata']) for d in documents]
    except Exception as e:
        logging.error(f"Error loading JSON: {e}")
        return []

# Step 2: Build the vector store (run once)
def build_vector_store(docs):
    if not docs:
        logging.error("No documents to process")
        return None
    text_splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    
    # Embeddings: Use HuggingFace (local, no API key needed)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Vector store: FAISS for local, efficient similarity search
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local("faiss_index_doctors")  # Save for reuse
    logging.info("Vector store built and saved")
    return vectorstore

# Step 3: Query the RAG system
def query_rag(question, vectorstore, groq_api_key, top_k=5):
    if not vectorstore:
        return "No data available to query."
    
    # LLM: Use Groq with the provided API key
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",  # Or "llama3-70b-8192" if preferred
        temperature=0
    )
    
    # Retriever: Get top_k similar chunks
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    
    # Prompt: Customized RAG prompt for doctor queries
    prompt = hub.pull("rlm/rag-prompt")
    prompt.messages[0].prompt.template = """You are a helpful assistant that answers questions about doctors based on the provided context. 
    For each doctor, include name, url, location, and specialty. If no doctors match, say so.
    
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    # Chain: Retrieve -> Format context -> Prompt -> LLM -> Parse output
    def format_docs(docs):
        return "\n\n".join(f"Doctor: {doc.metadata['name']}\nURL: {doc.metadata['source']}\nLocation: {doc.metadata['location']}\nSpecialty: {doc.metadata['specialty']}\n{doc.page_content}" for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Run the query
    response = rag_chain.invoke(question)
    return response

# Streamlit App
def main():
    st.set_page_config(page_title="Doctor Search Engine", page_icon="🩺")

    # Sidebar for chat history
    st.sidebar.title("Chat History")
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Main content
    st.title("Doctor Search Engine")
    st.write("Ask questions about doctors, such as 'Provide me the list of available doctors in Dhaka' or 'Suggest some Dermatologist from Jessore'.")

    # Check for Groq API key in environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # If no API key in .env, prompt user
    if not groq_api_key:
        groq_api_key = st.text_input("Enter your Groq API Key:", type="password")
        if not groq_api_key:
            st.warning("Please enter your Groq API key to proceed.")
            return
    else:
        st.info("Groq API key loaded from environment.")

    # Load documents
    docs = load_documents()
    if not docs:
        st.error("No documents loaded. Check dataset/cleaned_data.json")
        return

    # Build or load vector store
    if os.path.exists("faiss_index_doctors"):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.load_local("faiss_index_doctors", embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = build_vector_store(docs)
        if not vectorstore:
            st.error("Failed to build vector store.")
            return

    # User input
    question = st.text_input("Ask a question about doctors:")
    if question:
        with st.spinner("Processing..."):
            answer = query_rag(question, vectorstore, groq_api_key)
            st.markdown(f"**Answer:** {answer}")
            
            # Save to chat history
            st.session_state.chat_history.append({"question": question, "answer": answer})

    # Display chat history in sidebar
    for idx, chat in enumerate(reversed(st.session_state.chat_history), 1):
        with st.sidebar.expander(f"Chat {len(st.session_state.chat_history) - idx + 1}"):
            st.write(f"**Q:** {chat['question']}")
            st.write(f"**A:** {chat['answer']}")

if __name__ == "__main__":
    main()
