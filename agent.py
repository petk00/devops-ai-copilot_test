import asyncio
import json
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from tools import kreiraj_ili_zapisi_datoteku, pokreni_lokalnu_naredbu

# 1. Definiramo stanje (State) koje graf prenosi između koraka
class AgentState(TypedDict):
    user_prompt: str
    context: str
    messages: list[dict]
    iterations: int
    final_output: str

# 2. ČVOR 1: Dohvaćanje znanja iz Qdrant RAG baze
async def dohvati_znanje_node(state: AgentState):
    print("\n[AGENT] Pretražujem lokalnu bazu znanja...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name="devops_knowledge",
        url="http://localhost:6333"
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    relevant_docs = await retriever.ainvoke(state["user_prompt"])
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    return {"context": context}

# 3. ČVOR 2: Model donosi odluku o akciji
async def llm_misli_node(state: AgentState):
    print(f"\n[AGENT] LLM razmišlja (Iteracija {state['iterations'] + 1})...")
    llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0, format="json")
    
    sistemski_prompt = f"""
    You are an autonomous DevOps Agent. Your job is to fulfill the user request using available tools.
    
    CRITICAL: To find out the current date and time, you MUST execution the terminal command 'date' first! 
    Do not guess the time, and do not try to write the file before you have the output of the 'date' command.

    If the last message in history shows that 'kreiraj_ili_zapisi_datoteku' was successfully executed, you MUST immediately output:
    {{"action": "complete", "summary": "Successfully fetched date and saved to build_info.txt"}}
    Do not invoke any more tools after the file is created.

    Available tools:
    - 'kreiraj_ili_zapisi_datoteku' (args: putanja, sadrzaj)
    - 'pokreni_lokalnu_naredbu' (args: naredba)

    Strictly follow these internal company rules:
    {state['context']}

    You must output a JSON object with your next action. 
    If you need to use a tool:
    {{"action": "call_tool", "name": "tool_name", "arguments": {{"arg": "val"}}}}
    """
    
    history = [SystemMessage(content=sistemski_prompt)]
    for msg in state["messages"]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(SystemMessage(content=msg["content"]))
            
    history.append(HumanMessage(content=state["user_prompt"]))
    
    odgovor = await llm.ainvoke(history)
    
    # Ispisujemo sirovi odgovor u terminal radi lakšeg debugginga
    print(f"[LOG MODELA]: {odgovor.content}")
    
    nove_poruke = state["messages"] + [{"role": "assistant", "content": odgovor.content}]
    
    return {"messages": nove_poruke, "iterations": state["iterations"] + 1}

# 4. ČVOR 3: Izvršavanje alata na temelju odluke modela
async def izvrsi_alat_node(state: AgentState):
    zadnja_poruka = state["messages"][-1]["content"]
    data = json.loads(zadnja_poruka)
    
    tool_name = data.get("name")
    args = data.get("arguments", {})
    
    print(f"[ALAT] Pokrećem alat '{tool_name}'...")
    
    if tool_name == "kreiraj_ili_zapisi_datoteku":
        rezultat = kreiraj_ili_zapisi_datoteku.invoke(args)
    elif tool_name == "pokreni_lokalnu_naredbu":
        rezultat = pokreni_lokalnu_naredbu.invoke(args)
    else:
        rezultat = f"Greška: Nepoznat alat {tool_name}"
        
    print(f"[ALAT] Rezultat izvršavanja:\n{rezultat}")
    
    # Vraćamo rezultat natrag u povijest kako bi ga LLM vidio u idućem koraku
    nove_poruke = state["messages"] + [{"role": "user", "content": f"Result of tool {tool_name}: {rezultat}"}]
    return {"messages": nove_poruke}

# 5. RUB (Edge): Odlučuje kamo idemo dalje na temelju stanja
def usmjeri_tok(state: AgentState):
    zadnja_poruka = state["messages"][-1]["content"]
    try:
        data = json.loads(zadnja_poruka)
        if data.get("action") == "complete" or state["iterations"] >= 5:
            print("\n[AGENT] Završavam rad (Zadatak dovršen ili postignut limit iteracija).")
            return "kraj"
        return "izvrsi_alat"
    except Exception as e:
        print(f"[GREŠKA PARSIRANJA]: {e}")
        return "kraj"

# --- SASTAVLJANJE GRAFA ---
workflow = StateGraph(AgentState)

# Dodaj čvorove
workflow.add_node("dohvati_znanje", dohvati_znanje_node)
workflow.add_node("llm_misli", llm_misli_node)
workflow.add_node("izvrsi_alat", izvrsi_alat_node)

# Poveži čvorove
workflow.set_entry_point("dohvati_znanje")
workflow.add_edge("dohvati_znanje", "llm_misli")

# Uvjetno grananje nakon razmišljanja modela
workflow.add_conditional_edges(
    "llm_misli",
    usmjeri_tok,
    {
        "izvrsi_alat": "izvrsi_alat",
        "kraj": END
    }
)

# Nakon izvršavanja alata, vraćamo se modelu na ponovno razmišljanje
workflow.add_edge("izvrsi_alat", "llm_misli")

# Kompajliramo LangGraph aplikaciju
app = workflow.compile()

async def pokreni_agenta():
    pocetno_stanje = {
        "user_prompt": "Stvori skriptu pod nazivom 'build_info.txt' i unutra zapiši trenutni datum i vrijeme koristeći terminal naredbu date",
        "context": "",
        "messages": [],
        "iterations": 0,
        "final_output": ""
    }
    
    print("Započinje autonomni agent...")
    await app.ainvoke(pocetno_stanje)

if __name__ == "__main__":
    asyncio.run(pokreni_agenta())