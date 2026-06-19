import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS as LC_FAISS
import google.generativeai as genai
import spacy


# ---------------- LAZY INIT HELPERS ----------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)


def _ensure_env_loaded():
    """Load .env files (idempotent — dotenv ignores repeated calls)."""
    env_path = os.path.join(BASE_DIR, "config", ".env")
    load_dotenv(env_path)
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    load_dotenv(os.path.join(CURRENT_DIR, "..", "kg_pipeline", ".env"))


def get_embedding_model():
    _ensure_env_loaded()
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_llm_model():
    _ensure_env_loaded()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash-lite")


def get_vectorstore():
    _ensure_env_loaded()
    embedding_wrapper = get_embedding_model()
    faiss_folder = os.path.join(CURRENT_DIR, "faiss_store")
    if not os.path.isdir(faiss_folder):
        raise RuntimeError(
            f"FAISS index not found at {faiss_folder}. "
            "Run 'python scripts/build_vector_index.py' or 'python rag_pipeline/build_vector_index.py' first."
        )
    # SAFETY: Deserializing a FAISS pickle from disk carries code-execution risk.
    # The index path is restricted to a known local directory (rag_pipeline/faiss_store/).
    # DO NOT load FAISS indexes from untrusted sources.
    return LC_FAISS.load_local(
        folder_path=faiss_folder,
        embeddings=embedding_wrapper,
        allow_dangerous_deserialization=True,
    )


@lru_cache(maxsize=1)
def get_retriever():
    return get_vectorstore().as_retriever(search_kwargs={"k": 5})


# ---------------- RAG CORE FUNCTION ----------------

def rag_qa(query: str, use_fallback: bool = False, fallback_keyword: str = None) -> str:
    _ensure_env_loaded()
    retriever = get_retriever()

    # Main retrieval call
    retrieved_docs = retriever.invoke(query)

    # Fallback keyword logic
    if use_fallback and fallback_keyword:
        fallback_lower = fallback_keyword.lower()
        found = any(fallback_lower in doc.page_content.lower() for doc in retrieved_docs)
    else:
        found = bool(retrieved_docs)

    # Fallback search if needed
    if use_fallback and not found and fallback_keyword:
        print("Semantic search failed. Using keyword fallback...")
        fallback_lower = fallback_keyword.lower()
        vectorstore = get_vectorstore()
        retrieved_docs = [
            doc
            for doc in vectorstore.docstore._dict.values()
            if fallback_lower in doc.page_content.lower()
        ]
        if not retrieved_docs:
            return f"Could not find any relevant information for '{fallback_keyword}'."

    # Reorder results to prioritize keyword-matching docs
    if use_fallback and fallback_keyword:
        contains_keyword, others = [], []
        fallback_lower = fallback_keyword.lower()

        for doc in retrieved_docs:
            if fallback_lower in doc.page_content.lower():
                contains_keyword.append(doc)
            else:
                others.append(doc)

        ordered_docs = contains_keyword + others
    else:
        ordered_docs = retrieved_docs

    # Build context
    context = "\n\n".join(doc.page_content for doc in ordered_docs)

    # Construct prompt
    prompt = f"""You are helping users understand MOSDAC satellite data products.

Context:
{context}

Question:
{query}

Instructions:
- Base your answer ONLY on the context above.
- If the question asks for spatial resolution or temporal frequency, look for:
  - grid size (e.g., 0.25 degree, 0.5 degree, km, etc.)
  - time step (e.g., 30 minutes, hourly, daily).
- If the context contains any approximate information related to the question, use it and answer in one strong, factual sentence.
- Only if the context truly has no relevant information to answer the question, respond with exactly: I don't know the answer.
- Do NOT say you don't know just because access details (download URL, portal path) are missing.

Answer in a paragraph format.:
"""


    print("Prompt sent to Gemini:\n", prompt)

    # Generate answer
    model = get_llm_model()
    response = model.generate_content(prompt)
    return response.text


# ---------------- FALLBACK KEYWORD EXTRACTION ----------------


@lru_cache(maxsize=1)
def get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        raise RuntimeError(
            "spaCy model 'en_core_web_sm' not found. "
            "Run: python -m spacy download en_core_web_sm"
        )


def extract_fallback_keyword(query: str) -> str:
    nlp = get_nlp()
    doc = nlp(query)
    entities = [ent.text for ent in doc.ents]
    return entities[0] if entities else None


# ---------------- RAG PIPELINE WRAPPER ----------------

def run_rag_pipeline(
    query: str,
    history: list | None = None,
    use_fallback: bool = True,
    fallback_keyword: str = None,
) -> dict:
    
    # Building a history-aware query text for Gemini (but NOT for retriever)
    history_prefix = "" 
    if history:
        last = history[-6:]
        lines = []
        for msg in last:
            prefix = "User:" if msg["role"] =="user" else "Assistant:"
            lines.append(f"{prefix} {msg['content']}")
        history_prefix="\n".join(lines) + "\n\n"
        history_aware_query = history_prefix + f"User's current question: {query}"

    # Auto-extract fallback keyword if not provided
    if not fallback_keyword:
        fallback_keyword = extract_fallback_keyword(query)

    # Retrieve docs BEFORE Gemini call for source listing
    retriever = get_retriever()
    retrieved_docs = retriever.invoke(query)

    # Extract top 3 sources
    sources = [
        {
            "source": doc.metadata.get("source", "Unknown"),
            "content_preview": doc.page_content[:200] + "...",
        }
        for doc in retrieved_docs[:3]
    ]

    # Get final answer from Gemini
    answer = rag_qa(
        history_aware_query,
        use_fallback=use_fallback,
        fallback_keyword=fallback_keyword,
    )

    return {
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    q = "Where is INSAT-3D SST data?"
    resp = run_rag_pipeline(q)
    print("Q:", q)
    print("Answer:", resp["answer"])
    print("Sources:", resp["sources"])
