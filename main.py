import asyncio
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

# 1. Definiramo strukturu (shemu) koju ŽELIMO od modela (kao TypeScript interface)
class TaskAnalysis(BaseModel):
    category: str = Field(description="Kategorija zadatka (npr. 'docker', 'bug_fix', 'documentation')")
    estimated_difficulty: str = Field(description="Procjena tezine: 'easy', 'medium', 'hard'")
    steps_required: list[str] = Field(description="Lista koraka potrebnih za izvrsavanje zadatka")

async def analyze_task(user_prompt: str):
    # 2. Inicijaliziramo lokalni model preko Ollame
    llm = ChatOllama(
        model="qwen3.6:latest",
        temperature=0,  # 0 znaci deterministicki, precizan odgovor bez kreativnosti
    )

    # 3. Prisiljavamo model da mapira svoj odgovor u nasu Pydantic shemu
    structured_llm = llm.with_structured_output(TaskAnalysis)

    print(f"Slanje zadatka modelu: '{user_prompt}'...\n")
    
    # 4. Asinkroni poziv prema lokalnom modelu
    response = await structured_llm.ainvoke(user_prompt)
    
    # Rezultat nije obican tekst, nego pravi Python objekt tipa TaskAnalysis
    print("--- REZULTAT OD AI MODELA (Strukturirani JSON) ---")
    print(f"Kategorija: {response.category}")
    print(f"Tezina: {response.estimated_difficulty}")
    print("Koraci:")
    for step in response.steps_required:
        print(f" - {step}")

if __name__ == "__main__":
    # Pokretanje asinkrone glavne funkcije
    test_prompt = "Kreiraj mi Dockerfile za Node.js aplikaciju i provjeri radi li build"
    asyncio.run(analyze_task(test_prompt))