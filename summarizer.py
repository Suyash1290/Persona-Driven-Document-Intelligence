import re
from typing import Dict, Any, List

class Summarizer:
    """Handles text summarization for document sections."""
    
    def __init__(self):
        self.max_summary_length = 500  # Maximum summary length in characters
        self.min_sentence_length = 10  # Minimum sentence length
    
    def summarize_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a refined summary of a document section."""
        content = section["content"]
        
        # Extract key sentences
        summary = self._extractive_summarization(content)
        
        return {
            "document_name": section["document_name"],
            "page_number": section["page_number"],
            "section_title": section["section_title"],
            "refined_extracted_text": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(content) if content else 0
        }
    
    def _extractive_summarization(self, text: str) -> str:
        """Perform extractive summarization by selecting key sentences."""
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 3:
            return text  # Return original if too short
        
        # Score sentences
        sentence_scores = self._score_sentences(sentences, text)
        
        # Select top sentences
        top_sentences = self._select_top_sentences(sentences, sentence_scores)
        
        # Reorder sentences to maintain original order
        selected_sentences = self._maintain_order(sentences, top_sentences)
        
        summary = ' '.join(selected_sentences)
        
        # Ensure summary is not too long
        if len(summary) > self.max_summary_length:
            summary = self._truncate_summary(summary)
        
        return summary
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= self.min_sentence_length:
                # Add period back if missing
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _score_sentences(self, sentences: List[str], full_text: str) -> List[float]:
        """Score sentences based on various features."""
        scores = []
        
        # Calculate word frequencies in the full text
        word_freq = self._calculate_word_frequencies(full_text)
        
        for sentence in sentences:
            score = 0.0
            
            # Feature 1: Word frequency score
            words = re.findall(r'\b\w+\b', sentence.lower())
            if words:
                freq_score = sum(word_freq.get(word, 0) for word in words) / len(words)
                score += freq_score * 0.4
            
            # Feature 2: Position score (first and last sentences are often important)
            position_score = self._calculate_position_score(sentences.index(sentence), len(sentences))
            score += position_score * 0.2
            
            # Feature 3: Length score (prefer medium-length sentences)
            length_score = self._calculate_length_score(len(words))
            score += length_score * 0.1
            
            # Feature 4: Keyword density
            keyword_score = self._calculate_keyword_score(sentence)
            score += keyword_score * 0.3
            
            scores.append(score)
        
        return scores
    
    def _calculate_word_frequencies(self, text: str) -> Dict[str, float]:
        """Calculate word frequencies in text."""
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Filter out stop words and short words
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequencies
        word_counts = {}
        total_words = len(filtered_words)
        
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Convert to frequencies
        word_freq = {word: count / total_words for word, count in word_counts.items()}
        
        return word_freq
    
    def _calculate_position_score(self, position: int, total_sentences: int) -> float:
        """Calculate position-based score for a sentence."""
        if total_sentences <= 1:
            return 1.0
        
        # First and last sentences get higher scores
        if position == 0 or position == total_sentences - 1:
            return 1.0
        elif position == 1 or position == total_sentences - 2:
            return 0.8
        else:
            # Middle sentences get lower scores
            return 0.5
    
    def _calculate_length_score(self, word_count: int) -> float:
        """Calculate length-based score for a sentence."""
        # Prefer medium-length sentences (10-30 words)
        if 10 <= word_count <= 30:
            return 1.0
        elif 5 <= word_count <= 50:
            return 0.7
        else:
            return 0.3
    
    def _calculate_keyword_score(self, sentence: str) -> float:
        """Calculate keyword density score for a sentence."""
        # Define important keywords
        important_keywords = {
            'important', 'key', 'main', 'primary', 'essential', 'critical',
            'significant', 'major', 'central', 'fundamental', 'crucial',
            'conclusion', 'summary', 'overview', 'introduction', 'background',
            'method', 'approach', 'technique', 'strategy', 'solution'
        }
        
        # Count important keywords
        words = re.findall(r'\b\w+\b', sentence.lower())
        keyword_count = sum(1 for word in words if word in important_keywords)
        
        # Normalize by sentence length
        if words:
            return min(keyword_count / len(words) * 10, 1.0)
        else:
            return 0.0
    
    def _select_top_sentences(self, sentences: List[str], scores: List[float]) -> List[str]:
        """Select top-scoring sentences for summary."""
        # Pair sentences with scores
        sentence_scores = list(zip(sentences, scores))
        
        # Sort by score (descending)
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top sentences (aim for 30-50% of original)
        target_length = max(3, len(sentences) // 3)
        selected_sentences = [sentence for sentence, score in sentence_scores[:target_length]]
        
        return selected_sentences
    
    def _maintain_order(self, original_sentences: List[str], selected_sentences: List[str]) -> List[str]:
        """Maintain original sentence order in summary."""
        # Create a set for fast lookup
        selected_set = set(selected_sentences)
        
        # Return sentences in original order
        ordered_sentences = [sentence for sentence in original_sentences if sentence in selected_set]
        
        return ordered_sentences
    
    def _truncate_summary(self, summary: str) -> str:
        """Truncate summary to maximum length."""
        if len(summary) <= self.max_summary_length:
            return summary
        
        # Find a good breaking point
        truncated = summary[:self.max_summary_length]
        last_space = truncated.rfind(' ')
        
        if last_space > self.max_summary_length * 0.8:
            truncated = truncated[:last_space]
        
        return truncated + "..." 