import React, { useState } from 'react';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [persona, setPersona] = useState('');
  const [job, setJob] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Backend URL for Challenge 1b
  const BACKEND_URL = 'http://localhost:8002';

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setResults(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0 || !persona || !job) return;
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('persona', persona);
    formData.append('job_to_be_done', job);

    try {
      const res = await fetch(`${BACKEND_URL}/process-persona/`, {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) throw new Error('Failed to process PDFs for persona analysis');
      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadJSON = () => {
    if (!results) return;
    
    // Create the proper JSON output format
    const outputData = {
      metadata: results.metadata || {
        input_documents: files.map(file => file.name),
        persona: persona,
        job_to_be_done: job,
        processing_timestamp: new Date().toISOString()
      },
      extracted_sections: results.extracted_sections || [],
      subsection_analysis: results.subsection_analysis || []
    };

    // Create and download the JSON file
    const blob = new Blob([JSON.stringify(outputData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `persona_analysis_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎭 Persona-Driven Document Intelligence</h1>
        <p>Challenge 1b - Analyze multiple PDFs based on persona and job requirements</p>
      </header>

      <div className="main-content">
        <div className="upload-section">
          <h2>Upload PDF Files & Configure Analysis</h2>
          <form onSubmit={handleSubmit}>
            <div className="file-input-container">
              <input 
                type="file" 
                multiple 
                accept="application/pdf" 
                onChange={handleFileChange}
                className="file-input"
                id="file-input"
              />
              <label htmlFor="file-input" className="file-input-label">
                Choose PDF files...
              </label>
            </div>
            
            {files.length > 0 && (
              <div className="selected-files">
                <h3>Selected Files ({files.length}):</h3>
                <ul>
                  {files.map((file, index) => (
                    <li key={index}>{file.name}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="persona-config">
              <div className="input-group">
                <label htmlFor="persona">Persona:</label>
                <input
                  type="text"
                  id="persona"
                  value={persona}
                  onChange={(e) => setPersona(e.target.value)}
                  placeholder="e.g., Travel Planner"
                  required
                />
              </div>
              
              <div className="input-group">
                <label htmlFor="job">Job to be Done:</label>
                <input
                  type="text"
                  id="job"
                  value={job}
                  onChange={(e) => setJob(e.target.value)}
                  placeholder="e.g., Plan a trip of 4 days for a group of 10 college friends"
                  required
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              disabled={loading || files.length === 0 || !persona || !job}
              className="submit-button"
            >
              {loading ? 'Analyzing...' : 'Analyze PDFs'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="loading">
            <p>Analyzing {files.length} PDF file(s) for persona: {persona}</p>
            <p>Processing time constraint: ≤ 60 seconds</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>Error: {error}</p>
          </div>
        )}

        {results && (
          <div className="results">
            <div className="results-header">
              <h2>Analysis Results</h2>
              <button onClick={downloadJSON} className="download-button">
                📥 Download JSON Output
              </button>
            </div>
            
            <div className="analysis-summary">
              <h3>📊 Metadata</h3>
              <div className="metadata-grid">
                <div><strong>Persona:</strong> {results.metadata?.persona_description || persona}</div>
                <div><strong>Job:</strong> {results.metadata?.job_to_be_done_description || job}</div>
                <div><strong>Processed Files:</strong> {results.metadata?.input_documents?.length || 0}</div>
                <div><strong>Processing Time:</strong> {results.metadata?.processing_time ? `${results.metadata.processing_time.toFixed(2)}s` : 'N/A'}</div>
                <div><strong>Total Sections:</strong> {results.metadata?.total_sections_extracted || 0}</div>
                <div><strong>Timestamp:</strong> {new Date().toLocaleString()}</div>
              </div>
              
              <div className="json-preview">
                <h4>📄 JSON Output Preview</h4>
                <p>The downloaded JSON will contain:</p>
                <ul>
                  <li><strong>metadata:</strong> Input documents, persona, job-to-be-done, processing timestamp</li>
                  <li><strong>extracted_sections:</strong> Document, page number, section title, importance_rank, relevance_score</li>
                  <li><strong>subsection_analysis:</strong> Document, refined text, page number, compression ratio</li>
                </ul>
              </div>
            </div>
            
            <div className="sections-container">
              <div className="sections">
                <h4>📋 Extracted Sections ({results.extracted_sections?.length || 0})</h4>
                <div className="sections-grid">
                  {results.extracted_sections && results.extracted_sections.map((section, i) => (
                    <div key={i} className="section-card">
                      <div className="section-header">
                        <span className="relevance-score">Relevance: {section.relevance_score?.toFixed(2) || 'N/A'}</span>
                        <span className="importance-rank">Rank: {section.importance_rank || i + 1}</span>
                        <span className="page-number">Page: {section.page_number || 1}</span>
                      </div>
                      <h5 className="section-title">{section.section_title || `Section ${i + 1}`}</h5>
                      <p className="section-text">{section.content_preview || section.content || 'No content preview available'}</p>
                      <div className="section-meta">
                        <span>Document: {section.document}</span>
                        <span>Words: {section.word_count || 'N/A'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="subsections">
                <h4>🔍 Subsection Analysis ({results.subsection_analysis?.length || 0})</h4>
                <div className="subsections-grid">
                  {results.subsection_analysis && results.subsection_analysis.map((subsection, i) => (
                    <div key={i} className="subsection-card">
                      <div className="subsection-header">
                        <span className="page-number">Page: {subsection.page_number || 1}</span>
                        <span className="compression-ratio">Compression: {(subsection.compression_ratio * 100)?.toFixed(1) || 'N/A'}%</span>
                      </div>
                      <h5 className="subsection-title">{subsection.section_title || `Summary ${i + 1}`}</h5>
                      <p className="subsection-text">{subsection.refined_text || 'No summary available'}</p>
                      <div className="subsection-meta">
                        <span>Document: {subsection.document}</span>
                        <span>Original: {subsection.original_length || 'N/A'} chars</span>
                        <span>Summary: {subsection.summary_length || 'N/A'} chars</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 