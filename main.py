from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import os
import time
from datetime import datetime
import json

# Import the working components from DocuPersona
from document_processor import DocumentProcessor
from semantic_analyzer import SemanticAnalyzer
from summarizer import Summarizer

app = FastAPI(
    title="Persona-Driven Analysis API",
    description="Enhanced API for persona-driven document analysis",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path(__file__).parent / "uploads_1b"
UPLOAD_DIR.mkdir(exist_ok=True)

class AnalysisResponse(BaseModel):
    metadata: dict
    extracted_sections: List[dict]
    subsection_analysis: List[dict]

@app.get("/")
async def root():
    return {
        "message": "Persona-Driven Analysis API",
        "version": "2.0.0",
        "endpoints": {
            "process-persona": "POST /process-persona/ - Upload multiple PDFs for persona analysis"
        }
    }

@app.post("/process-persona/", response_model=AnalysisResponse)
async def process_persona(
    files: List[UploadFile] = File(...),
    persona: str = Form(...),
    job_to_be_done: str = Form(...)
):
    """Process multiple PDF files for persona-driven analysis."""
    
    try:
        # Validate inputs
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        if not persona or not job_to_be_done:
            raise HTTPException(status_code=400, detail="Persona and job_to_be_done are required")
        
        # Create session directory
        session_id = f"persona_{int(time.time())}"
        session_dir = UPLOAD_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
            
            file_path = session_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            saved_files.append((str(file_path), file.filename))
        
        if not saved_files:
            raise HTTPException(status_code=400, detail="No valid PDF files uploaded")
        
        # Process documents using DocuPersona approach
        results = process_documents(saved_files, persona, job_to_be_done)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

def process_documents(file_paths: List[tuple], persona: str, task: str) -> Dict[str, Any]:
    """Main processing pipeline for document analysis."""
    
    # Initialize components
    processor = DocumentProcessor()
    analyzer = SemanticAnalyzer()
    summarizer = Summarizer()
    
    start_time = time.time()
    
    # Extract text from PDFs
    documents = []
    for file_path, original_name in file_paths:
        doc_data = processor.extract_text_from_pdf(file_path, original_name)
        if doc_data:
            documents.append(doc_data)
    
    if not documents:
        raise Exception("No documents could be processed")
    
    # Extract sections from all documents
    all_sections = []
    for doc in documents:
        sections = processor.extract_sections(doc)
        all_sections.extend(sections)
    
    if not all_sections:
        raise Exception("No sections could be extracted from documents")
    
    # Rank sections based on semantic similarity to persona and task
    ranked_sections = analyzer.rank_sections(all_sections, persona, task)
    
    # Generate sub-section summaries (limited to match filtered sections)
    subsection_analysis = []
    for section in ranked_sections[:10]:  # Limit to top 10 to match filtering
        summary = summarizer.summarize_section(section)
        subsection_analysis.append(summary)
    
    processing_time = time.time() - start_time
    
    # Build results JSON
    results = {
        "metadata": {
            "input_documents": [name for _, name in file_paths],
            "persona": persona,
            "job_to_be_done": task,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
            "total_sections_extracted": len(all_sections),
            "total_documents_processed": len(documents)
        },
        "extracted_sections": ranked_sections,
        "subsection_analysis": subsection_analysis
    }
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 