import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.ollama import OllamaEmbedding
import time
import psycopg2
import requests

from llama_index.core import PromptTemplate
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondenseQuestionChatEngine

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
Settings.llm = Ollama(model=llm_name, request_timeout=30.0)

# create the chroma client and add or retrieve our data
remote_db = chromadb.HttpClient()
chroma_collection = remote_db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# Here, a token limit is set
memory = ChatMemoryBuffer.from_defaults(llm=Settings.llm)

query_engine = index.as_query_engine(top_k=10, verbose=True)

custom_prompt = PromptTemplate(
    """\
Given a conversation (between Human and Assistant) and a follow up message from Human, \
rewrite the message to be a standalone question that captures all relevant context \
from the conversation.

<Chat History>
{chat_history}

<Follow Up Message>
{question}

<Standalone question>
"""
)

# list of `ChatMessage` objects
custom_chat_history = [
    ChatMessage(
        role=MessageRole.USER,
        content="Hello assistant, today we are creating animations in Python using the manim library and documentation.",
    ),
    ChatMessage(role=MessageRole.ASSISTANT, content="Okay, sounds good."),
]

chat_engine = index.as_chat_engine(llm=Settings.llm, chat_mode="react", stream=True, verbose=True)

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    

    with st.chat_message("assistant"):
        msg = st.write_stream(chat_engine.stream_chat(prompt).response_gen)

    st.session_state.messages.append({"role": "assistant", "content": msg})

    