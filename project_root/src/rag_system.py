# src/rag_system.py
"""Core RAG system implementation.

This module connects the PDF/text ingestion pipeline using LlamaIndex,
and orchestrates the flow using LangGraph for a state-machine based RAG approach.
"""

import os
import re
from pathlib import Path
from typing import List, TypedDict

import numpy as np
import subprocess
import sys
import os

# Dynamically install required BM25 packages if they are missing
try:
    import rank_bm25
    from llama_index.retrievers.bm25 import BM25Retriever
except ImportError:
    try:
        print("Installing required BM25 packages for Hybrid Search...")
        python_exe = sys.executable
        if 'uvicorn' in python_exe.lower():
            python_exe = os.path.join(os.path.dirname(python_exe), 'python.exe')
        subprocess.check_call([python_exe, "-m", "pip", "install", "llama-index-retrievers-bm25", "rank_bm25"])
        import rank_bm25
        from llama_index.retrievers.bm25 import BM25Retriever
    except Exception as e:
        print(f"Failed to install BM25 dependencies: {e}. Hybrid search will be disabled.")
        # Fallback dummy class to prevent NameError later
        class BM25Retriever:
            @classmethod
            def from_defaults(cls, *args, **kwargs):
                raise ImportError("BM25 packages are missing.")

# Load environment variables (e.g., GROQ_API_KEY) from a .env file if present
from dotenv import load_dotenv
load_dotenv(override=True)

from langgraph.graph import StateGraph, END
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from groq import Groq
from pydantic import BaseModel, Field

# Fix Chunk Size for MiniLM to prevent truncation
Settings.chunk_size = 256
Settings.chunk_overlap = 50

# Set up the embedding model (all-MiniLM-L6-v2)
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = embed_model

class GraphState(TypedDict):
    question: str
    context: str
    response: str
    retry_count: int
    confidence_score: int
    username: str

# Local utilities – handle imports for both package and script execution
try:
    from .embeddings import embed_texts  # retained for possible fallback use
    from .vector_store import create_or_update_index, query_faiss
except ImportError:
    from src.embeddings import embed_texts
    from src.vector_store import create_or_update_index, query_faiss

# Path to a default data file (can be replaced by user‑provided documents)
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "fixed_extracted_text.txt"

def ingest_uploaded_file(file_path: Path):
    """Helper for API to ingest newly uploaded files into the existing index."""
    storage_dir = "./storage_v2"
    
    try:
        from .contract_parser import extract_text_from_pdf, chunk_text
    except ImportError:
        from src.contract_parser import extract_text_from_pdf, chunk_text
        
    if file_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        text = file_path.read_text(encoding="utf-8")
        
    chunks = chunk_text(text)
    from llama_index.core.schema import TextNode
    nodes = [TextNode(text=chunk) for chunk in chunks]
    
    if not os.path.exists(storage_dir):
        index = VectorStoreIndex(nodes, embed_model=embed_model)
        index.storage_context.persist(persist_dir=storage_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        index.insert_nodes(nodes)
        index.storage_context.persist(persist_dir=storage_dir)

def startup_and_ingest(state: GraphState):
    print("--- STEP: STARTUP & INGESTION ---")
    storage_dir = "./storage_v2"
    
    if not os.path.exists(storage_dir):
        # Ingest default data if index is missing
        try:
            from .contract_parser import chunk_text
        except ImportError:
            from src.contract_parser import chunk_text
            
        text = DATA_PATH.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        from llama_index.core.schema import TextNode
        nodes = [TextNode(text=chunk) for chunk in chunks]
        
        index = VectorStoreIndex(nodes, embed_model=embed_model)
        index.storage_context.persist(persist_dir=storage_dir)
    else:
        # Load existing FAISS/Vector index
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
    
    return {"question": state["question"]}

def retrieve(state: GraphState):
    print("--- STEP: RETRIEVAL ---")
    storage_dir = "./storage_v2"
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context, embed_model=embed_model)
    
    # 1. Vector Search
    vector_retriever = index.as_retriever(similarity_top_k=5)
    
    # 2. BM25 Sparse Search (Lexical)
    # Get nodes from the docstore to build the BM25 index
    nodes = list(storage_context.docstore.docs.values())
    try:
        bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5)
        
        # 3. Hybrid Retrieval with Manual Reciprocal Rank Fusion (RRF)
        vector_results = vector_retriever.retrieve(state["question"])
        bm25_results = bm25_retriever.retrieve(state["question"])
        
        rrf_scores = {}
        node_map = {}
        c = 60
        
        for results in [vector_results, bm25_results]:
            for rank, node_with_score in enumerate(results):
                node_id = node_with_score.node.node_id
                if node_id not in rrf_scores:
                    rrf_scores[node_id] = 0.0
                    node_map[node_id] = node_with_score
                rrf_scores[node_id] += 1.0 / (rank + 1 + c)
                
        sorted_node_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        retrieved_nodes = [node_map[nid] for nid in sorted_node_ids[:5]]
        
    except Exception as e:
        print(f"Hybrid search failed, falling back to vector search: {e}")
        retrieved_nodes = vector_retriever.retrieve(state["question"])
    
    # Concatenate retrieved chunks into context_text
    context = "\n\n".join([node.get_text() for node in retrieved_nodes])
    retries = state.get("retry_count", 0)
    return {"context": context, "retry_count": retries + 1}

def generate(state: GraphState):
    print("--- STEP: GENERATE RESPONSE ---")
    # Dynamically reload environment variables to ensure the latest API key is used
    from dotenv import load_dotenv
    load_dotenv(override=True)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Build Prompt
    system_prompt = (
        "You are an expert AI assistant for a telecom company. Answer the user's inquiry accurately "
        "using ONLY the provided context.\n"
        "IMPORTANT RULES:\n"
        "1. Be concise and direct. Provide a single, unified answer.\n"
        "2. Do NOT just summarize every section where a topic is mentioned. Instead, synthesize the core rules or definitions into a cohesive response.\n"
        "3. Do NOT say 'According to section X' or 'Context mentions...' unless explicitly asked for references.\n"
        "4. If the user just provides a keyword (e.g., 'Access control'), provide a brief, comprehensive summary of the policy regarding that keyword.\n"
        "5. If the user's question is vague (e.g., 'how much is the cost'), but the context contains pricing or relevant info, list the relevant options found in the context instead of saying you don't know.\n"
        "6. ONLY if the context is completely irrelevant to the query, reply exactly with 'I don't know'.\n\n"
        f"CONTEXT:\n{state['context']}"
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": state["question"]}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )
    
    response = chat_completion.choices[0].message.content
    return {"response": response}

try:
    from . import db
except ImportError:
    import db

def log_transaction(state: GraphState):
    print("--- STEP: LOGGING TO DATABASE ---")
    
    # Extract data from state
    user_query = state["question"]
    final_response = state["response"]
    
    # Using 'username' to match the parameter in db.py
    username = state.get("username", "anonymous")
    db.log_query(username=username, query=user_query, response=final_response)
    
    return state # Pass through state unchanged
# 1. Define the Grader Schema
class GradeHallucination(BaseModel):
    """Binary score for hallucination check."""
    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# 2. Define the Hallucination Grader Node with Score
def hallucination_grader_with_score(state: GraphState):
    print("--- STEP: GRADING CONFIDENCE ---")
    # Dynamically reload environment variables to ensure the latest API key is used
    from dotenv import load_dotenv
    load_dotenv(override=True)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    import json
    
    grading_prompt = (
        "You are an expert auditor. Compare the GENERATION against the FACTS provided. "
        "Even if the GENERATION uses different wording or synonyms, evaluate if the core meaning is supported by the FACTS. "
        "Output a valid JSON object with exactly two keys:\n"
        "1. 'score': an integer between 0 and 100 representing confidence in the accuracy.\n"
        "2. 'grounded': a string 'yes' or 'no' representing if the claim is supported by the facts.\n"
        f"\n\nFACTS: {state['context']}\n\nGENERATION: {state['response']}"
    )
    
    completion = client.chat.completions.create(
            messages=[{"role": "system", "content": grading_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0,
            response_format={"type": "json_object"}
        )
    
    result = completion.choices[0].message.content
    
    try:
        parsed = json.loads(result)
        confidence = int(parsed.get("score", 0))
        grounded = "yes" in str(parsed.get("grounded", "no")).lower()
    except Exception as e:
        print(f"Failed to parse JSON grader output: {e}")
        confidence = 0
        grounded = False

    return {"confidence_score": confidence, "is_grounded": grounded}

# 3. Conditional Routing Function
def decide_to_finish(state: GraphState):
    response_lower = state.get("response", "").lower()
    
    # 1. Primary Rule: No Answer -> No Guessing
    # We tighten the string check so it doesn't discard partial answers
    if response_lower.startswith("i don't know") or response_lower.startswith("sorry"):
        print("--- NO ANSWER FOUND: TRIGGERING FALLBACK ---")
        return "fallback"
        
    grade_result = hallucination_grader_with_score(state)
    
    # Update state with the confidence score
    state["confidence_score"] = grade_result["confidence_score"]
    
    if grade_result["is_grounded"] and state["confidence_score"] > 60:
        return "log_results" # Proceed to DB logging
    else:
        # Check retries to avoid infinite loops
        retries = state.get("retry_count", 0)
        if retries >= 2:
            print(f"--- LOW CONFIDENCE ({state['confidence_score']}) / LIMIT REACHED: TRIGGERING FALLBACK ---")
            return "fallback"
        else:
            print(f"--- LOW CONFIDENCE ({state['confidence_score']}): RETRYING ---")
            return "retrieve"    # Loop back to search again or refine

# 4. Fallback Handler Node
def fallback_handler(state: GraphState):
    print("--- STEP: FALLBACK HANDLER ---")
    # Simulate Combined Flow: Detect Region -> Route -> Assign
    region = "US-East"
    print(f"--- Detect Region: {region} ---")
    print(f"--- Route to Regional Queue: {region} Queue ---")
    print("--- Assign to Available Agent (User waits in queue if busy) ---")
    
    response = (
        "I'm sorry, I don't have the information needed to answer that. "
        "Let me connect you with a support specialist who can help you further.\n"
        f"[System: Routed to {region} Support Queue. Assigning to available agent...]"
    )
    
    return {"response": response}

# -------------------------------------------------------------------------
# Constructing the LangGraph
# -------------------------------------------------------------------------
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("startup", startup_and_ingest)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.add_node("log_results", log_transaction) # New node
workflow.add_node("fallback", fallback_handler)   # Fallback node

# Define Flow
workflow.set_entry_point("startup")
workflow.add_edge("startup", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_conditional_edges(
    "generate",
    decide_to_finish,
    {
        "log_results": "log_results",
        "retrieve": "retrieve",
        "fallback": "fallback"
    }
)
workflow.add_edge("fallback", "log_results")  # Ensure fallback is logged
workflow.add_edge("log_results", END)         # Final exit

# Compile the Application
app = workflow.compile()

if __name__ == "__main__":
    inputs = {"question": "What are the payment terms in this contract?"}

    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"Finished Node: {key}")

    # Access the final state data
    final_state = output.get("log_results") or output.get("generate") or value
    print("-" * 30)
    print(f"ANSWER: {final_state.get('response', '')}")
    confidence = final_state.get('confidence_score', 0)
    print(f"CONFIDENCE SCORE: {confidence}%")
    print("-" * 30)
