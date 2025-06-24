import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
import time


from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY=os.environ["GROQ_API_KEY"]

if "vector" not in st.session_state:
    st.session_state.embeddings = OllamaEmbeddings(
        model="deepseek-r1:7b"
    )
    st.session_state.loader=WebBaseLoader("https://python.langchain.com/docs/introduction/")
    st.session_state.docs= st.session_state.loader.load()


    st.session_state.text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    st.session_state.final_documents=st.session_state.text_splitter.split_documents(st.session_state.docs[:5])
    st.session_state.vectors=FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)


st.title("LangChain Groq App")
llm=ChatGroq(groq_api_key=GROQ_API_KEY,
             model="gemma2-9b-it")

prompt=ChatPromptTemplate.from_template(
    """Answer the following question based on the provided context.
    Please provide the most accurate response based on the question
    <context>
    {context}
    <context>
    Questions:{input}
    """
)

document_chain=create_stuff_documents_chain(llm,prompt)
retriever=st.session_state.vectors.as_retriever()
retriever_chain= create_retrieval_chain(retriever, document_chain)


prompt=st.chat_input("What do you want to know   ")


if prompt:
    start=time.process_time()
    response=retriever_chain.invoke({"input":prompt})
    print("Response time: ", time.process_time() - start)
    print(response['answer'])

    #with streamlit expander
    with st.expander("Document Similarity search"):
        #find relevant chunks
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------------")