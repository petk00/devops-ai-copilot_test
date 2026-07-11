import asyncio
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

async def main():
    # 1. Učitaj lokalnu dokumentaciju
    loader = TextLoader("docs/interne_upute.md")
    documents = loader.load()

    # 2. Razreži dokument na manje komade (chunks)
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)

    # 3. Inicijaliziraj namjenski lokalni embedding model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # 4. Spoji se na lokalni Qdrant u Dockeru i spremi vektore
    print("Indeksiram dokumentaciju u Qdrant vektorsku bazu...")
    
    QdrantVectorStore.from_documents(
        docs,
        embeddings,
        url="http://localhost:6333",
        collection_name="devops_knowledge",
    )
    
    print("Uspješno spremljeno! Tvoj Copilot sada ima bazu znanja.")

if __name__ == "__main__":
    asyncio.run(main())