import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.retrievers import VectorIndexRetriever
import time
import psycopg2
import requests

from llama_index.core import PromptTemplate
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondenseQuestionChatEngine, CondensePlusContextChatEngine

# Streamed response emulator
def response_streamer(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

# Add button that will request an index from the parser API
with st.sidebar:
    local = st.toggle('Run locally :sunglasses:', True)

    with st.expander("See options"):
        document_count = st.slider(label="How many documents per chat message?", min_value=0, max_value=20, value=3, step=1)

        if document_count > 5:
            st.warning("Adding too many documents to the context may cause the LLM to forget parts of the chat history, depending on the model.")
        if document_count == 0:
            st.warning("No context will be used.  Are you sure this is what you want?")

    if local:
        local_models = [model["name"] for model in requests.get('http://ollama:11434/api/tags').json()["models"]]

        st.markdown("""---""")
        st.title("Choose chat model")
        llm_name = st.selectbox("Select chat model", local_models)

        st.title("Index all data")
        embedding_model = st.selectbox("Select embedding model", local_models)

        if st.button("Create data embeddings"):
            with st.spinner("Indexing data..."):
                # Post request to parser:8001/index
                response = requests.post("http://parser:8001/index", json={"name": embedding_model})

        with st.expander("Pull new models"):
            st.markdown("""---""")
            st.title("Pull Ollama model")
            # Allow user to enter model name to pull
            st.link_button("See options", "https://ollama.com/library")
            model_to_pull = st.text_input("Enter model name to pull")

            if st.button("Pull model"):
                with st.spinner("Pulling model..."):
                    response = requests.post("http://ollama:11434/api/pull", json={"name": model_to_pull})
    
    else:
        st.write("Using remote models is not supported yet")

if local:
    # bge embedding model
    # Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
    Settings.embed_model = OllamaEmbedding(model_name=embedding_model, base_url="http://ollama:11434")

    # ollama
    Settings.llm = Ollama(model=llm_name, request_timeout=90.0, base_url="http://ollama:11434")

    # create the chroma client and add or retrieve our data
    remote_db = chromadb.HttpClient(host='db', port=8000)
    chroma_collection = remote_db.get_or_create_collection("quickstart")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Here, a token limit is set
    memory = ChatMemoryBuffer.from_defaults(llm=Settings.llm)

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=document_count,
    )

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
            content="Hello assistant, today we are coding and/or analysing code.  Pay close attention to the context provided when answering each question.",
        ),
        ChatMessage(role=MessageRole.ASSISTANT, content="Okay, sounds good."),
    ]

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        llm=Settings.llm,
        retriever=retriever,
        memory=memory,
        prompt_template=custom_prompt,
        chat_history=custom_chat_history,
        response_streamer=response_streamer,

    )

    st.title("💬 Chatbot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        response = chat_engine.stream_chat(prompt)
        with st.chat_message("assistant"):
            msg = st.write_stream(response.response_gen)

            with st.expander("See context"):

                sources = [s.node.get_text() for s in response.source_nodes]
                st.write(sources)

        st.session_state.messages.append({"role": "assistant", "content": msg})

    