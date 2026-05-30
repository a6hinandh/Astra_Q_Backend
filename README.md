# Astra_Q Backend

A hybrid Retrieval‑Augmented Generation (RAG) + Knowledge Graph (KG) backend for MOSDAC‑style satellite data queries.  
The service is built with **FastAPI**, **Neo4j**, **FAISS**, **Google Gemini**, and **Firebase**.

## Features

- **KG** – Cypher‑based queries powered by Neo4j and Gemini.
- **RAG** – Semantic search over a FAISS vector store built from parsed docs.
- **Hybrid** – Automatic mode selection (KG, RAG, or BOTH) based on the user query.
- **Firestore** – Conversation history persistence.
- **CORS** – Configurable via environment variables.
- **Health check** – `/health` endpoint for deployment monitoring.

## Local Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/Astra_Q_Backend.git
   cd Astra_Q_Backend
   ```

2. **Create a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file**  
   Copy the example and fill in the values.  
   ```bash
   cp .env.example .env
   ```

5. **Run the FastAPI server**  
   ```bash
   uvicorn backend.main:app --reload
   ```

6. **Build the FAISS index (once)**  
   ```bash
   python rag_pipeline/build_vector_index.py
   ```

## Deployment

The app is ready to be deployed on Render, Railway, or any platform that supports FastAPI.

### Render

1. Create a new **Web Service**.  
2. Set the **Build Command** to `pip install -r requirements.txt`  
3. Set the **Start Command** to `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`  
4. Add the environment variables listed in `.env.example`.  
5. Deploy.

### Railway

1. Add a new **Service**.  
2. Use the same build and start commands as Render.  
3. Add the required environment variables.  
4. Deploy.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Main chat endpoint. Accepts `user_id`, `thread_id`, and `message`. |
| `/api/thread/{thread_id}` | GET | Retrieve conversation history. Requires `user_id` query param. |
| `/health` | GET | Health check endpoint. Returns `{"status":"ok"}`. |

## Folder Structure

```
Astra_Q_Backend/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   │   └── chat.py
│   │   └── router_logic.py
│   └── session/
│       └── firebase_session.py
├── kg_pipeline/
│   ├── kg_nl_demo.py
│   ├── populate_kg.py
│   ├── queries.py
│   ├── cypher_examples.md
│   └── metadata_report.txt
├── rag_pipeline/
│   ├── build_vector_index.py
│   ├── retrieve.py
│   └── store_vectordb.py   # legacy prototype
├── requirements.txt
└── .env.example
```

## Testing

Run the test suite with:

```bash
pytest
```

(Tests are located in the `tests/` directory and cover the chat endpoint, KG queries, and RAG retrieval.)

## Contributing

Feel free to open issues or pull requests. Please keep the code style consistent and add tests for new features.

## License

MIT
