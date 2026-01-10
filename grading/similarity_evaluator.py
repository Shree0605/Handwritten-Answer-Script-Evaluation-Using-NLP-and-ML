import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
from typing import List, Dict, Tuple
import re

class SimilarityEvaluator:
    def __init__(self, model_name='paraphrase-MiniLM-L6-v2'):
        print(f"🔧 Loading similarity model: {model_name}")
        self.similarity_model = SentenceTransformer(model_name)
        self.similarity_cache = {}
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for comparison"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def semantic_similarity(self, predicted: str, expected: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        predicted_clean = self.clean_text(predicted)
        expected_clean = self.clean_text(expected)
        
        if not predicted_clean or not expected_clean:
            return 0.0
        
        cache_key = f"{predicted_clean}||{expected_clean}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        try:
            embeddings = self.similarity_model.encode([predicted_clean, expected_clean])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            self.similarity_cache[cache_key] = similarity
            return similarity
        except Exception as e:
            print(f"❌ Semantic similarity error: {e}")
            return 0.0
    
    def lexical_similarity(self, predicted: str, expected: str) -> float:
        """Calculate lexical similarity using edit distance"""
        predicted_clean = self.clean_text(predicted)
        expected_clean = self.clean_text(expected)
        
        if not predicted_clean or not expected_clean:
            return 0.0
        
        max_len = max(len(predicted_clean), len(expected_clean))
        if max_len == 0:
            return 0.0
        
        distance = Levenshtein.distance(predicted_clean, expected_clean)
        similarity = 1 - (distance / max_len)
        return max(0.0, similarity)
    
    def keyword_overlap(self, predicted: str, expected: str) -> float:
        """Calculate keyword overlap ratio"""
        predicted_clean = self.clean_text(predicted)
        expected_clean = self.clean_text(expected)
        
        if not predicted_clean or not expected_clean:
            return 0.0
        
        pred_words = set(predicted_clean.split())
        exp_words = set(expected_clean.split())
        
        if not exp_words:
            return 0.0
        
        intersection = len(pred_words.intersection(exp_words))
        union = len(pred_words.union(exp_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def combined_similarity(self, predicted: str, expected: str, 
                          weights: Dict[str, float] = None) -> float:
        """Calculate combined similarity score"""
        if weights is None:
            weights = {
                'semantic': 0.6,
                'lexical': 0.3, 
                'keyword': 0.1
            }
        
        semantic_sim = self.semantic_similarity(predicted, expected)
        lexical_sim = self.lexical_similarity(predicted, expected)
        keyword_sim = self.keyword_overlap(predicted, expected)
        
        combined = (weights['semantic'] * semantic_sim + 
                   weights['lexical'] * lexical_sim + 
                   weights['keyword'] * keyword_sim)
        
        return combined
    
    def evaluate_answers(self, predictions: List[str], expected_answers: List[str]) -> pd.DataFrame:
        """Evaluate multiple answer pairs"""
        results = []
        
        print("📊 Calculating similarity scores...")
        for i, (pred, exp) in enumerate(zip(predictions, expected_answers)):
            semantic = self.semantic_similarity(pred, exp)
            lexical = self.lexical_similarity(pred, exp)
            keyword = self.keyword_overlap(pred, exp)
            combined = self.combined_similarity(pred, exp)
            
            results.append({
                'index': i,
                'predicted': pred,
                'expected': exp,
                'semantic_similarity': semantic,
                'lexical_similarity': lexical,
                'keyword_overlap': keyword,
                'combined_similarity': combined,
                'exact_match': pred.lower().strip() == exp.lower().strip()
            })
        
        return pd.DataFrame(results)

def test_similarity():
    evaluator = SimilarityEvaluator()
    
    test_pairs = [
        ("photosynthesis", "photosynthesis"),
        ("photosinthesis", "photosynthesis"),
        ("plant energy process", "photosynthesis"),
        ("mitochondria", "cell power house"),
        ("abc", "photosynthesis"),
    ]
    
    print("🧪 Testing Similarity Evaluator")
    print("="*50)
    
    for pred, exp in test_pairs:
        semantic = evaluator.semantic_similarity(pred, exp)
        lexical = evaluator.lexical_similarity(pred, exp)
        combined = evaluator.combined_similarity(pred, exp)
        
        print(f"Pred: '{pred}' vs Exp: '{exp}'")
        print(f"  Semantic: {semantic:.3f}, Lexical: {lexical:.3f}, Combined: {combined:.3f}")
        print()

if __name__ == "__main__":
    test_similarity()
