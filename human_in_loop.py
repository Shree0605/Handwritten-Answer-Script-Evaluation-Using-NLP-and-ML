import streamlit as st
import pandas as pd
from grading.answer_evaluation import AnswerEvaluationSystem

class HumanInLoopCorrector:
    def __init__(self):
        self.corrections = {}
    
    def display_correction_interface(self, results):
        """Display interface for manual correction of OCR predictions"""
        
        st.markdown("### Review and Correct Predictions")
        st.warning("💡 Correct any OCR errors below. Changes will affect final grading.")
        
        correction_data = []
        
        for i, question in enumerate(results['question_details']):
            with st.expander(f"Question {i+1} | Current Marks: {question['marks_obtained']}/{question['total_marks']}", 
                           expanded=question['marks_obtained']==0):
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write("**OCR Prediction:**")
                    current_pred = question['predicted_answer']
                    corrected_pred = st.text_area(
                        f"Edit prediction for Q{i+1}",
                        value=current_pred,
                        key=f"correction_{i}",
                        height=80,
                        label_visibility="collapsed"
                    )
                
                with col2:
                    st.write("**Expected Answer:**")
                    st.info(question['expected_answer'])
                    
                    st.write("**Similarity Metrics:**")
                    st.metric("Semantic", f"{question['semantic_similarity']:.3f}")
                    st.metric("Combined", f"{question['combined_similarity']:.3f}")
                
                with col3:
                    st.write("**Current Status:**")
                    if question['ml_prediction'] == 1:
                        st.success("✅ Correct")
                    else:
                        st.error("❌ Incorrect")
                    
                    st.write("**ML Confidence:**")
                    st.metric("Prob", f"{question['correctness_probability']:.3f}")
                
                # Track changes
                if corrected_pred != current_pred:
                    st.success(f"✏️ Correction applied: '{current_pred}' → '{corrected_pred}'")
                
                correction_data.append({
                    'question_number': i+1,
                    'original_prediction': current_pred,
                    'corrected_prediction': corrected_pred,
                    'expected_answer': question['expected_answer'],
                    'changed': corrected_pred != current_pred,
                    'total_marks': question['total_marks']
                })
        
        # Submit corrections
        if st.button("🔄 Re-evaluate with Corrections", type="primary"):
            return self.apply_corrections(correction_data, results)
        
        return None
    
    def apply_corrections(self, correction_data, original_results):
        """Apply manual corrections and re-evaluate"""
        
        # Extract corrected predictions
        corrected_predictions = [item['corrected_prediction'] for item in correction_data]
        expected_answers = [item['expected_answer'] for item in correction_data]
        marks_per_question = [item['total_marks'] for item in correction_data]
        
        # Count changes
        correction_count = sum(1 for item in correction_data if item['changed'])
        
        # Re-evaluate with corrections
        evaluator = AnswerEvaluationSystem()
        new_results = evaluator.evaluate_student_answers(
            corrected_predictions, expected_answers, marks_per_question
        )
        
        # Calculate improvement
        original_score = original_results['total_marks_obtained']
        new_score = new_results['total_marks_obtained']
        improvement = new_score - original_score
        
        # Add metadata
        new_results['student_name'] = original_results['student_name']
        new_results['exam_title'] = original_results['exam_title']
        new_results['subject'] = original_results['subject']
        new_results['improvement'] = improvement
        
        # Show comparison
        st.success(f"🎉 Re-evaluation complete! Score improved by {improvement} marks")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original Score", 
                     f"{original_score}/{original_results['total_possible_marks']}")
        with col2:
            st.metric("Corrected Score", 
                     f"{new_score}/{new_results['total_possible_marks']}",
                     delta=f"+{improvement}")
        
        return {
            'final_results': new_results,
            'correction_data': correction_data,
            'correction_count': correction_count,
            'improvement': improvement
        }
