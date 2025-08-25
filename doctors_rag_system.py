import json
import os
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    
    # LLM: Use Groq with your API key
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

# Main execution
if __name__ == "__main__":
    # Replace with your Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # if GROQ_API_KEY == "api_key":
    #     logging.error("Please set your GROQ_API_KEY environment variable or update the script.")
    #     exit(1)
    
    # Load documents
    docs = load_documents()
    if not docs:
        logging.error("No documents loaded. Check dataset/cleaned_data.json")
        exit(1)
    
    # Build or load vector store
    if os.path.exists("faiss_index_doctors"):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.load_local("faiss_index_doctors", embeddings, allow_dangerous_deserialization=True)
        logging.info("Loaded existing vector store")
    else:
        vectorstore = build_vector_store(docs)
    
    # Interactive query loop
    while True:
        question = input("Ask a question about doctors (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        answer = query_rag(question, vectorstore, GROQ_API_KEY)
        print(f"Answer: {answer}\n")