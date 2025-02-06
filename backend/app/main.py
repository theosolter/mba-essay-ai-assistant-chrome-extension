from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
import sys

from .services.essay_analyzer import (
    EssayAnalyzer, 
    AnalysisRequest, 
    AnalysisResponse
)
from .services.rag import RAGService
from .config import Settings
from .middleware import error_handling_middleware
from .services.word_cutter import WordCutter, WordCutRequest, WordCutResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_cors(app: FastAPI) -> None:
    """Configure CORS for the application."""
    origins: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4173",  # Vite preview
        "chrome-extension://*",   # Chrome extension
        "http://localhost:8000",  # Localhost
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app = FastAPI(title="MBA Essay Assistant API")
setup_cors(app)
app.middleware("http")(error_handling_middleware)
settings = Settings()

essay_analyzer = EssayAnalyzer()
rag_service = RAGService()
word_cutter = WordCutter()

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_essay(request: AnalysisRequest):
    try:
        context = await rag_service.get_relevant_context(
            essay_text=request.essay_text,
            essay_prompt=request.essay_prompt,
            school=request.school
        )
        
        analysis = await essay_analyzer.analyze(
            essay_text=request.essay_text,
            essay_prompt=request.essay_prompt,
            user_instructions=request.user_instructions,
            context=context,
            school=request.school
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing essay: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cut-words", response_model=WordCutResponse)
async def cut_words(request: WordCutRequest):
    
    if not request.word_limit:
        raise HTTPException(status_code=400, detail="Word limit is required")
        
    try:
        result = await word_cutter.cut_words(
            essay_text=request.essay_text,
            essay_prompt=request.essay_prompt,
            word_limit=request.word_limit,
        )
        
        return result
    except Exception as e:
        logger.error(f"Error cutting words: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}