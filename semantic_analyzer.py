import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import re
from collections import Counter

class SemanticAnalyzer:
    """Handles semantic analysis and ranking of document sections."""
    
    def __init__(self):
        self.vectorizer = None
    
    def rank_sections(self, sections: List[Dict[str, Any]], persona: str, task: str) -> List[Dict[str, Any]]:
        """Rank sections based on relevance to persona and task."""
        if not sections:
            return []
        
        # Create query from persona and task
        query = f"{persona} {task}"
        
        # Extract text content from sections
        section_texts = [section["content"] for section in sections]
        
        # Calculate relevance scores
        relevance_scores = self._calculate_relevance_scores(section_texts, query)
        
        # Add scores to sections and sort
        for i, section in enumerate(sections):
            section["relevance_score"] = float(relevance_scores[i])
            section["importance_rank"] = 0  # Will be set after sorting
        
        # Sort by relevance score (descending)
        ranked_sections = sorted(sections, key=lambda x: x["relevance_score"], reverse=True)
        
        # Apply selective filtering - only keep highly relevant sections
        filtered_sections = self._apply_relevance_filter(ranked_sections, persona, task)
        
        # Assign importance ranks to filtered sections
        for i, section in enumerate(filtered_sections):
            section["importance_rank"] = i + 1
        
        return filtered_sections
    
    def _calculate_relevance_scores(self, texts: List[str], query: str) -> np.ndarray:
        """Calculate relevance scores using multiple methods."""
        # Method 1: TF-IDF similarity
        tfidf_scores = self._tfidf_similarity(texts, query)
        
        # Method 2: Keyword matching
        keyword_scores = self._keyword_matching(texts, query)
        
        # Method 3: Simple entity matching (without spaCy)
        entity_scores = self._simple_entity_matching(texts, query)
        
        # Combine scores with weights
        combined_scores = (
            0.5 * tfidf_scores +
            0.3 * keyword_scores +
            0.2 * entity_scores
        )
        
        return combined_scores
    
    def _tfidf_similarity(self, texts: List[str], query: str) -> np.ndarray:
        """Calculate TF-IDF based cosine similarity."""
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            processed_query = self._preprocess_text(query)
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            # Fit on all texts including query
            all_texts = processed_texts + [processed_query]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            query_vector = tfidf_matrix[-1]
            document_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(query_vector, document_vectors).flatten()
            return similarities
            
        except Exception as e:
            print(f"TF-IDF similarity error: {e}")
            return np.zeros(len(texts))
    
    def _keyword_matching(self, texts: List[str], query: str) -> np.ndarray:
        """Calculate keyword matching scores."""
        # Extract keywords from query
        query_keywords = self._extract_keywords(query)
        
        scores = []
        for text in texts:
            text_keywords = self._extract_keywords(text)
            
            # Calculate keyword overlap
            overlap = len(set(query_keywords) & set(text_keywords))
            total_keywords = len(set(query_keywords) | set(text_keywords))
            
            if total_keywords > 0:
                score = overlap / total_keywords
            else:
                score = 0.0
            
            scores.append(score)
        
        return np.array(scores)
    
    def _simple_entity_matching(self, texts: List[str], query: str) -> np.ndarray:
        """Simple entity matching without spaCy."""
        # Extract potential entities (capitalized words) from query
        query_entities = set(re.findall(r'\b[A-Z][a-z]+\b', query))
        
        scores = []
        for text in texts:
            text_entities = set(re.findall(r'\b[A-Z][a-z]+\b', text))
            
            # Calculate entity overlap
            overlap = len(query_entities & text_entities)
            total_entities = len(query_entities | text_entities)
            
            if total_entities > 0:
                score = overlap / total_entities
            else:
                score = 0.0
            
            scores.append(score)
        
        return np.array(scores)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Split into words
        words = re.findall(r'\b\w+\b', processed_text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequencies
        word_freq = Counter(keywords)
        
        # Return most common keywords
        return [word for word, freq in word_freq.most_common(20)]
    
    def _apply_relevance_filter(self, ranked_sections: List[Dict[str, Any]], persona: str, task: str) -> List[Dict[str, Any]]:
        """Apply filtering to keep only highly relevant sections."""
        if not ranked_sections:
            return []
        
        # Calculate relevance threshold
        scores = [section["relevance_score"] for section in ranked_sections]
        if scores:
            threshold = np.mean(scores) + 0.5 * np.std(scores)
        else:
            threshold = 0.1
        
        # Filter sections above threshold
        filtered_sections = [section for section in ranked_sections if section["relevance_score"] >= threshold]
        
        # Apply persona-specific filtering
        filtered_sections = self._apply_persona_specific_filter(filtered_sections, persona, task)
        
        # Limit to top 20 sections
        return filtered_sections[:20]
    
    def _apply_persona_specific_filter(self, sections: List[Dict[str, Any]], persona: str, task: str) -> List[Dict[str, Any]]:
        """Apply persona-specific filtering to prioritize relevant content."""
        # Extract persona keywords
        persona_keywords = self._extract_keywords(persona)
        task_keywords = self._extract_keywords(task)
        
        # Score sections based on persona and task relevance
        for section in sections:
            section_text = section["content"].lower()
            
            # Calculate persona relevance
            persona_score = sum(1 for keyword in persona_keywords if keyword in section_text)
            
            # Calculate task relevance
            task_score = sum(1 for keyword in task_keywords if keyword in section_text)
            
            # Combine scores
            combined_score = persona_score + task_score
            
            # Boost relevance score for persona/task matches
            if combined_score > 0:
                section["relevance_score"] *= (1 + combined_score * 0.1)
        
        # Re-sort by updated scores
        return sorted(sections, key=lambda x: x["relevance_score"], reverse=True) 