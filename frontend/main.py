import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.ollama import OllamaEmbedding
import time
import psycopg2
import requests

# Streamed response emulator
def response_streamer(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

# Add button that will request an index from the parser API
if st.button("Index data"):
    st.write("Indexing data...")
    # Post request to localhost:8001/index
    response = requests.post("http://0.0.0.0:8001/index")

# bge embedding model
# Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# ollama
Settings.llm = Ollama(model="llama2", request_timeout=30.0)

# create the chroma client and add or retrieve our data
remote_db = chromadb.HttpClient()
chroma_collection = remote_db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_query_engine()

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = query_engine.query(prompt)
    msg = response.response
    

    with st.chat_message("assistant"):
        _ = st.markdown(st.write_stream(response_streamer(msg)))

    st.session_state.messages.append({"role": "assistant", "content": msg})

    