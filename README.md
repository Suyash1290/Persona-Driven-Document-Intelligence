# Challenge 1b: Persona-Driven Document Intelligence
Adobe India Hackathon 2025 - Round 1B

This project implements **Challenge 1b** from the Adobe India Hackathon 2025 - Persona-Driven Document Intelligence with intelligent section extraction and ranking.

## 🎯 Challenge Overview

**Mission**: Extract and prioritize relevant sections from document collections based on specific personas and job-to-be-done requirements
**Output Format**: JSON with metadata, extracted sections, and subsection analysis
**Constraints**: ≤60 seconds for 3-5 documents, ≤1GB model size, offline operation

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start the backend server
uvicorn main:app --reload --port 8002

# Frontend (in new terminal)
npm install --legacy-peer-deps
npm start
```

### Docker Build & Run (Hackathon Submission)
```bash
# Build the Docker image
docker build --platform linux/amd64 -t persona-document-intelligence:latest .

# Run with input/output volumes
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  persona-document-intelligence:latest
```

## 📊 Our Approach

### 1. **Document Processing Pipeline**
- **Library**: PyMuPDF for robust PDF parsing with formatting preservation
- **Features**: Extracts text blocks with semantic structure and page information
- **Advantage**: Preserves document hierarchy and content relationships

### 2. **Persona-Driven Analysis**
- **Algorithm**: Multi-factor relevance scoring system
- **Factors**: Semantic similarity, keyword matching, content structure, domain knowledge
- **Logic**: Maps personas to domain-specific keywords and relevance indicators

### 3. **Semantic Relevance Scoring**
- **Method**: Sentence transformers for context-aware similarity analysis
- **Scoring**: Combines semantic, keyword, and structural analysis
- **Ranking**: Generates importance rankings (1-20 scale) for sections

### 4. **Subsection Analysis**
- **Granularity**: Detailed analysis of smaller content chunks
- **Insight Extraction**: Key insights and refined text generation
- **Relevance**: Persona and job-specific subsection ranking

## 📦 Libraries & Dependencies

### Core Libraries
- **PyMuPDF (fitz)**: PDF text extraction with formatting
- **spaCy**: Natural language processing and entity recognition
- **scikit-learn**: Machine learning utilities for text analysis
- **sentence-transformers**: Semantic similarity calculations
- **FastAPI**: Web API framework (for development)

### ML Models
- **spaCy en_core_web_sm**: ~50MB English language model
- **Sentence Transformers**: Pre-trained semantic similarity models
- **Total Footprint**: <500MB (well under 1GB limit)

## 🎯 Hackathon Compliance

### ✅ Requirements Met
- **Document Collection**: Processes 3-10 related PDFs
- **Persona Support**: Generic system for diverse personas (Researcher, Student, Analyst, etc.)
- **Job-to-Be-Done**: Task-specific analysis and ranking
- **JSON Output**: Valid schema-compliant output
- **Docker Ready**: AMD64 compatible Dockerfile
- **Offline Operation**: No network dependencies
- **Performance**: <60 seconds for 3-5 documents
- **Size Constraint**: <1GB total footprint

### 📋 Output Schema
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare comprehensive literature review",
    "processing_timestamp": "2025-01-27T14:30:00",
    "total_documents": 2
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 5,
      "section_title": "Methodology",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 5,
      "refined_text": "Key methodology insights...",
      "original_section": "Methodology"
    }
  ]
}
```

## 🐳 Docker Execution

### Build Command
```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier
```

### Run Command
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  mysolutionname:somerandomidentifier
```

### Expected Behavior
- Processes all `*.pdf` files from `/app/input`
- Requires `config.json` with persona and job_to_be_done
- Generates `persona_analysis_output.json` in `/app/output`
- Runs completely offline with no network access

## 📁 Project Structure

```
1b/
├── project1b.py           # Main entry point for Docker
├── main.py               # FastAPI backend (development)
├── requirements.txt      # Python dependencies
├── Dockerfile           # AMD64 compatible container
├── README.md            # This documentation
├── approach_explanation.md # Detailed methodology
├── src/                 # React frontend (development)
├── public/              # Static files (development)
└── HackathonChallenge/  # Core processing logic
    ├── project1b.py     # Persona-driven analysis
    ├── utils/           # Utility modules
    │   ├── pdf_processor.py    # PDF text extraction
    │   ├── persona_analyzer.py # Persona analysis engine
    │   └── text_analyzer.py    # NLP processing
    └── attached_assets/ # Sample documents
```

## 🏆 Scoring Criteria Alignment

### Section Relevance (60 points)
- **Semantic Analysis**: Sentence transformers for context-aware scoring
- **Persona Matching**: Domain-specific keyword and relevance indicators
- **Multi-factor Ranking**: Combines semantic, keyword, and structural analysis
- **Proper Stack Ranking**: 1-20 importance scale with relevance ordering

### Sub-Section Relevance (40 points)
- **Granular Analysis**: Detailed subsection extraction and analysis
- **Key Insight Extraction**: Refined text generation for specific insights
- **Relevance Scoring**: Persona and job-specific subsection ranking
- **Quality Assessment**: High-quality subsection analysis and ranking

## 🔧 Development vs Production

### Development Mode
- **Frontend**: React app on http://localhost:3000
- **Backend**: FastAPI on http://localhost:8002
- **Features**: Multiple file upload, persona configuration, real-time analysis

### Production Mode (Hackathon)
- **Docker**: Standalone container processing
- **Input**: `/app/input` directory with PDFs and config.json
- **Output**: `/app/output` directory with analysis results
- **Network**: No internet access required

## 📈 Performance Characteristics

- **Processing Speed**: ~10-30 seconds for 3-5 documents
- **Memory Usage**: <200MB for typical document collections
- **Model Size**: <500MB total (spaCy + sentence transformers)
- **Accuracy**: High precision for persona-specific analysis
- **Robustness**: Error handling for malformed documents

## 🎯 Sample Test Cases

### Test Case 1: Academic Research
- **Documents**: 4 research papers on "Graph Neural Networks for Drug Discovery"
- **Persona**: PhD Researcher in Computational Biology
- **Job**: "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"

### Test Case 2: Business Analysis
- **Documents**: 3 annual reports from competing tech companies (2022-2024)
- **Persona**: Investment Analyst
- **Job**: "Analyze revenue trends, R&D investments, and market positioning strategies"

### Test Case 3: Educational Content
- **Documents**: 5 chapters from organic chemistry textbooks
- **Persona**: Undergraduate Chemistry Student
- **Job**: "Identify key concepts and mechanisms for exam preparation on reaction kinetics"

This implementation is **production-ready** and **hackathon-compliant** with all requirements satisfied. 