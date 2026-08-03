# Installation Guide (Open Notebook Lite)

This guide describes the decoupled architecture setup, demonstrating how to run the API and Frontend on a Linux environment (e.g., a Debian VM) while leveraging a Windows Host for the heavy LLM inference.

## Prerequisites

1. **Linux Environment (VM / Container / WSL)**
   - Python 3.11+ (Python 3.13 supported)
   - Node.js & npm (for Next.js frontend)
   - `python3-dev` and build tools (required to compile `chroma-hnswlib`)
2. **Host (for LLM Execution)**
   - [`llama.cpp` server](https://github.com/ggerganov/llama.cpp) (`llama-server.exe`)
   - IBM Granite Models (`granite-4.0-h-tiny-UD-Q4_K_XL.gguf` & `granite-embedding-107m-multilingual-Q8_0.gguf`)

---

## Step 1: Start the LLM Router on the Host
The backend relies on an OpenAI-compatible endpoint for text generation and vector embeddings. We run `llama-server` in router-mode on the host machine.

1. Ensure your models are downloaded to a local directory.
2. Start the `llama-server.exe` on port `8080` (or another port of your choice).
   *Note: By omitting the `--model` flag and relying on a configuration file or dynamic loading, the server can handle both chat and embedding requests simultaneously.*

---

## Step 2: Configure the Backend Environment
1. Clone this repository into your Linux environment.
2. Navigate to the project root and create a `.env` file based on `.env.example`.
3. Set the `OPENAI_API_BASE` to point to your host machine's IP. 
   - *Example for QEMU/VirtualBox NAT:* `http://10.0.2.2:8080/v1`
   - *Example for WSL2:* Use the Windows host IP address.

```ini
# .env
OPENAI_API_BASE=http://10.0.2.2:8080/v1
OPENAI_API_KEY=local-bypass
LLM_MODEL_NAME=granite-4.0-h-tiny-UD-Q4_K_XL.gguf
EMBEDDING_MODEL_NAME=granite-embedding-107m-multilingual-Q8_0.gguf

SQLITE_DB_PATH=/path/to/project/data/notebook.db
CHROMA_DB_PATH=/path/to/project/data/chroma
```

---

## Step 3: Install & Start the FastAPI Backend
1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies (this will install FastAPI, LangChain, SQLAlchemy, ChromaDB, etc.):
   ```bash
   pip install -e .
   ```
3. Start the Uvicorn server:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
   *The SQLite database and ChromaDB collections will be automatically initialized in the `data/` directory upon first startup.*

---

## Step 4: Install & Start the Next.js Frontend
1. Open a new terminal and navigate to the `frontend/` directory.
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file in the `frontend/` directory to point to your FastAPI backend:
   ```ini
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Start the Next.js development server:
   ```bash
   npm run dev
   ```

## Step 5: Verify the Setup
1. Open your browser and navigate to `http://localhost:3000`.
2. Check the "System Status" banner on the Notebooks page. It should read `Aktiv: Open Notebook Light` and display the current ChromaDB chunk count.
3. Upload a test PDF via the Sources tab to verify that the Host LLM is successfully calculating embeddings.
