import asyncio
import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tools import kreiraj_ili_zapisi_datoteku, pokreni_lokalnu_naredbu

async def main():
    # Koristimo striktan JSON mode u Ollami kako bismo bili 100% sigurni u format
    llm = ChatOllama(
        model="qwen2.5-coder:7b", 
        temperature=0,
        format="json"  # Ovo prisiljava Ollamu da vrati ČISTI JSON bez čavrljanja
    )
    
    sistemska_uputa = """
    You must output a JSON object specifying a tool execution.
    Format: 
    {
        "name": "name_of_the_tool",
        "arguments": {
            "arg_name": "value"
        }
    }
    Available tools: 'kreiraj_ili_zapisi_datoteku', 'pokreni_lokalnu_naredbu'.
    """

    poruke = [
        SystemMessage(content=sistemska_uputa),
        HumanMessage(content="Spremi tekst 'Hello World' u datoteku pod nazivom test.txt u korijenu projekta")
    ]
    
    print("Saljem upit modelu...")
    odgovor = await llm.ainvoke(poruke)
    
    print("\n--- Odgovor Modela (Sirovi JSON Tekst) ---")
    print(odgovor.content)
    
    # 2. Parsiramo JSON i izvršavamo alat ručno
    try:
        data = json.loads(odgovor.content)
        tool_name = data.get("name")
        args = data.get("arguments", {})
        
        print("\n--- Izvršavanje Alata ---")
        if tool_name == "kreiraj_ili_zapisi_datoteku":
            # Pozivamo našu Python funkciju s argumentima koje je AI odredio
            # Koristimo .invoke() jer je to LangChain standard za pokretanje alata
            rezultat = kreiraj_ili_zapisi_datoteku.invoke(args)
            print(rezultat)
        elif tool_name == "pokreni_lokalnu_naredbu":
            rezultat = pokreni_lokalnu_naredbu.invoke(args)
            print(rezultat)
        else:
            print(f"Model je zatražio nepostojeći alat: {tool_name}")
            
    except json.JSONDecodeError:
        print("Model nije vratio validan JSON.")

if __name__ == "__main__":
    asyncio.run(main())