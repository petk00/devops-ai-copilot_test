import asyncio
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

# 1. Zadržavamo našu strukturu iz Faze 1
class TaskAnalysis(BaseModel):
    category: str = Field(description="Kategorija zadatka (npr. 'docker', 'bug_fix')")
    estimated_difficulty: str = Field(description="Procjena tezine: 'easy', 'medium', 'hard'")
    steps_required: list[str] = Field(description="Lista koraka prilagođena internim pravilima organizacije")
    internal_rules_applied: list[str] = Field(description="Koja su interna pravila iz dokumentacije primijenjena u koracima")

async def analyze_task_with_rag(user_prompt: str):
    # 2. Inicijaliziramo embedding model kako bismo mogli pretraživati Qdrant
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # 3. Spajamo se na postojeću kolekciju u Qdrant-u
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name="devops_knowledge",
        url="http://localhost:6333"
    )
    
    # Pretvaramo bazu u "retriever" (tražilicu) koji vraća top 1 najsličniji komad teksta
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    
    print(f"Pretražujem bazu znanja za: '{user_prompt}'...")
    relevant_docs = await retriever.ainvoke(user_prompt)
    
    # Izvlačimo sirovi tekst iz pronađenih dokumenata
    context = "\n".join([doc.page_content for doc in relevant_docs])
    print(f"Pronađen kontekst u bazi:\n{context}\n")

    # 4. Inicijaliziramo glavni model za razmišljanje
    llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)
    structured_llm = llm.with_structured_output(TaskAnalysis)

    # 5. Kreiramo prompt koji kombinira pronađeno interno znanje i korisnički upit
    full_prompt = f"""
    Koristi isključivo sljedeća interna pravila firme ako su relevantna za zadatak:
    {context}
    
    Zadatak: {user_prompt}
    """
    
    response = await structured_llm.ainvoke(full_prompt)
    
    print("--- REZULTAT NAKON RAG-a ---")
    print(f"Kategorija: {response.category}")
    print(f"Tezina: {response.estimated_difficulty}")
    print("Koraci:")
    for step in response.steps_required:
        print(f" - {step}")
    print("\nPrimijenjena interna pravila:")
    for rule in response.internal_rules_applied:
        print(f" - {rule}")

if __name__ == "__main__":
    test_prompt = "Kreiraj mi Dockerfile za Node.js aplikaciju"
    asyncio.run(analyze_task_with_rag(test_prompt))