# ZENDS TELECOM AI BRAND INTELLIGENCE SYSTEM
## Complete Master Documentation

---

## 1. PROJECT OVERVIEW

**Project Name:** Zends Telecom AI Brand Intelligence System
**Version:** v2.1
**Purpose:** An AI-powered telecom customer intelligence platform that performs real-time sentiment analysis on customer feedback, retrieves relevant policy documents via a RAG (Retrieval-Augmented Generation) system, auto-generates tickets, and provides an analyst dashboard for brand monitoring.

### Business Problem Solved
Telecom companies receive thousands of customer feedback messages daily. Manually reading, categorizing, and responding to each is impossible at scale. This system:
- Auto-classifies customer sentiment (Positive / Neutral / Mixed / Negative)
- Routes negative/mixed feedback to support tickets automatically
- Retrieves relevant policy documents to generate accurate AI responses
- Gives analysts a real-time dashboard of brand health

### Core Objectives
1. **Sentiment Analysis** — Classify customer feedback using a dual-model pipeline (DistilBERT + Groq LLM)
2. **RAG System** — Answer telecom policy questions by retrieving relevant document chunks and generating grounded LLM responses

### End-to-End Workflow
```
Customer submits feedback
        ↓
DistilBERT baseline classification
        ↓
Groq Llama-3.3-70B refines classification + assigns category
        ↓
If Negative/Mixed → auto-generate ticket → persist to live_feedback.json
        ↓
RAG retrieves relevant policy docs → display to customer
        ↓
Analyst dashboard reads live_feedback.json → display KPIs + charts
```

---

## 2. TECH STACK

### Frontend
| Technology | Version | Role |
|---|---|---|
| Streamlit | latest | Full UI framework for both customer portal and analyst dashboard |
| Plotly | latest | Interactive charts (line, donut, heatmap, scatter, bar) |
| HTML/CSS (inline) | N/A | Custom glassmorphism UI with CSS variables for dark/light themes |
| Google Fonts | N/A | IBM Plex Sans + Mono (dashboard), Sora + JetBrains Mono (portal) |

### Backend
| Technology | Version | Role |
|---|---|---|
| FastAPI | latest | REST API server exposing RAG endpoints |
| Uvicorn | latest | ASGI server running FastAPI |
| Python | 3.10+ | Core language |
| python-multipart | latest | Handles file uploads in FastAPI |

### AI / ML
| Technology | Version | Role |
|---|---|---|
| Groq SDK | latest | Cloud LLM inference API client |
| Llama-3.3-70b-versatile | N/A | Primary LLM for sentiment refinement + RAG response generation |
| Llama-3.1-8b-instant | N/A | Lightweight LLM used for hallucination grading |
| DistilBERT (distilbert-base-uncased-finetuned-sst-2-english) | N/A | Baseline sentiment classifier (Hugging Face Transformers) |
| sentence-transformers | latest | Embedding model wrapper |
| all-MiniLM-L6-v2 | N/A | Embedding model for document vectorization (384-dim) |
| LangGraph | latest | State machine orchestration of the RAG pipeline |
| LlamaIndex | latest | Document indexing, vector store management, retrieval |
| langchain-text-splitters | latest | RecursiveCharacterTextSplitter for chunking |
| rank_bm25 | latest | BM25 sparse retrieval for hybrid search |
| llama-index-retrievers-bm25 | latest | LlamaIndex BM25 retriever wrapper |

### Vector Database
| Technology | Role |
|---|---|
| FAISS (faiss-cpu) | Primary vector index stored in `storage_v2/` via LlamaIndex |
| LlamaIndex VectorStoreIndex | Manages FAISS index + docstore persistence |

### Databases
| Technology | Role |
|---|---|
| PostgreSQL | Primary production DB — stores users and query_logs |
| SQLite | Legacy/dev DB in `database/users.db` — stores users + api_keys |

### Libraries
| Package | Role |
|---|---|
| psycopg2-binary | PostgreSQL driver |
| SQLAlchemy | ORM (imported, available for future use) |
| pymupdf (fitz) | PDF text extraction |
| passlib[bcrypt] | Password hashing |
| python-jose[cryptography] | JWT token generation |
| python-dotenv | .env file loading |
| numpy | Numerical operations for embeddings |
| pandas | DataFrame operations in the dashboard |
| requests | HTTP calls from Streamlit to FastAPI |
| huggingface_hub | HuggingFace model downloads |

---

## 3. FOLDER STRUCTURE

```
Zends/
├── project_root/                  ← MAIN APPLICATION ROOT
│   ├── api.py                     ← FastAPI backend (entry point 1)
│   ├── streamlit_app.py           ← Streamlit router (entry point 2)
│   ├── locales.py                 ← i18n translation strings (EN/ES/FR)
│   ├── requirements.txt           ← All Python dependencies
│   ├── .env                       ← API keys + DB credentials
│   ├── Zend data.ipynb            ← Training/EDA notebook
│   ├── telecom_feedback_dataset.csv ← Training dataset
│   ├── vector_index.faiss         ← Legacy FAISS index (flat)
│   ├── chunks.pkl                 ← Serialized chunk metadata
│   ├── src/
│   │   ├── __init__.py
│   │   ├── rag_system.py          ← Core RAG + LangGraph pipeline
│   │   ├── contract_parser.py     ← PDF extraction + chunking
│   │   ├── embeddings.py          ← Embedding utility (fallback)
│   │   ├── vector_store.py        ← Legacy FAISS index management
│   │   ├── db.py                  ← PostgreSQL helpers
│   │   ├── faiss_index.bin        ← Embedded FAISS binary
│   │   └── faiss_index.pkl        ← Embedded FAISS metadata
│   ├── data/
│   │   ├── live_feedback.json     ← Real-time feedback feed (shared state)
│   │   ├── fixed_extracted_text.txt ← Default RAG knowledge base text
│   │   └── uploads/               ← User-uploaded PDFs/TXTs
│   ├── storage_v2/                ← LlamaIndex persisted vector store
│   ├── database/
│   │   └── db.py                  ← SQLite helper (dev/legacy)
│   ├── results/
│   │   ├── checkpoint-500/        ← DistilBERT fine-tuning checkpoint
│   │   ├── checkpoint-1000/       ← DistilBERT fine-tuning checkpoint
│   │   └── checkpoint-1500/       ← DistilBERT fine-tuning checkpoint
│   └── tests/
├── analyst_dashboard.py           ← Analyst UI (loaded by streamlit_app.py)
├── customer_ui.py                 ← Customer Portal UI
├── rag_management.py              ← Standalone RAG management UI
├── merge_ui.py                    ← Merge utility
└── .gitignore
```

---

## 4. SENTIMENT ANALYSIS SYSTEM

### Dual-Model Pipeline Architecture

The system uses a **two-stage hybrid pipeline**:

#### Stage 1 — DistilBERT Baseline
- **Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Source:** Hugging Face Transformers `pipeline("sentiment-analysis")`
- **Output:** Binary label (POSITIVE/NEGATIVE) + confidence score
- **Role:** Provides a fast, lightweight initial signal
- **Limitation:** Binary only — cannot detect Neutral or Mixed sentiments

#### Stage 2 — Groq Llama-3.3-70B Refinement
- **Model:** `llama-3.3-70b-versatile` via Groq API
- **Role:** Overrides DistilBERT with nuanced, context-aware classification
- **Output:** 4-class label + category + confidence + reasoning
- **Temperature:** 0.0 (fully deterministic)
- **Response format:** Enforced JSON object

### Prompt Engineering Strategy
The Groq prompt implements **Aspect-Based Sentiment Analysis (ABSA)**:
```
- Sentiment must be one of: [Positive, Negative, Neutral, Mixed]
- Only evaluate sentiment toward ZENDS Communications
- Ignore anger at external factors (weather, user error, pets)
- Do NOT fall for the "Conjunction Trap" (but/however ≠ always Mixed)
- Few-shot examples are embedded to demonstrate edge cases
- DistilBERT result is passed as context for the LLM to consider
```

### Classification Labels
| Label | Meaning |
|---|---|
| Positive | Customer is happy with ZENDS services |
| Negative | Customer is dissatisfied with ZENDS services |
| Neutral | No strong opinion expressed toward ZENDS |
| Mixed | Both positive and negative aspects toward ZENDS |

### Full Lifecycle
```
feedback_text
    → DistilBERT → bert_label, bert_score
    → Groq Prompt (includes bert_label as context)
    → JSON response: {sentiment, category, confidence, reasoning}
    → if Negative/Mixed → generate ticket_id (TCK-XXXXXX)
    → persist to live_feedback.json
    → display result + RAG docs to customer
```

### Category Routing
8 categories auto-detected by the LLM:
- Network Connectivity, Billing & Payments, Data Services
- Roaming & International, Customer Support, Device & SIM
- Plan & Subscription, Voice & Calls

### Training Background
- **Dataset:** `telecom_feedback_dataset.csv` — telecom-specific customer feedback
- **Fine-tuning:** DistilBERT fine-tuned in `Zend data.ipynb` with 3 checkpoints saved (500, 1000, 1500 steps)
- **Note:** The production system uses the Groq LLM as the primary classifier; DistilBERT provides a baseline signal only

---

## 5. RAG SYSTEM ANALYSIS

### Architecture: LangGraph State Machine

The RAG system is implemented as a **directed acyclic graph** using LangGraph with retry logic and hallucination grading.

### LangGraph Nodes

```
[startup] → [retrieve] → [generate] → {conditional}
                ↑              ↓
           (retry)      [hallucination_grader]
                              ↓
                    confidence > 60% + grounded?
                    YES → [log_results] → END
                    NO  → retry (max 2) or [fallback] → [log_results] → END
```

### Node Descriptions

| Node | File | Function |
|---|---|---|
| startup | rag_system.py | Loads or builds LlamaIndex VectorStoreIndex from storage_v2/ |
| retrieve | rag_system.py | Hybrid search: Vector (top-5) + BM25 (top-5) + RRF fusion |
| generate | rag_system.py | Calls Groq Llama-3.3-70B with context + strict system prompt |
| hallucination_grader | rag_system.py | Calls Groq Llama-3.1-8B-instant to score groundedness (0-100) |
| log_results | rag_system.py | Persists query + response to PostgreSQL query_logs table |
| fallback | rag_system.py | Returns escalation message + simulates regional queue routing |

### GraphState (TypedDict)
```python
{
  "question": str,
  "context": str,
  "response": str,
  "retry_count": int,
  "confidence_score": int,
  "username": str
}
```

### Document Ingestion Pipeline
```
PDF/TXT file uploaded
    → extract_text_from_pdf() [PyMuPDF/fitz]
    → chunk_text() [RecursiveCharacterTextSplitter]
         chunk_size=1000, overlap=150
         separators=["\n\n", "\n", ". ", " ", ""]
    → TextNode objects created
    → VectorStoreIndex.insert_nodes() [LlamaIndex]
         embed_model=all-MiniLM-L6-v2 (384-dim)
         chunk_size=256, overlap=50 (MiniLM limit)
    → Persisted to storage_v2/
```

### Hybrid Retrieval — Reciprocal Rank Fusion (RRF)
```
Query
  → Vector Retriever (top-5) — semantic similarity via FAISS
  → BM25 Retriever (top-5) — lexical/keyword match
  → RRF Fusion: score = Σ 1/(rank + 1 + 60)
  → Top-5 fused nodes selected
  → Context = "\n\n".join(node.get_text() for node in top5)
```

**RRF constant c=60** prevents over-weighting of top ranks.

### Embedding Model
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Loaded via:** `HuggingFaceEmbedding` (LlamaIndex wrapper)
- **Cached globally** in `Settings.embed_model`

### Hallucination Grading
- **Model:** `llama-3.1-8b-instant` (fast, low-cost)
- **Input:** FACTS (retrieved context) + GENERATION (LLM response)
- **Output:** `{"score": 0-100, "grounded": "yes"/"no"}`
- **Threshold:** score > 60 AND grounded == "yes" → proceed to log
- **Retry limit:** 2 retries before fallback

### RAG Query Flow (Full)
```
POST /ask {question, username}
    → rag_app.stream(inputs) [LangGraph]
    → startup: load index from storage_v2/
    → retrieve: hybrid search → context string
    → generate: Groq Llama-3.3-70B → response
    → decide_to_finish():
        if "i don't know" → fallback
        else → hallucination_grader_with_score()
            if grounded + score>60 → log_results → END
            elif retries<2 → retrieve again
            else → fallback → log_results → END
    → return {answer, confidence, context, status}
```

---

## 6. DATABASE & DATA FLOW

### PostgreSQL Schema (Production — src/db.py)

#### Table: users
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PRIMARY KEY | Auto-increment |
| username | TEXT UNIQUE NOT NULL | Unique login |
| password | TEXT NOT NULL | Should be bcrypt hash |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP |

#### Table: query_logs
| Column | Type | Notes |
|---|---|---|
| id | SERIAL PRIMARY KEY | Auto-increment |
| username | TEXT NOT NULL | Who made the query |
| query | TEXT NOT NULL | User's question |
| response | TEXT | LLM-generated answer |
| timestamp | TIMESTAMP | Default CURRENT_TIMESTAMP |

### SQLite Schema (Dev/Legacy — database/db.py)

#### Table: users
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | |
| username | TEXT NOT NULL UNIQUE | |
| api_key | TEXT NOT NULL | API key (not hashed password) |

### JSON Flat File: live_feedback.json
Used as **shared state** between Customer UI and Analyst Dashboard.

```json
{
  "id": "TCK-XXXXXX or FB-XXXXX",
  "timestamp": "ISO datetime",
  "category": "Network Connectivity",
  "sentiment": "Negative",
  "feedback": "customer text",
  "confidence": 99,
  "status": "Pending | Resolved | No Action"
}
```

- Written by `customer_ui.py` on feedback submission
- Read by `analyst_dashboard.py` for KPI cards + live feed
- Max 50 entries retained (FIFO)

---

## 7. API ANALYSIS

### Base URL: http://127.0.0.1:8000

| Method | Endpoint | Description |
|---|---|---|
| POST | /register | Register new user |
| POST | /login | Verify credentials |
| POST | /upload | Upload + ingest single document |
| POST | /upload-batch | Upload + ingest multiple documents |
| POST | /ask | Query the RAG pipeline |
| GET | /documents | List uploaded documents |
| DELETE | /documents/{filename} | Delete doc + rebuild index |
| GET | /health | Health check |

### Request/Response Details

#### POST /ask
```json
Request:  {"question": "string", "username": "anonymous"}
Response: {"answer": "string", "confidence": 85, "context": "string", "status": "success"}
```

#### POST /upload
```
Request:  multipart/form-data, file field
Response: {"message": "Successfully uploaded and indexed filename.pdf"}
```

#### POST /register
```json
Request:  {"username": "string", "password": "string"}
Response: {"message": "User registered successfully."}
```

### Middleware & Error Handling
- FastAPI auto-validates Pydantic models
- `HTTPException` with appropriate status codes (400, 401, 404, 500)
- File overwrite detection with warning in response
- Exception catching in all endpoints with 500 responses

---

## 8. STREAMLIT APPLICATION ARCHITECTURE

### Entry Point: streamlit_app.py

Acts as a **router** that:
1. Sets global page config (once only)
2. Manages language selection (English / Español / Français)
3. Manages dark/light theme toggle
4. Dynamically `exec()`s either `analyst_dashboard.py` or `customer_ui.py`
5. Strips duplicate `st.set_page_config()` calls from sub-modules via regex

### customer_ui.py — Customer Portal
Two tabs:
1. **💬 Customer Portal** — FAQ, feedback form, sentiment result, RAG docs display
2. **⚙️ RAG Document Management** — Upload/delete docs, test RAG queries

Key flows:
- Calls `analyze_feedback()` → dual-model sentiment pipeline
- Calls `get_rag_docs(category)` → static policy lookup (not RAG API)
- Calls `http://127.0.0.1:8000/upload` for document uploads
- Calls `http://127.0.0.1:8000/ask` for RAG test queries
- Writes results to `data/live_feedback.json`

### analyst_dashboard.py — Analyst Dashboard
Four tabs:
1. **📈 Sentiment Trends** — Line chart + donut chart + weekly heatmap
2. **📂 Category Analysis** — Stacked bar + horizontal bar + summary table
3. **🔴 Live Feed** — Real-time feedback from live_feedback.json + volume spike chart
4. **🤖 AI Recommendations** — Static insights + Effort vs Impact scatter matrix

Data: Partially synthetic (pandas DataFrames with `random.seed(42)`) + live data from `live_feedback.json`

---

## 9. INTERNATIONALIZATION (i18n)

### locales.py
Supports 3 languages: English, Español, Français

```python
t("btn_analyze", lang)  # Returns language-specific button label
```

Used in: `streamlit_app.py`, `customer_ui.py`
Translation keys include: nav labels, button text, placeholders, AI response headers

---

## 10. DEPENDENCY REPORT

| Package | Purpose | Used In |
|---|---|---|
| streamlit | UI framework | streamlit_app.py, customer_ui.py, analyst_dashboard.py |
| fastapi | REST API | api.py |
| uvicorn[standard] | ASGI server | Runs api.py |
| groq | Groq LLM API client | rag_system.py, customer_ui.py |
| langgraph | RAG state machine | rag_system.py |
| llama-index | Vector indexing + retrieval | rag_system.py |
| llama-index-embeddings-huggingface | HuggingFace embed model | rag_system.py |
| sentence-transformers | Embedding + vector_store.py | vector_store.py, rag_system.py |
| faiss-cpu | Vector similarity search | vector_store.py, storage_v2/ |
| langchain-text-splitters | Text chunking | contract_parser.py |
| pymupdf | PDF text extraction | contract_parser.py |
| rank_bm25 | BM25 sparse retrieval | rag_system.py |
| llama-index-retrievers-bm25 | BM25 retriever wrapper | rag_system.py |
| psycopg2-binary | PostgreSQL driver | src/db.py |
| SQLAlchemy | ORM (available) | imported |
| passlib[bcrypt] | Password hashing | auth (available) |
| python-jose[cryptography] | JWT tokens | auth (available) |
| python-dotenv | .env loading | all modules |
| python-multipart | File upload parsing | api.py |
| plotly | Charts | analyst_dashboard.py |
| pandas | DataFrames | analyst_dashboard.py |
| numpy | Numerical ops | embeddings.py, rag_system.py |
| requests | HTTP client | customer_ui.py |
| huggingface_hub | Model downloads | embedding model |
| openai | Listed in requirements (legacy) | N/A |

---

## 11. INTERVIEW PREPARATION

### "Explain your project in 2 minutes"
> This is a Telecom AI Brand Intelligence System built for a fictional telecom company called ZENDS Communications. The system has two main AI engines: a Sentiment Analysis pipeline and a RAG system. When a customer submits feedback, it runs through DistilBERT for a baseline sentiment signal, then Groq's Llama-3.3-70B model refines it with aspect-based analysis, avoids common classification traps, assigns the correct category, and generates a confidence score. If the feedback is negative or mixed, a support ticket is automatically created. The analyst dashboard reads this data in real-time and shows KPIs, trend charts, and AI-generated recommendations. The RAG system uses LangGraph as a state machine that orchestrates document retrieval, LLM generation, hallucination grading, and database logging. It uses a hybrid retrieval strategy combining FAISS vector search with BM25 sparse search via Reciprocal Rank Fusion.

### "Why did you choose this architecture?"
> LangGraph was chosen over a simple chain because the RAG pipeline needed retry logic and conditional routing — if the LLM produces a low-confidence or hallucinated response, the graph loops back to retrieval. FastAPI decouples the backend from the frontend, allowing the Streamlit UI to call REST APIs independently. Groq was chosen for its extremely low inference latency. The dual-model sentiment approach (DistilBERT + LLM) gives both speed and nuance — the BERT model is fast but binary, while the LLM provides 4-class classification with reasoning.

### "What challenges did you face?"
> 1. **Conjunction Trap in Sentiment** — "I love the speed but customer service is terrible" was being classified as Mixed when the user only complained about one aspect. Solved with explicit few-shot examples and aspect-based rules in the prompt.
> 2. **BM25 Installation at Runtime** — BM25 packages aren't always installed; added dynamic subprocess pip install with fallback dummy class.
> 3. **MiniLM Token Truncation** — The all-MiniLM-L6-v2 model has a 256-token limit. Set chunk_size=256 and chunk_overlap=50 in LlamaIndex Settings.
> 4. **Shared State** — The analyst dashboard needed to see customer feedback in real-time. Used a JSON flat file (live_feedback.json) as the shared state between Streamlit pages since Streamlit session_state doesn't persist across processes.
> 5. **Duplicate st.set_page_config** — When exec()ing sub-modules, the page config call would throw DuplicateError. Solved with a regex strip in streamlit_app.py.

### "How does your RAG work?"
> When a user asks a question via /ask, LangGraph starts at the startup node which loads the persisted LlamaIndex VectorStoreIndex from storage_v2/. The retrieve node runs two searches: FAISS vector search for semantic similarity and BM25 for keyword matching, then merges results using Reciprocal Rank Fusion. The top-5 chunks are concatenated as context. The generate node sends this context with a strict system prompt to Groq's Llama-3.3-70B. A conditional router then checks if the answer is grounded — it calls Llama-3.1-8B-instant as a judge to score the response against the facts. If confidence > 60% and grounded, it logs the query to PostgreSQL and returns the answer. Otherwise it retries up to 2 times, then falls back to a human escalation message.

### "How does your sentiment analysis work?"
> The pipeline is a dual-model hybrid. First, DistilBERT (distilbert-base-uncased-finetuned-sst-2-english) runs locally via Hugging Face Transformers and gives a binary Positive/Negative signal with a confidence score. This result is then passed to Groq's Llama-3.3-70B model as additional context. The LLM performs aspect-based sentiment analysis focused specifically on ZENDS Communications — it ignores external frustrations, identifies the correct category from 8 options, and outputs one of four labels: Positive, Neutral, Mixed, or Negative. The model is instructed at temperature 0.0 to be fully deterministic and must respond in strict JSON format.

### "Future improvements?"
> 1. Add JWT authentication to protect the /ask and /upload endpoints
> 2. Replace live_feedback.json with a PostgreSQL table for proper persistence and concurrency
> 3. Add streaming LLM responses for real-time typewriter effect
> 4. Implement proper bcrypt password hashing (currently stored as plaintext)
> 5. Add Redis caching for repeated RAG queries
> 6. Deploy via Docker + cloud (AWS/GCP) with CI/CD pipeline
> 7. Add multi-turn conversation memory to the RAG system
> 8. Replace synthetic dashboard data with real PostgreSQL aggregations

---

## 12. SYSTEM DESIGN EVALUATION

### Strengths
- ✅ Clean separation of concerns (API / UI / AI / DB layers)
- ✅ LangGraph state machine enables robust retry + fallback logic
- ✅ Hybrid retrieval (vector + BM25 + RRF) is production-grade
- ✅ Dual-model sentiment is more accurate than single-model
- ✅ Aspect-based prompting prevents common classification errors
- ✅ Live feedback JSON enables real-time cross-page data sharing

### Weaknesses & Security Issues
| Issue | Severity | Fix |
|---|---|---|
| Passwords stored in plaintext (src/db.py) | HIGH | Use passlib bcrypt hashing |
| GROQ_API_KEY committed to .env (now in git?) | HIGH | Use secret manager |
| No authentication on /ask and /upload | HIGH | Add JWT middleware |
| live_feedback.json has no concurrency control | MEDIUM | Use PostgreSQL |
| dynamic pip install in rag_system.py at runtime | MEDIUM | Pre-install all dependencies |
| exec() in streamlit_app.py | LOW | Use importlib instead |
| Synthetic data in analyst dashboard | LOW | Connect to real DB |

### Scalability Assessment
- **Current:** Single-instance, single-process, file-based state → suitable for demo
- **Production:** Needs: load balancer, PostgreSQL connection pool, Redis cache, async LLM calls, Docker containerization

### Performance Bottlenecks
1. MiniLM embedding model loads on cold start (~2-3 seconds)
2. DistilBERT loads on first feedback submission (cold start)
3. Two Groq API calls per RAG query (generate + grade)
4. LlamaIndex reloads from disk on every request

---

## 13. ARCHITECTURE DIAGRAM (Text)

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT APPLICATION                      │
│  ┌──────────────────────┐  ┌───────────────────────────────┐ │
│  │   customer_ui.py     │  │   analyst_dashboard.py        │ │
│  │  - FAQ Panel         │  │  - KPI Cards (6)              │ │
│  │  - Feedback Form     │  │  - Sentiment Trend Charts     │ │
│  │  - Sentiment Result  │  │  - Category Analysis          │ │
│  │  - RAG Doc Display   │  │  - Live Feed                  │ │
│  │  - RAG Mgmt Tab      │  │  - AI Recommendations         │ │
│  └──────────┬───────────┘  └──────────────────┬────────────┘ │
└─────────────┼────────────────────────────────┼──────────────┘
              │ HTTP REST                       │ reads
              ↓                                ↓
┌─────────────────────────┐     ┌──────────────────────────┐
│     FastAPI (api.py)    │     │  live_feedback.json      │
│  /ask  /upload /docs    │     │  (shared flat-file state)│
│  /register  /login      │     └──────────────────────────┘
└──────────┬──────────────┘
           │
           ↓
┌──────────────────────────────────────────────────────────┐
│              LangGraph RAG Pipeline (rag_system.py)       │
│                                                           │
│  startup → retrieve → generate → [grade] → log / retry   │
│                                                           │
│  LlamaIndex VectorStoreIndex (storage_v2/)               │
│  + FAISS vector search (top-5)                            │
│  + BM25 sparse search (top-5)                             │
│  + RRF fusion → top-5 context chunks                     │
│                                                           │
│  Groq Llama-3.3-70B → generate response                  │
│  Groq Llama-3.1-8B  → grade hallucination                │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │  PostgreSQL Database   │
              │  - users table         │
              │  - query_logs table    │
              └────────────────────────┘

Embedding Model: all-MiniLM-L6-v2 (384-dim)
Document Parser: PyMuPDF + RecursiveCharacterTextSplitter
Sentiment: DistilBERT → Groq Llama-3.3-70B (ABSA)
```

---

*Documentation generated from codebase analysis — May 2026*
*System: ZENDS Telecom AI Brand Intelligence v2.1*
