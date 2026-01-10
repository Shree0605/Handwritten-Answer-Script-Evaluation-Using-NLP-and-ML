import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json
from .similarity_evaluator import SimilarityEvaluator
from .ml_grader import MLGrader

class AnswerEvaluationSystem:
    def __init__(self):
        self.similarity_evaluator = SimilarityEvaluator()
        self.ml_grader = MLGrader()
    
    def evaluate_student_answers(self, 
                               student_predictions: List[str],
                               expected_answers: List[str],
                               marks_per_question: List[int] = None) -> Dict[str, Any]:
        """
        Evaluate student answers and calculate total marks
        """
        if marks_per_question is None:
            marks_per_question = [1] * len(expected_answers)
        
        print("🎯 Starting answer evaluation...")
        
        # Step 1: Calculate similarity scores
        similarity_df = self.similarity_evaluator.evaluate_answers(
            student_predictions, expected_answers
        )
        
        # Step 2: ML-based correctness prediction
        graded_df = self.ml_grader.predict_correctness(similarity_df)
        
        # Step 3: Calculate marks
        total_marks = 0
        question_results = []
        
        for i, (_, row) in enumerate(graded_df.iterrows()):
            marks_obtained = marks_per_question[i] if row['ml_prediction'] == 1 else 0
            total_marks += marks_obtained
            
            question_results.append({
                'question_number': i + 1,
                'predicted_answer': row['predicted'],
                'expected_answer': row['expected'],
                'semantic_similarity': row['semantic_similarity'],
                'lexical_similarity': row['lexical_similarity'],
                'keyword_overlap': row['keyword_overlap'],
                'combined_similarity': row['combined_similarity'],
                'correctness_probability': row['correctness_probability'],
                'ml_prediction': row['ml_prediction'],
                'marks_obtained': marks_obtained,
                'total_marks': marks_per_question[i]
            })
        
        # Step 4: Prepare final results
        total_possible_marks = sum(marks_per_question)
        
        results = {
            'total_marks_obtained': total_marks,
            'total_possible_marks': total_possible_marks,
            'score_percentage': (total_marks / total_possible_marks) * 100,
            'questions_correct': sum(graded_df['ml_prediction']),
            'total_questions': len(graded_df),
            'average_similarity': graded_df['combined_similarity'].mean(),
            'question_details': question_results,
            'grading_summary': {
                'threshold_used': self.ml_grader.threshold,
                'ml_model_used': 'Logistic Regression',
                'similarity_model': 'Sentence Transformer'
            }
        }
        
        print(f"✅ Evaluation complete: {results['questions_correct']}/{results['total_questions']} correct")
        
        return results

def demo_evaluation():
    evaluator = AnswerEvaluationSystem()
    
    student_predictions = [
        "photosynthesis",
        "mitocondria", 
        "cell wall",
        "DNA replication",
        "wrong answer",
    ]
    
    expected_answers = [
        "photosynthesis",
        "mitochondria", 
        "cell membrane",
        "DNA replication",
        "photosynthesis"
    ]
    
    marks_per_question = [2, 2, 2, 3, 1]
    
    print("🎓 AUTOMATED ANSWER EVALUATION SYSTEM")
    print("="*60)
    
    results = evaluator.evaluate_student_answers(
        student_predictions, expected_answers, marks_per_question
    )
    
    print(f"📊 STUDENT RESULTS")
    print(f"✅ Total Marks: {results['total_marks_obtained']}/{results['total_possible_marks']}")
    print(f"📈 Percentage: {results['score_percentage']:.1f}%")
    print(f"🔢 Questions Correct: {results['questions_correct']}/{results['total_questions']}")
    print(f"📏 Average Similarity: {results['average_similarity']:.3f}")
    
    print(f"\n📝 QUESTION-WISE BREAKDOWN:")
    print("-" * 80)
    for question in results['question_details']:
        status = "✅" if question['marks_obtained'] > 0 else "❌"
        print(f"{status} Q{question['question_number']}: {question['predicted_answer']}")
        print(f"   Expected: {question['expected_answer']}")
        print(f"   Similarity: {question['combined_similarity']:.3f}")
        print(f"   ML Confidence: {question['correctness_probability']:.3f}")
        print(f"   Marks: {question['marks_obtained']}/{question['total_marks']}")
        print()
    
    return results

if __name__ == "__main__":
    demo_evaluation()

