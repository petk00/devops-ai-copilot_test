import streamlit as st
import asyncio
import json
from agent import app  # Uvozimo tvoj kompajlirani LangGraph agent

st.set_page_config(page_title="DevOps AI Copilot", page_icon="🤖", layout="wide")

st.title("🤖 DevOps AI Copilot")
st.caption("Autonomni agent s pristupom bazi znanja i lokalnim alatima")

# Inicijalizacija povijesti čavrljanja u Streamlit sesiji
if "messages" not in st.session_state:
    st.session_state.messages = []

# Prikaz prethodnih poruka iz povijesti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Korisnički unos
if user_input := st.chat_input("Što želiš da napravim? (npr. Provjeri vrijeme i zapiši u build_info.txt)"):
    
    # Prikaži korisnikov unos na sučelju
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Pokretanje agenta i prikaz njegovog razmišljanja
    with st.chat_message("assistant"):
        st.write("🤖 *Agent se pokreće...*")
        
        # Kontejner u koji ćemo ispisivati tijek rada uživo
        status_placeholder = st.empty()
        
        # Početno stanje za LangGraph graph
        pocetno_stanje = {
            "user_prompt": user_input,
            "context": "",
            "messages": [],
            "iterations": 0,
            "final_output": ""
        }

        # Funkcija koja vrti graf i hvata ispise (stream) kroz čvorove
        async def pokreni_agenta_ui():
            tekst_ispisa = ""
            
            # Pratimo izvršavanje kroz evente grafa
            async for event in app.astream(pocetno_stanje, stream_mode="updates"):
                # Provjeravamo koji čvor je upravo odradio posao
                for node_name, output in event.items():
                    if node_name == "dohvati_znanje":
                        tekst_ispisa += "🔍 *Pretražujem lokalnu bazu znanja...*\n"
                        if output.get("context"):
                            tekst_ispisa += "✅ *Pronašao sam relevantne DevOps upute.*\n\n"
                    
                    elif node_name == "llm_misli":
                        zadnja_poruka = output["messages"][-1]["content"]
                        try:
                            data = json.loads(zadnja_poruka)
                            akcija = data.get("action")
                            
                            if akcija == "call_tool":
                                alat = data.get("name")
                                tekst_ispisa += f"🧠 **Razmišljanje:** Model je odlučio pozvati alat `{alat}`.\n"
                            elif akcija == "complete":
                                tekst_ispisa += f"🏁 **Zadatak završen!** {data.get('summary', '')}\n"
                        except:
                            tekst_ispisa += "🧠 *Model analizira idući korak...*\n"
                            
                    elif node_name == "izvrsi_alat":
                        # Izvlačimo zadnji ispis alata iz povijesti poruka
                        zadnja_poruka = output["messages"][-1]["content"]
                        tekst_ispisa += f"🛠️ **Izvršavanje alata:**\n```text\n{zadnja_poruka}\n```\n\n"
                    
                    # Ažuriraj sučelje u stvarnom vremenu
                    status_placeholder.markdown(tekst_ispisa)
            
            return tekst_ispisa

        # Pokrećemo asinkronu petlju unutar Streamlita
        konacni_rezultat = asyncio.run(pokreni_agenta_ui())
        
        # Spremi odgovor agenta u povijest sesije
        st.session_state.messages.append({"role": "assistant", "content": konacni_rezultat})