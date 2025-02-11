# MBA Essay Analyzer: A Chrome extension for Google Docs that helps MBA applicants write compelling essays.

This extension analyzes and refines your MBA application essays directly within Google Docs. Leveraging a unique backend powered by Retrieval-Augmented Generation (RAG) and an agentic workflow, it provides targeted feedback on essay structure, flow, word choice, and content. The system learns from a vector database of successful essays, school-specific examples, prompt information, and feedback data to offer personalized suggestions for improvement. Cut unnecessary words and strengthen your narrative to craft a winning MBA application.

[Watch a demo](https://drive.google.com/file/d/1POUQVKItoE5QSWmtWCCpJHuwFlPb3ac8/view?usp=drive_link) - **Please note: This demo is slightly outdated and does not include the latest agentic workflow features. An updated demo is coming soon!**

## Agentic workflow diagram

![Untitled drawing (1)](https://github.com/user-attachments/assets/ff2aed7c-08aa-469e-b391-2fd0cf0cb2b9)

## Setup Instructions

### Frontend Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cd frontend
   cp .env.example .env
   ```
2. Configure Google OAuth:
   - Create a project in Google Cloud Console
   - Enable Google OAuth2 API
   - Create OAuth 2.0 Client ID credentials
   - Add your Google OAuth client ID to `.env` file as `VITE_GOOGLE_CLIENT_ID`
   - Note: All frontend environment variables must be prefixed with `VITE_`
3. Configure API URL:
   - Set `VITE_API_BASE_URL` in `.env` (defaults to http://localhost:8001)
4. Install dependencies:
   ```bash
   yarn install
   ```

### Backend Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cd backend
   cp .env.example .env
   ```
2. Add your API keys to `.env`:
   - OPENAI_API_KEY
   - PINECONE_API_KEY
   - COHERE_API_KEY
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development
1. Start the frontend:
   ```bash
   cd frontend
   yarn dev
   ```
2. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Environment Variables
- Frontend (must be prefixed with `VITE_`):
  - VITE_GOOGLE_CLIENT_ID: OAuth client ID for Google authentication
  - VITE_API_BASE_URL: Backend API URL (default: http://localhost:8000)
- Backend:
  - OPENAI_API_KEY: API key for OpenAI services
  - PINECONE_API_KEY: API key for Pinecone vector database
  - COHERE_API_KEY: API key for Cohere reranking service
