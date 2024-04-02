from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.ollama import OllamaEmbedding
import time
import fastapi
from pydantic import BaseModel


class EmbeddingModel(BaseModel):
    name: str
# Create API that accepts a request to index a directory

app = fastapi.FastAPI()

@app.post("/index")

def index_directory(model: EmbeddingModel):
    documents = SimpleDirectoryReader("/app/data", recursive=True).load_data()
    remote_db = chromadb.HttpClient()
    Settings.embed_model = OllamaEmbedding(model_name=model.name)

    # ollama
    Settings.llm = Ollama(model="llama2", request_timeout=30.0)

    remote_db.delete_collection("quickstart")
    chroma_collection = remote_db.get_or_create_collection("quickstart")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True
    )

    return {"status": "success"}
