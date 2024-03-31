from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.postgres import PGVectorStore

def main():

    
    documents = SimpleDirectoryReader("/app/data", recursive=True).load_data()
    print(documents)

    # bge embedding model
    Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

    # ollama
    Settings.llm = Ollama(model="llama2", request_timeout=30.0)

    index = VectorStoreIndex.from_documents(
        documents,
    )

    query_engine = index.as_query_engine()
    response = query_engine.query("Write some code to animate a square to a circle in manim")
    print(response)

if __name__ == "__main__":
    main()