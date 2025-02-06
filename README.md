# MBA Essay Assistant

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