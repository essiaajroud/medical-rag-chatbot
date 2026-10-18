# MediBot — Medical Chatbot with RAG

MediBot is a medical question-answering chatbot built with **Retrieval-Augmented Generation (RAG)**. It retrieves relevant information from a medical knowledge base and uses a language model to generate responses grounded in the available context.

The project combines a Python backend, semantic vector search, language-model integration, and a conversational web interface.

> **Medical disclaimer:** MediBot is an educational and informational project. It does not replace a qualified healthcare professional, medical diagnosis, or emergency medical care. In an emergency, contact local emergency services immediately.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Medical Safety](#medical-safety)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## Features

- Medical question answering using Retrieval-Augmented Generation.
- Semantic retrieval with FAISS.
- Text embeddings generated with Sentence Transformers.
- Language-model integration with Gemini and an optional Ollama provider.
- Multilingual question handling, including English, French, and Arabic.
- Source metadata for relevant medical information.
- Emergency symptom detection and priority handling.
- Fallback responses when the retrieved context is insufficient.
- Automated tests for emergency detection, retrieval behavior, and multilingual handling.

These features are subject to the current implementation and the contents of the medical knowledge base.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Question routing | LangGraph |
| Retrieval-augmented generation | Custom RAG pipeline |
| Vector search | FAISS |
| Text embeddings | Sentence Transformers |
| Embedding model | `paraphrase-multilingual-MiniLM-L12-v2` or the model configured by the application |
| Language model | Gemini API |
| Alternative language model | Ollama |
| Frontend | React, Vite, TypeScript |
| Testing | pytest |

Check the actual embedding configuration and dependency files before treating this table as a complete inventory.

## Architecture

MediBot follows a retrieval-augmented question-answering workflow:

1. The user submits a question through the chat interface.
2. The backend identifies the question's language and determines how to route it.
3. Emergency detection checks for supported emergency indicators.
4. For regular medical questions, the retrieval layer searches the FAISS index.
5. Relevant documents are filtered according to the configured context threshold.
6. The language model generates an answer using the selected context.
7. The backend returns the answer and available source references to the frontend.

If no relevant documents are retained, the current RAG pipeline can return a localized fallback response without calling the generation model.

## Project Structure

The following is an overview of the known application modules. Confirm the complete directory layout in the repository.

```text
Chatbot_with_RAG/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agent.py
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   └── language_utils.py
│   │   ├── data/
│   │   │   └── loader.py
│   │   ├── llm/
│   │   │   └── llm_service.py
│   │   └── rag/
│   │       ├── faiss_store.py
│   │       └── rag_pipeline.py
│   ├── data/
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── ...
```

### Important modules

- `app/main.py`: FastAPI application entry point.
- `app/api/routes.py`: API routes used by the frontend.
- `app/agent.py`: question classification, routing, and emergency detection.
- `app/rag/rag_pipeline.py`: retrieval filtering, prompt construction, and answer generation.
- `app/rag/faiss_store.py`: vector-search implementation.
- `app/llm/llm_service.py`: language-model integration.
- `app/core/language_utils.py`: language detection and localized text.
- `app/data/loader.py`: medical data loading.
- `tests/`: automated tests.
- `scripts/`: validation, evaluation, and development utilities.

## Prerequisites

- Python with a version compatible with the project's dependencies.
- Node.js and npm for the React/Vite frontend.
- A Gemini API key if the Gemini provider is enabled.
- Git for version control.

Ollama is needed only if the application is configured to use the local Ollama provider.

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Chatbot_with_RAG
```

Replace `<YOUR_REPOSITORY_URL>` with the actual Git repository URL.

### 2. Set up the backend

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, use the appropriate activation method for your system or execute the environment's Python directly.

### 3. Configure environment variables

Create a `.env` file in the backend directory if it is not already present.

Example configuration:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-2.5-flash
```

The exact supported variable names and defaults must match the current configuration code. Do not commit real API keys or other secrets to Git.

### 4. Install the frontend dependencies

Open another terminal and navigate to the actual frontend directory:

```powershell
cd ..\frontend

npm install
```

Use the directory containing the frontend's `package.json` if its name differs from `frontend`.

## Running the Application

### Start the backend

From the backend directory, with the virtual environment activated:

```powershell
uvicorn app.main:app --reload
```

The local API is expected to be available at:

`http://127.0.0.1:8000`

FastAPI's interactive API documentation is normally available at:

`http://127.0.0.1:8000/docs`

### Start the frontend

From the frontend directory:

```powershell
npm run dev
```

Open the local URL printed by Vite in the terminal.

The frontend must be configured to send requests to the running backend. Use the API URL and environment-variable conventions defined by the actual frontend code.

## API Documentation

Once the backend is running, open:

`http://127.0.0.1:8000/docs`

This page lists the API endpoints registered by FastAPI and allows supported requests to be tested interactively.

Refer to `app/api/routes.py` for the request and response schemas. Do not assume endpoint names or payload formats without checking the implementation.

## Testing

Run the backend test suite from the backend directory:

```powershell
python -m pytest -q
```

Run Python syntax and compilation checks:

```powershell
python -m compileall -q app scripts
```

The test suite includes checks for multilingual behavior and emergency detection, including tests of whether supported emergency cases bypass normal retrieval and generation paths.

Passing automated tests does not establish clinical validity or guarantee that all emergencies will be detected.

## Medical Safety

MediBot should be developed and evaluated with the following principles:

- Emergency indicators must take priority over routine question answering.
- The chatbot must not present a symptom list as a confirmed diagnosis.
- Answers must not claim to be supported by sources that were not actually retrieved and verified.
- Insufficient evidence should lead to an appropriate fallback response.
- Source metadata must be validated before it is presented as a citation.
- Medical content should be reviewed against reliable medical references.
- Emergency behavior must be evaluated for both false negatives and false positives.
- The application must not replace professional medical care.

## Troubleshooting

### The backend cannot start

- Activate the intended Python environment.
- Install dependencies from the backend requirements file.
- Check that the command is executed from the backend directory.
- Review the terminal error for missing modules or configuration problems.

### Gemini requests fail

- Confirm that the API key is configured in the environment used by the backend.
- Verify the selected model name and API access.
- Inspect the backend logs for authentication, quota, timeout, or provider errors.
- Never print or commit the full API key.

### The chatbot returns an insufficient-context response

- Confirm that the medical dataset is present and loaded.
- Verify that the FAISS index contains the expected records.
- Check the retrieval scores and context threshold.
- Confirm that the question is covered by the available medical documents.

### The frontend cannot reach the backend

- Confirm that FastAPI is running.
- Check the backend URL configured in the frontend.
- Inspect browser developer tools for network or CORS errors.
- Verify the request path and payload against the FastAPI documentation.

## Future Improvements

Potential areas for future work include:

- Expanding and reviewing the medical knowledge base.
- Improving multilingual retrieval and evaluation.
- Adding regression tests for emergency detection.
- Measuring retrieval quality and answer faithfulness.
- Improving source transparency and medical content review.
- Adding reproducible evaluation reports and development documentation.

## Disclaimer

MediBot is a software development and research project for medical information retrieval and question answering. It is not a certified medical device and must not be relied on as the sole basis for clinical decisions.
