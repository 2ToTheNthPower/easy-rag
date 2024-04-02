import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.ollama import OllamaEmbedding
import time
import psycopg2
import requests

from llama_index.core import PromptTemplate

template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given this information, please answer the question: {query_str}\n"
)
qa_template = PromptTemplate(template)

# Streamed response emulator
def response_streamer(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

# Add button that will request an index from the parser API
with st.sidebar:

    st.title("Index all data")
    local_models = [model["name"] for model in requests.get('http://localhost:11434/api/tags').json()["models"]]

    embedding_model = st.selectbox("Select embedding model", local_models)

    if st.button("Start"):
        with st.spinner("Indexing data..."):
            # Post request to localhost:8001/index
            response = requests.post("http://0.0.0.0:8001/index", json={"name": embedding_model})
    
    st.markdown("""---""")
    st.title("Choose chat model")
    llm_name = st.selectbox("Select chat model", local_models)

    st.markdown("""---""")
    st.title("Pull Ollama model")
    # Allow user to enter model name to pull
    st.link_button("See options", "https://ollama.com/library")
    model_to_pull = st.text_input("Enter model name to pull")

    if st.button("Pull model"):
        with st.spinner("Pulling model..."):
            response = requests.post("http://localhost:11434/api/pull", json={"name": model_to_pull})

# bge embedding model
# Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.embed_model = OllamaEmbedding(model_name=embedding_model)

# ollama
Settings.llm = Ollama(model="llama2", request_timeout=30.0)

# create the chroma client and add or retrieve our data
remote_db = chromadb.HttpClient()
chroma_collection = remote_db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_query_engine(text_qa_template=qa_template, top_k=10)

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
        _ = st.write_stream(response_streamer(msg))

    st.session_state.messages.append({"role": "assistant", "content": msg})

    