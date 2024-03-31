import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
import time

# Streamed response emulator
def response_streamer(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


documents = SimpleDirectoryReader("/app/data", recursive=True).load_data()

# bge embedding model
# Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# ollama
Settings.llm = Ollama(model="llama2", request_timeout=30.0)

index = VectorStoreIndex.from_documents(
        documents, show_progress=True
    )

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():


    query_engine = index.as_query_engine(similarity_top_k=1)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = query_engine.query(prompt)
    msg = response.response
    

    with st.chat_message("assistant"):
        _ = st.write_stream(response_streamer(msg))

    st.session_state.messages.append({"role": "assistant", "content": msg})

    