import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from typing import List, Dict, Tuple
import json

class MLGrader:
    def __init__(self, threshold=0.65):
        self.model = None
        self.threshold = threshold
        self.feature_columns = [
            'semantic_similarity', 
            'lexical_similarity', 
            'keyword_overlap',
            'combined_similarity',
            'answer_length_ratio'
        ]
    
    def extract_features(self, similarity_df: pd.DataFrame) -> np.ndarray:
        """Extract features for ML model"""
        features = []
        
        for _, row in similarity_df.iterrows():
            pred_len = len(str(row['predicted']))
            exp_len = len(str(row['expected']))
            length_ratio = min(pred_len / max(exp_len, 1), 1.0)
            
            feature_vector = [
                row['semantic_similarity'],
                row['lexical_similarity'], 
                row['keyword_overlap'],
                row['combined_similarity'],
                length_ratio
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def create_training_data(self, n_samples=1000):
        """Create synthetic training data"""
        np.random.seed(42)
        data = []
        
        # Correct answers (high similarity)
        for _ in range(n_samples // 2):
            semantic = np.random.uniform(0.7, 1.0)
            lexical = np.random.uniform(0.6, 1.0)
            keyword = np.random.uniform(0.5, 1.0)
            combined = (semantic + lexical + keyword) / 3
            length_ratio = np.random.uniform(0.8, 1.2)
            
            data.append({
                'features': [semantic, lexical, keyword, combined, min(length_ratio, 1.0)],
                'label': 1
            })
        
        # Incorrect answers (low similarity)
        for _ in range(n_samples // 2):
            semantic = np.random.uniform(0.0, 0.4)
            lexical = np.random.uniform(0.0, 0.3)
            keyword = np.random.uniform(0.0, 0.2)
            combined = (semantic + lexical + keyword) / 3
            length_ratio = np.random.uniform(0.1, 1.5)
            
            data.append({
                'features': [semantic, lexical, keyword, combined, min(length_ratio, 1.0)],
                'label': 0
            })
        
        return data
    
    def train(self, training_data=None):
        """Train the ML grading model"""
        if training_data is None:
            training_data = self.create_training_data()
        
        X = np.array([item['features'] for item in training_data])
        y = np.array([item['label'] for item in training_data])
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = LogisticRegression(
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ ML Grader trained successfully")
        print(f"📊 Test Accuracy: {accuracy:.3f}")
        
        return self.model
    
    def predict_correctness(self, similarity_df: pd.DataFrame) -> pd.DataFrame:
        """Predict correctness for answer pairs"""
        if self.model is None:
            print("🔧 Training ML grader...")
            self.train()
        
        X = self.extract_features(similarity_df)
        probabilities = self.model.predict_proba(X)[:, 1]
        
        result_df = similarity_df.copy()
        result_df['correctness_probability'] = probabilities
        result_df['ml_prediction'] = (probabilities >= self.threshold).astype(int)
        
        return result_df
    
    def save_model(self, filepath: str):
        if self.model is not None:
            joblib.dump(self.model, filepath)
            print(f"💾 Model saved to: {filepath}")
    
    def load_model(self, filepath: str):
        self.model = joblib.load(filepath)
        print(f"💾 Model loaded from: {filepath}")

def test_ml_grader():
    from similarity_evaluator import SimilarityEvaluator
    
    evaluator = SimilarityEvaluator()
    
    test_pairs = [
        ("photosynthesis", "photosynthesis"),
        ("photosinthesis", "photosynthesis"), 
        ("cell energy", "photosynthesis"),
        ("mitochondria", "cell powerhouse"),
        ("wrong answer", "photosynthesis"),
    ]
    
    predictions = [p[0] for p in test_pairs]
    expected = [p[1] for p in test_pairs]
    
    similarity_df = evaluator.evaluate_answers(predictions, expected)
    grader = MLGrader()
    graded_df = grader.predict_correctness(similarity_df)
    
    print("🧪 ML Grading Results")
    print("="*50)
    print(graded_df[['predicted', 'expected', 'combined_similarity', 'correctness_probability', 'ml_prediction']])

if __name__ == "__main__":
    test_ml_grader()
