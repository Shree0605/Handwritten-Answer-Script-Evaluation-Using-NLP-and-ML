import streamlit as st
import os
import tempfile
import json
from PIL import Image
import pandas as pd
import time
from enhanced_report import EnhancedReportGenerator
from human_in_loop import HumanInLoopCorrector
from utils.progress_tracker import ProgressTracker

# Page configuration
st.set_page_config(
    page_title="Handwritten Answer Evaluator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📝 Automated Handwritten Answer Evaluation System")
    st.markdown("---")
    
    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'corrected_predictions' not in st.session_state:
        st.session_state.corrected_predictions = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Upload answer script
        uploaded_file = st.file_uploader("📤 Upload Answer Script", 
                                       type=['jpg', 'jpeg', 'png'])
        
        # Upload or create ground truth
        gt_option = st.radio("Ground Truth:", 
                           ["Upload JSON", "Manual Input"])
        
        ground_truth = None
        if gt_option == "Upload JSON":
            gt_file = st.file_uploader("Upload Ground Truth JSON", 
                                     type=['json'])
            if gt_file:
                ground_truth = json.load(gt_file)
        else:
            st.info("Configure ground truth after processing")
        
        # Grading threshold
        threshold = st.slider("Grading Threshold", 0.1, 0.9, 0.65, 0.05)
        
        # Process button
        process_btn = st.button("🚀 Process Answer Script", 
                              type="primary", 
                              disabled=uploaded_file is None)
        
        # Reset button
        if st.button("🔄 Reset Processing"):
            reset_processing()
    
    # Main content area - Single column layout for better flow
    if uploaded_file:
        st.subheader("📄 Uploaded Answer Script")
        image = Image.open(uploaded_file)
        st.image(image, caption="Student Answer Script", use_container_width=True)  # Fixed deprecation warning
    
    if process_btn:
        process_answer_script(uploaded_file, ground_truth, threshold)
    
    # Show results in logical sequence below the processing
    if st.session_state.processing_complete:
        display_processing_results()
        
    if st.session_state.corrected_predictions:
        display_final_results()

def reset_processing():
    """Reset all session state variables"""
    st.session_state.processing_complete = False
    st.session_state.results = None
    st.session_state.corrected_predictions = None
    st.session_state.current_step = 0
    st.rerun()

def process_answer_script(uploaded_file, ground_truth, threshold):
    """Process the uploaded answer script with live progress"""
    
    # Initialize progress tracker
    progress_tracker = ProgressTracker()
    
    with st.container():
        st.subheader("🔄 Processing Pipeline")
        
        # Progress steps
        steps = [
            "Saving uploaded file...",
            "Cropping answer boxes...", 
            "Running OCR ensemble...",
            "Configuring ground truth...",
            "Evaluating answers...",
            "Processing complete!"
        ]
        
        # Create progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Save uploaded file
        current_step = 0
        status_text.text(f"📥 Step {current_step+1}/6: {steps[current_step]}")
        progress_bar.progress(16)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            input_image_path = tmp_file.name
        
        time.sleep(0.5)  # Visual delay
        
        # Step 2: Crop answers
        current_step = 1
        status_text.text(f"✂️ Step {current_step+1}/6: {steps[current_step]}")
        progress_bar.progress(33)
        
        from image_processing.answer_cropper import AnswerCropper
        cropper = AnswerCropper()
        cropped_paths = cropper.crop_answers(input_image_path)
        
        # Display cropped images
        if cropped_paths:
            st.success(f"✅ Detected {len(cropped_paths)} answer boxes")
            cols = st.columns(3)
            for idx, crop_path in enumerate(cropped_paths):
                with cols[idx % 3]:
                    st.image(crop_path, caption=f"Q{idx+1}", width=150)
        
        time.sleep(0.5)
        
        # Step 3: OCR Processing
        current_step = 2
        status_text.text(f"🔍 Step {current_step+1}/6: {steps[current_step]}")
        progress_bar.progress(50)
        
        from ocr.ensemble_ocr import OCREnsemble
        ocr_ensemble = OCREnsemble()
        predictions = ocr_ensemble.predict_batch(cropped_paths)
        
        time.sleep(0.5)
        
        # ---- SHOW OCR OUTPUT IMMEDIATELY ----
    st.markdown("### 🔍 OCR Results (Raw Output)")

    if not predictions:
        st.warning("No OCR predictions generated.") 
    else:
        for idx, (filename, pred_data) in enumerate(predictions.items()):
            st.markdown(f"**Q{idx+1} – {filename}**")
            st.write(f"Final Prediction: `{pred_data['final_prediction']}`")

            if pred_data['all_predictions']:
                with st.expander("🔎 Ensemble Details"):
                    for model, text in pred_data['all_predictions']:
                        st.write(f"- {model}: {text}")
            else:
                st.info("No OCR engine produced output.")

        # Step 4: Get ground truth (if not provided)
        current_step = 3
        status_text.text(f"📝 Step {current_step+1}/6: {steps[current_step]}")
        progress_bar.progress(66)
        
        if not ground_truth:
            ground_truth = get_manual_ground_truth(cropped_paths, predictions)
        
        time.sleep(0.5)
        
        # Step 5: Grading
        current_step = 4
        status_text.text(f"📊 Step {current_step+1}/6: {steps[current_step]}")
        progress_bar.progress(83)
        
        from grading.answer_evaluation import AnswerEvaluationSystem
        evaluator = AnswerEvaluationSystem()
        evaluator.ml_grader.threshold = threshold
        
        # Prepare data for grading
        student_predictions = []
        expected_answers = []
        question_files = []
        
        for crop_path in cropped_paths:
            filename = os.path.basename(crop_path)
            question_files.append(filename)
            
            if filename in predictions and predictions[filename]['final_prediction']:
                student_predictions.append(predictions[filename]['final_prediction'])
            else:student_predictions.append("")

            
            if filename in ground_truth['expected_answers']:
                expected_answers.append(ground_truth['expected_answers'][filename])
            else:
                expected_answers.append("Unknown")
        
        marks_per_question = [ground_truth.get('marks_per_question', 1)] * len(student_predictions)
        
        results = evaluator.evaluate_student_answers(
            student_predictions, expected_answers, marks_per_question
        )
        
        # Add metadata
        results['student_name'] = ground_truth.get('student_name', 'Student')
        results['exam_title'] = ground_truth.get('exam_title', 'Assessment')
        results['subject'] = ground_truth.get('subject', 'Subject')
        results['original_image'] = input_image_path
        results['annotated_image'] = os.path.join("output/cropped_answers", "annotated_answers.jpg")
        results['question_files'] = question_files
        results['raw_predictions'] = predictions
        
        # Store results
        st.session_state.results = results
        st.session_state.processing_complete = True
        
        # Step 6: Complete
        current_step = 5
        status_text.text(f"✅ Step {current_step+1}/6: {steps[current_step]}")
        progress_bar.progress(100)

        st.session_state.ocr_predictions = predictions

        
        # Cleanup
        os.unlink(input_image_path)
        
        st.success("🎉 Processing completed successfully!")

def get_manual_ground_truth(cropped_paths, predictions):
    """Get ground truth manually through UI"""
    st.subheader("📝 Configure Ground Truth")
    st.info("Please provide the expected answers for each question below:")
    
    ground_truth = {
        "student_name": st.text_input("Student Name", "John Doe"),
        "exam_title": st.text_input("Exam Title", "CAT 1 ASSESSMENT"),
        "subject": st.text_input("Subject", "Science"),
        "expected_answers": {},
        "marks_per_question": st.number_input("Marks per Question", min_value=1, value=1)
    }
    
    st.write("### Expected Answers:")
    
    # Create a table-like layout for better organization
    for idx, crop_path in enumerate(cropped_paths):
        filename = os.path.basename(crop_path)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 2])
            
            with col1:
                st.image(crop_path, caption=f"Q{idx+1}", width=120)
            
            with col2:
                predicted = predictions[filename]['final_prediction'] if filename in predictions else ""
                expected = st.text_input(
                    f"Expected answer for Q{idx+1}",
                    value=predicted,
                    key=f"exp_{idx}",
                    help="Edit this if the OCR prediction is incorrect"
                )
                ground_truth['expected_answers'][filename] = expected
            
            with col3:
                st.metric(
                    "OCR Prediction", 
                    predicted if predicted else "No prediction",
                    delta="Needs review" if not predicted else ""
                )
    
    if st.button("✅ Save Ground Truth & Continue", type="primary"):
        return ground_truth
    else:
        st.stop()

def display_processing_results():
    """Display all processing results in sequence"""
    st.markdown("---")
    st.subheader("📊 Processing Results")
    
    results = st.session_state.results
    
    # 1. Show OCR Predictions First
    st.subheader("🔍 OCR Predictions")
    ocr_data = []
    for idx, (filename, pred_data) in enumerate(results['raw_predictions'].items()):
        ocr_data.append({
            'Question': f"Q{idx+1}",
            'Prediction': pred_data['final_prediction'],
            'All Model Predictions': ", ".join([f"{model}: {pred}" for model, pred in pred_data['all_predictions']])
        })
    
    st.dataframe(pd.DataFrame(ocr_data), use_container_width=True)
    
    # 2. Show Initial Evaluation Results
    st.subheader("📈 Initial Evaluation Results")
    
    # Overall metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Score", 
            f"{results['total_marks_obtained']}/{results['total_possible_marks']}",
            help="Marks obtained vs total possible marks"
        )
    with col2:
        st.metric(
            "Percentage", 
            f"{results['score_percentage']:.1f}%",
            help="Overall percentage score"
        )
    with col3:
        st.metric(
            "Questions Correct", 
            f"{results['questions_correct']}/{results['total_questions']}",
            help="Number of correct answers"
        )
    with col4:
        st.metric(
            "Avg Similarity", 
            f"{results['average_similarity']:.3f}",
            help="Average similarity score across all answers"
        )
    
    # 3. Detailed Question Analysis
    st.subheader("📋 Question-wise Analysis")
    
    question_data = []
    for question in results['question_details']:
        question_data.append({
            'Question': f"Q{question['question_number']}",
            'Predicted': question['predicted_answer'],
            'Expected': question['expected_answer'],
            'Similarity': f"{question['combined_similarity']:.3f}",
            'ML Confidence': f"{question['correctness_probability']:.3f}",
            'Marks': f"{question['marks_obtained']}/{question['total_marks']}",
            'Status': '✅ Correct' if question['marks_obtained'] > 0 else '❌ Incorrect'
        })
    
    st.dataframe(pd.DataFrame(question_data), use_container_width=True)
    
    # NEW: Download Report Button BEFORE Manual Correction
    st.markdown("---")
    st.subheader("📄 Generate Initial Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Initial PDF Report", type="secondary", use_container_width=True):
            try:
                report_generator = EnhancedReportGenerator()
                pdf_report = report_generator.generate_pdf_report(results)
                with open(pdf_report, "rb") as file:
                    st.download_button(
                        label="⬇️ Click to Download PDF",
                        data=file,
                        file_name=f"Initial_Report_{results['student_name']}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Could not generate PDF report: {e}")
    
    with col2:
        if st.button("📥 Download Initial HTML Report", type="secondary", use_container_width=True):
            try:
                report_generator = EnhancedReportGenerator()
                html_report = report_generator.generate_html_report(results)
                with open(html_report, "r") as file:
                    html_content = file.read()
                
                st.download_button(
                    label="⬇️ Click to Download HTML",
                    data=html_content,
                    file_name=f"Initial_Report_{results['student_name']}.html",
                    mime="text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Could not generate HTML report: {e}")
    
    # 4. Human in the loop correction
    st.markdown("---")
    st.subheader("✏️ Manual Correction (Human-in-the-Loop)")
    st.info("""
    💡 **Review and correct OCR predictions if needed:**  
    - If the OCR made a mistake in reading the handwriting, you can correct it here
    - The system will re-evaluate with your corrections
    - This ensures fair grading despite OCR errors
    - *You can also download the initial report above without making corrections*
    """)
    
    corrector = HumanInLoopCorrector()
    corrected_data = corrector.display_correction_interface(st.session_state.results)
    
    if corrected_data:
        st.session_state.corrected_predictions = corrected_data
        st.rerun()

def display_final_results():
    """Display final results after human correction"""
    st.markdown("---")
    st.subheader("🎯 Final Evaluation Results")
    
    corrected_data = st.session_state.corrected_predictions
    results = corrected_data['final_results']
    
    st.success(f"✅ Re-evaluation complete! {corrected_data.get('correction_count', 0)} corrections applied.")
    
    # Enhanced metrics display with improvement
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Final Score", 
            f"{results['total_marks_obtained']}/{results['total_possible_marks']}",
            delta=f"+{results.get('improvement', 0)} marks",
            help="Final score after manual corrections"
        )
    with col2:
        st.metric(
            "Final Percentage", 
            f"{results['score_percentage']:.1f}%",
            help="Final percentage score"
        )
    with col3:
        st.metric(
            "Correct Answers", 
            f"{results['questions_correct']}/{results['total_questions']}",
            help="Number of correct answers after correction"
        )
    with col4:
        changes = corrected_data.get('correction_count', 0)
        st.metric(
            "Manual Corrections", 
            changes,
            help="Number of answers manually corrected"
        )
    
    # Show what was corrected
    if corrected_data.get('correction_count', 0) > 0:
        st.subheader("📝 Correction Summary")
        correction_summary = []
        for correction in corrected_data['correction_data']:
            if correction['changed']:
                correction_summary.append({
                    'Question': f"Q{correction['question_number']}",
                    'Original': correction['original_prediction'],
                    'Corrected': correction['corrected_prediction'],
                    'Impact': '✅ Improved' if len(correction['corrected_prediction']) > len(correction['original_prediction']) else '🔄 Modified'
                })
        
        if correction_summary:
            st.dataframe(pd.DataFrame(correction_summary), use_container_width=True)
    
    # Report Generation Section
    st.markdown("---")
    st.subheader("📄 Generate Final Reports")
    
    # Generate and display enhanced report
    report_generator = EnhancedReportGenerator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF Report
        try:
            pdf_report = report_generator.generate_pdf_report(results)
            with open(pdf_report, "rb") as file:
                st.download_button(
                    label="📥 Download Final PDF Report",
                    data=file,
                    file_name=f"Final_Report_{results['student_name']}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    help="Download a professional PDF report with all corrections"
                )
        except Exception as e:
            st.error(f"Could not generate PDF report: {e}")
    
    with col2:
        # HTML Report
        try:
            html_report = report_generator.generate_html_report(results)
            with open(html_report, "r") as file:
                html_content = file.read()
            
            st.download_button(
                label="📥 Download Final HTML Report",
                data=html_content,
                file_name=f"Final_Report_{results['student_name']}.html",
                mime="text/html",
                use_container_width=True,
                help="Download an interactive HTML report with charts and corrections"
            )
        except Exception as e:
            st.error(f"Could not generate HTML report: {e}")
    
    # HTML Report Preview
    st.subheader("👀 Interactive Report Preview")
    st.info("Below is a preview of the interactive HTML report. Download using the button above.")
    
    try:
        with open(html_report, "r") as file:
            html_content = file.read()
        st.components.v1.html(html_content, height=800, scrolling=True)
    except:
        st.warning("Interactive preview not available. Please download the HTML report to view it.")

if __name__ == "__main__":
    main()