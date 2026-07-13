# 🤖 DevOps AI Copilot

doslovno zajebancija i testiranje

DevOps AI Copilot je autonomni AI agent dizajniran za automatizaciju svakodnevnih DevOps zadataka. Projekt koristi **LangGraph** za upravljanje logikom, **Qdrant** kao vektorsku bazu za pretraživanje znanja (RAG), te **Streamlit** za interaktivno web sučelje.

---

## 🚀 Značajke

* **Autonomno odlučivanje:** Agent samostalno planira korake (Reasoning) i izvršava akcije (Acting).
* **RAG (Retrieval-Augmented Generation):** Pretražuje lokalnu dokumentaciju prije donošenja odluka.
* **Lokalni alati:** Sigurno izvršava terminal naredbe i operacije nad datotekama.
* **Interaktivni UI:** Pregledno web sučelje za praćenje "razmišljanja" agenta u stvarnom vremenu.

## 🛠 Tehnologije

* **LLM:** `qwen2.5-coder` (pokrenut putem Ollame)
* **Orkestracija:** LangGraph, LangChain
* **Baza znanja:** Qdrant
* **Frontend:** Streamlit
* **Upravljanje paketima:** uv

---

## 📋 Upute za instalaciju i pokretanje

Slijedite ove korake kako biste podesili projekt na svom lokalnom stroju:

### 1. Kloniranje repozitorija

```bash
git clone https://github.com/tvoj-user/devops-ai-copilot.git
cd devops-ai-copilot
```

### 2. Instalacija ovisnosti

Pobrinite se da imate instaliran `uv` (Python paket menadžer) i instalirajte potrebne knjižnice:

```bash
uv sync
```

### 3. Pokretanje Qdrant baze podataka

Potreban vam je Docker. Pokrenite Qdrant kontejner koji će služiti kao vektorska memorija agenta:

```bash
docker run -d -p 127.0.0.1:6333:6333 -p 127.0.0.1:6334:6334 qdrant/qdrant
```

### 4. Indeksiranje baze znanja (RAG)

Prije nego agent može odgovarati na pitanja, morate učitati podatke u bazu:

```bash
uv run ingest.py
```

### 5. Pokretanje Web sučelja

Pokrenite Streamlit aplikaciju kako biste komunicirali s agentom putem modernog sučelja:

```bash
uv run streamlit run app.py
```

Nakon pokretanja, otvorite adresu `http://localhost:8501` u vašem pregledniku.

---

## 🧠 Kako agent radi?

Agent koristi LangGraph arhitekturu temeljenu na grafu. Nakon što unesete upit u sučelje, proces se odvija kroz sljedeće faze:

1. **Pretraživanje (Dohvati znanje):** Agent provjerava Qdrant bazu za relevantnim informacijama.
2. **Razmišljanje (LLM):** Model analizira kontekst i donosi odluku (koji alat koristiti).
3. **Izvršavanje (Alati):** Agent pokreće odabrani alat (npr. čitanje datoteka, izvršavanje shell naredbi).
4. **Završetak:** Agent samostalno evaluira je li zadatak gotov i daje potvrdu korisniku.

---

## 📝 Planirani razvoj

* [ ] Implementacija "Human-in-the-Loop" sustava za odobravanje kritičnih terminal naredbi.
* [ ] Dodavanje alata za Docker i Kubernetes dijagnostiku.
* [ ] Proširenje RAG baze s više tehničkih specifikacija.

---

*Projekt razvijen kao samostalni DevOps AI inženjerski alat.*
