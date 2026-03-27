# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from fpdf import FPDF
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime
# import json
# from jinja2 import Template

# class EnhancedReportGenerator:
#     def __init__(self):
#         self.template_dir = "templates"
#         os.makedirs(self.template_dir, exist_ok=True)

#     def generate_html_report(self, results):
#         """Generate interactive HTML report using template"""
        
#         # Calculate additional metrics
#         confidence = self._calculate_confidence(results)
#         ocr_accuracy = self._calculate_ocr_accuracy(results)
        
#         # Prepare data for template
#         template_data = {
#             'exam_title': results.get('exam_title', 'Assessment'),
#             'student_name': results.get('student_name', 'Student'),
#             'subject': results.get('subject', 'Subject'),
#             'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
#             'total_marks_obtained': results['total_marks_obtained'],
#             'total_possible_marks': results['total_possible_marks'],
#             'score_percentage': round(results['score_percentage'], 1),
#             'questions_correct': results['questions_correct'],
#             'total_questions': results['total_questions'],
#             'average_similarity': round(results['average_similarity'], 3),
#             'improvement': results.get('improvement', 0),
#             'grading_confidence': confidence['level'],
#             'confidence_class': confidence['class'],
#             'ocr_accuracy': ocr_accuracy,
#             'questions': self._prepare_questions_data(results),
#             'similarities': self._extract_similarities(results),
#             'question_numbers': list(range(1, len(results['question_details']) + 1)),
#             'question_scores': [q['marks_obtained'] for q in results['question_details']],
#             'similarities_list': [q['combined_similarity'] for q in results['question_details']],
#             'max_marks_per_question': max([q['total_marks'] for q in results['question_details']])
#         }
        
#         # Load template
#         template_path = os.path.join(self.template_dir, "report_template.html")
#         if not os.path.exists(template_path):
#             # Create template if it doesn't exist
#             self._create_default_template()
        
#         with open(template_path, 'r') as f:
#             template_content = f.read()
        
#         # Render template
#         template = Template(template_content)
#         html_content = template.render(**template_data)
        
#         # Save HTML file
#         report_path = f"output/reports/{results['student_name']}_interactive_report.html"
#         os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
#         with open(report_path, 'w') as f:
#             f.write(html_content)
        
#         return report_path
    
#     def _calculate_confidence(self, results):
#         """Calculate grading confidence level"""
#         avg_prob = sum(q['correctness_probability'] for q in results['question_details']) / len(results['question_details'])
        
#         if avg_prob >= 0.8:
#             return {'level': 'High', 'class': 'confidence-high'}
#         elif avg_prob >= 0.6:
#             return {'level': 'Medium', 'class': 'confidence-medium'}
#         else:
#             return {'level': 'Low', 'class': 'confidence-low'}
    
#     def _calculate_ocr_accuracy(self, results):
#         """Calculate OCR accuracy based on similarity scores"""
#         high_similarity = sum(1 for q in results['question_details'] if q['combined_similarity'] > 0.7)
#         accuracy = (high_similarity / len(results['question_details'])) * 100
#         return round(accuracy, 1)
    
#     def _prepare_questions_data(self, results):
#         """Prepare question data for template"""
#         questions = []
#         for q in results['question_details']:
#             questions.append({
#                 'question_number': q['question_number'],
#                 'predicted_answer': q['predicted_answer'],
#                 'expected_answer': q['expected_answer'],
#                 'combined_similarity': round(q['combined_similarity'], 3),
#                 'correctness_probability': round(q['correctness_probability'], 3),
#                 'marks_obtained': q['marks_obtained'],
#                 'total_marks': q['total_marks'],
#                 'corrected': q.get('corrected', False)
#             })
#         return questions
    
#     def _extract_similarities(self, results):
#         """Extract similarity scores for distribution chart"""
#         return [round(q['combined_similarity'], 2) for q in results['question_details']]
    
#     def _create_default_template(self):
#         """Create default HTML template if it doesn't exist"""
#         # This is the complete HTML template from above
#         template_content = """
#         <!DOCTYPE html>
#         <html lang="en">
#         ... [the entire HTML template from above] ...
#         </html>
#         """
        
#         template_path = os.path.join(self.template_dir, "report_template.html")
#         with open(template_path, 'w') as f:
#             f.write(template_content)
    
#     def generate_pdf_report(self, results):
#         """Generate professional PDF report"""
#         pdf = FPDF()
#         pdf.set_auto_page_break(auto=True, margin=15)
        
#         # Add first page
#         pdf.add_page()
        
#         # Header
#         pdf.set_font('Arial', 'B', 16)
#         pdf.cell(0, 10, results['exam_title'], 0, 1, 'C')
#         pdf.set_font('Arial', 'B', 14)
#         pdf.cell(0, 10, 'EVALUATION REPORT', 0, 1, 'C')
#         pdf.ln(10)
        
#         # Student info
#         pdf.set_font('Arial', 'B', 12)
#         pdf.cell(0, 10, f"Student: {results['student_name']}", 0, 1)
#         pdf.cell(0, 10, f"Subject: {results['subject']}", 0, 1)
#         pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
#         pdf.ln(10)
        
#         # Summary
#         pdf.set_font('Arial', 'B', 14)
#         pdf.cell(0, 10, 'SUMMARY', 0, 1)
#         pdf.set_font('Arial', '', 12)
        
#         summary_data = [
#             f"Total Score: {results['total_marks_obtained']}/{results['total_possible_marks']}",
#             f"Percentage: {results['score_percentage']:.1f}%",
#             f"Questions Correct: {results['questions_correct']}/{results['total_questions']}",
#             f"Average Similarity: {results['average_similarity']:.3f}"
#         ]
        
#         for line in summary_data:
#             pdf.cell(0, 10, line, 0, 1)
        
#         pdf.ln(10)
        
#         # Detailed results
#         pdf.set_font('Arial', 'B', 14)
#         pdf.cell(0, 10, 'DETAILED BREAKDOWN', 0, 1)
        
#         # Table header
#         pdf.set_font('Arial', 'B', 10)
#         pdf.cell(20, 10, 'Q.No', 1)
#         pdf.cell(60, 10, 'Predicted', 1)
#         pdf.cell(60, 10, 'Expected', 1)
#         pdf.cell(20, 10, 'Marks', 1)
#         pdf.cell(30, 10, 'Similarity', 1)
#         pdf.ln()
        
#         # Table rows
#         pdf.set_font('Arial', '', 9)
#         for question in results['question_details']:
#             pdf.cell(20, 10, f"Q{question['question_number']}", 1)
#             pdf.cell(60, 10, question['predicted_answer'][:30], 1)
#             pdf.cell(60, 10, question['expected_answer'][:30], 1)
#             pdf.cell(20, 10, f"{question['marks_obtained']}/{question['total_marks']}", 1)
#             pdf.cell(30, 10, f"{question['combined_similarity']:.3f}", 1)
#             pdf.ln()
        
#         # Save PDF
#         report_path = f"output/reports/{results['student_name']}_report.pdf"
#         os.makedirs(os.path.dirname(report_path), exist_ok=True)
#         pdf.output(report_path)
        
#         return report_path
    
#     def _create_score_gauge(self, results):
#         """Create a gauge chart for the score"""
#         percentage = results['score_percentage']
        
#         fig = go.Figure(go.Indicator(
#             mode = "gauge+number+delta",
#             value = percentage,
#             domain = {'x': [0, 1], 'y': [0, 1]},
#             title = {'text': "Overall Score"},
#             delta = {'reference': 50},
#             gauge = {
#                 'axis': {'range': [None, 100]},
#                 'bar': {'color': "darkblue"},
#                 'steps': [
#                     {'range': [0, 50], 'color': "lightgray"},
#                     {'range': [50, 80], 'color': "gray"},
#                     {'range': [80, 100], 'color': "lightgreen"}],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 90}}))
        
#         fig.update_layout(height=300)
#         return fig
    
#     def _create_score_distribution(self, results):
#         """Create a distribution chart of similarity scores"""
#         similarities = [q['combined_similarity'] for q in results['question_details']]
        
#         fig = px.histogram(x=similarities, 
#                           nbins=10,
#                           title="Distribution of Answer Similarities",
#                           labels={'x': 'Similarity Score', 'y': 'Number of Questions'})
        
#         fig.update_layout(height=300)
#         return fig
    

# #
# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from fpdf import FPDF
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime
# import json
# from jinja2 import Template

# class EnhancedReportGenerator:
#     def __init__(self):
#         self.template_dir = "templates"
#         os.makedirs(self.template_dir, exist_ok=True)

#     def generate_html_report(self, results):
#         """Generate interactive HTML report using template"""
        
#         # Calculate additional metrics
#         confidence = self._calculate_confidence(results)
#         ocr_accuracy = self._calculate_ocr_accuracy(results)
        
#         # Prepare data for template
#         template_data = {
#             'exam_title': results.get('exam_title', 'Assessment'),
#             'student_name': results.get('student_name', 'Student'),
#             'subject': results.get('subject', 'Subject'),
#             'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
#             'total_marks_obtained': results['total_marks_obtained'],
#             'total_possible_marks': results['total_possible_marks'],
#             'score_percentage': round(results['score_percentage'], 1),
#             'questions_correct': results['questions_correct'],
#             'total_questions': results['total_questions'],
#             'average_similarity': round(results['average_similarity'], 3),
#             'improvement': results.get('improvement', 0),
#             'grading_confidence': confidence['level'],
#             'confidence_class': confidence['class'],
#             'ocr_accuracy': ocr_accuracy,
#             'questions': self._prepare_questions_data(results),
#             'similarities': self._extract_similarities(results),
#             'question_numbers': list(range(1, len(results['question_details']) + 1)),
#             'question_scores': [q['marks_obtained'] for q in results['question_details']],
#             'similarities_list': [q['combined_similarity'] for q in results['question_details']],
#             'max_marks_per_question': max([q['total_marks'] for q in results['question_details']])
#         }
        
#         # Load template
#         template_path = os.path.join(self.template_dir, "report_template.html")
#         if not os.path.exists(template_path):
#             # Create template if it doesn't exist
#             self._create_default_template()
        
#         with open(template_path, 'r') as f:
#             template_content = f.read()
        
#         # Render template
#         template = Template(template_content)
#         html_content = template.render(**template_data)
        
#         # Save HTML file
#         report_path = f"output/reports/{results['student_name']}_interactive_report.html"
#         os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
#         with open(report_path, 'w') as f:
#             f.write(html_content)
        
#         return report_path
    
#     def _calculate_confidence(self, results):
#         """Calculate grading confidence level"""
#         avg_prob = sum(q['correctness_probability'] for q in results['question_details']) / len(results['question_details'])
        
#         if avg_prob >= 0.8:
#             return {'level': 'High', 'class': 'confidence-high'}
#         elif avg_prob >= 0.6:
#             return {'level': 'Medium', 'class': 'confidence-medium'}
#         else:
#             return {'level': 'Low', 'class': 'confidence-low'}
    
#     def _calculate_ocr_accuracy(self, results):
#         """Calculate OCR accuracy based on similarity scores"""
#         high_similarity = sum(1 for q in results['question_details'] if q['combined_similarity'] > 0.7)
#         accuracy = (high_similarity / len(results['question_details'])) * 100
#         return round(accuracy, 1)
    
#     def _prepare_questions_data(self, results):
#         """Prepare question data for template"""
#         questions = []
#         for q in results['question_details']:
#             questions.append({
#                 'question_number': q['question_number'],
#                 'predicted_answer': q['predicted_answer'],
#                 'expected_answer': q['expected_answer'],
#                 'combined_similarity': round(q['combined_similarity'], 3),
#                 'correctness_probability': round(q['correctness_probability'], 3),
#                 'marks_obtained': q['marks_obtained'],
#                 'total_marks': q['total_marks'],
#                 'corrected': q.get('corrected', False)
#             })
#         return questions
    
#     def _extract_similarities(self, results):
#         """Extract similarity scores for distribution chart"""
#         return [round(q['combined_similarity'], 2) for q in results['question_details']]
    
#     def _create_default_template(self):
#         """Create default HTML template if it doesn't exist"""
#         # This is the complete HTML template from above
#         template_content = """
#         <!DOCTYPE html>
#         <html lang="en">
#         ... [the entire HTML template from above] ...
#         </html>
#         """
        
#         template_path = os.path.join(self.template_dir, "report_template.html")
#         with open(template_path, 'w') as f:
#             f.write(template_content)
    
#     def generate_pdf_report(self, results):
#         """Generate professional PDF report"""
#         pdf = FPDF()
#         pdf.set_auto_page_break(auto=True, margin=15)
        
#         # Add first page
#         pdf.add_page()
        
#         # Header
#         pdf.set_font('Arial', 'B', 16)
#         pdf.cell(0, 10, results['exam_title'], 0, 1, 'C')
#         pdf.set_font('Arial', 'B', 14)
#         pdf.cell(0, 10, 'EVALUATION REPORT', 0, 1, 'C')
#         pdf.ln(10)
        
#         # Student info
#         pdf.set_font('Arial', 'B', 12)
#         pdf.cell(0, 10, f"Student: {results['student_name']}", 0, 1)
#         pdf.cell(0, 10, f"Subject: {results['subject']}", 0, 1)
#         pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
#         pdf.ln(10)
        
#         # Summary
#         pdf.set_font('Arial', 'B', 14)
#         pdf.cell(0, 10, 'SUMMARY', 0, 1)
#         pdf.set_font('Arial', '', 12)
        
#         summary_data = [
#             f"Total Score: {results['total_marks_obtained']}/{results['total_possible_marks']}",
#             f"Percentage: {results['score_percentage']:.1f}%",
#             f"Questions Correct: {results['questions_correct']}/{results['total_questions']}",
#             f"Average Similarity: {results['average_similarity']:.3f}"
#         ]
        
#         for line in summary_data:
#             pdf.cell(0, 10, line, 0, 1)
        
#         pdf.ln(10)
        
#         # Detailed results
#         pdf.set_font('Arial', 'B', 14)
#         pdf.cell(0, 10, 'DETAILED BREAKDOWN', 0, 1)
        
#         # Table header
#         pdf.set_font('Arial', 'B', 10)
#         pdf.cell(20, 10, 'Q.No', 1)
#         pdf.cell(60, 10, 'Predicted', 1)
#         pdf.cell(60, 10, 'Expected', 1)
#         pdf.cell(20, 10, 'Marks', 1)
#         pdf.cell(30, 10, 'Similarity', 1)
#         pdf.ln()
        
#         # Table rows
#         pdf.set_font('Arial', '', 9)
#         for question in results['question_details']:
#             pdf.cell(20, 10, f"Q{question['question_number']}", 1)
#             pdf.cell(60, 10, question['predicted_answer'][:30], 1)
#             pdf.cell(60, 10, question['expected_answer'][:30], 1)
#             pdf.cell(20, 10, f"{question['marks_obtained']}/{question['total_marks']}", 1)
#             pdf.cell(30, 10, f"{question['combined_similarity']:.3f}", 1)
#             pdf.ln()
        
#         # Save PDF
#         report_path = f"output/reports/{results['student_name']}_report.pdf"
#         os.makedirs(os.path.dirname(report_path), exist_ok=True)
#         pdf.output(report_path)
        
#         return report_path
    
#     def _create_score_gauge(self, results):
#         """Create a gauge chart for the score"""
#         percentage = results['score_percentage']
        
#         fig = go.Figure(go.Indicator(
#             mode = "gauge+number+delta",
#             value = percentage,
#             domain = {'x': [0, 1], 'y': [0, 1]},
#             title = {'text': "Overall Score"},
#             delta = {'reference': 50},
#             gauge = {
#                 'axis': {'range': [None, 100]},
#                 'bar': {'color': "darkblue"},
#                 'steps': [
#                     {'range': [0, 50], 'color': "lightgray"},
#                     {'range': [50, 80], 'color': "gray"},
#                     {'range': [80, 100], 'color': "lightgreen"}],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 90}}))
        
#         fig.update_layout(height=300)
#         return fig
    
#     def _create_score_distribution(self, results):
#         """Create a distribution chart of similarity scores"""
#         similarities = [q['combined_similarity'] for q in results['question_details']]
        
#         fig = px.histogram(x=similarities, 
#                           nbins=10,
#                           title="Distribution of Answer Similarities",
#                           labels={'x': 'Similarity Score', 'y': 'Number of Questions'})
        
#         fig.update_layout(height=300)
#         return fig
    
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from jinja2 import Template

class EnhancedReportGenerator:
    def __init__(self):
        self.template_dir = "templates"
        os.makedirs(self.template_dir, exist_ok=True)
    
    # NEW METHOD: Add this after __init__ but before generate_pdf_report
    def generate_enhanced_report(self, results, corrected_data=None):
        """Generate enhanced report with questions and feedback"""
        
        # Add question paper data to results for reporting
        if results.get('question_paper_data'):
            results['question_paper_context'] = results['question_paper_data']
        
        # Add feedback to results
        results['performance_feedback'] = self._generate_report_feedback(results, corrected_data)
        
        return self.generate_html_report(results)
    
    # NEW METHOD: Add this after generate_enhanced_report
    def _generate_report_feedback(self, results, corrected_data=None):
        """Generate comprehensive feedback for the report"""
        percentage = results['score_percentage']
        correct_answers = results['questions_correct']
        total_questions = results['total_questions']
        avg_similarity = results['average_similarity']
        
        feedback_sections = {
            'performance': '',
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # Performance analysis
        if percentage >= 90:
            feedback_sections['performance'] = "Exceptional performance demonstrating comprehensive understanding."
            feedback_sections['strengths'].extend([
                "Mastery of core concepts",
                "Excellent problem-solving skills",
                "Strong attention to detail"
            ])
        elif percentage >= 75:
            feedback_sections['performance'] = "Strong performance with good conceptual understanding."
            feedback_sections['strengths'].extend([
                "Solid foundation in key areas",
                "Good application of concepts"
            ])
            feedback_sections['improvements'].append("Focus on precision in answers")
        else:
            feedback_sections['performance'] = "Identified areas for improvement and growth."
            feedback_sections['improvements'].extend([
                "Review fundamental concepts",
                "Practice application of knowledge"
            ])
        
        # Answer quality analysis
        if avg_similarity >= 0.8:
            feedback_sections['strengths'].append("High answer accuracy and relevance")
        elif avg_similarity >= 0.6:
            feedback_sections['improvements'].append("Work on answer precision and completeness")
        
        # Correction analysis
        if corrected_data and corrected_data.get('correction_count', 0) > 0:
            feedback_sections['recommendations'].append(
                f"Note: {corrected_data['correction_count']} answers were reviewed for accuracy"
            )
        
        # Study recommendations
        incorrect_count = total_questions - correct_answers
        if incorrect_count > 0:
            feedback_sections['recommendations'].append(
                f"Focus on reviewing {incorrect_count} question(s) for improvement"
            )
        
        return feedback_sections
    
    # NEW METHOD: Add this after _generate_report_feedback
    def generate_comprehensive_pdf(self, results, corrected_data=None):
        """Generate PDF with questions and answers included"""
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f"{results.get('exam_title', 'Assessment')} - Comprehensive Report", 0, 1, 'C')
            pdf.ln(10)
            
            # Student Information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Student: {self._safe_text(results.get('student_name', 'Student'))}", 0, 1)
            pdf.cell(0, 10, f"Subject: {self._safe_text(results.get('subject', 'Subject'))}", 0, 1)
            pdf.cell(0, 10, f"Score: {results['total_marks_obtained']}/{results['total_possible_marks']} ({results['score_percentage']:.1f}%)", 0, 1)
            pdf.ln(10)
            
            # Questions and Answers Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Questions and Predicted Answers', 0, 1)
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 10)
            for idx, question in enumerate(results['question_details']):
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 8, f"Question {idx + 1}:", 0, 1)
                pdf.set_font('Arial', '', 9)
                
                # Predicted Answer
                predicted_text = self._safe_text(question['predicted_answer'])
                pdf.cell(0, 6, f"Predicted Answer: {predicted_text[:100]}...", 0, 1)
                
                # Expected Answer
                expected_text = self._safe_text(question['expected_answer'])
                pdf.cell(0, 6, f"Expected Answer: {expected_text[:100]}...", 0, 1)
                
                # Marks and Similarity
                pdf.cell(0, 6, f"Marks: {question['marks_obtained']}/{question['total_marks']} | Similarity: {question['combined_similarity']:.3f}", 0, 1)
                pdf.ln(3)
            
            # Add performance feedback
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Performance Feedback', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            feedback = self._generate_report_feedback(results, corrected_data)
            pdf.multi_cell(0, 8, f"Overall: {feedback['performance']}")
            
            if feedback['strengths']:
                pdf.cell(0, 8, "Strengths:", 0, 1)
                for strength in feedback['strengths']:
                    pdf.cell(10, 8, "", 0, 0)  # Indentation
                    pdf.cell(0, 8, f"• {strength}", 0, 1)
            
            if feedback['improvements']:
                pdf.cell(0, 8, "Areas for Improvement:", 0, 1)
                for improvement in feedback['improvements']:
                    pdf.cell(10, 8, "", 0, 0)  # Indentation
                    pdf.cell(0, 8, f"• {improvement}", 0, 1)
            
            if feedback['recommendations']:
                pdf.cell(0, 8, "Recommendations:", 0, 1)
                for recommendation in feedback['recommendations']:
                    pdf.cell(10, 8, "", 0, 0)  # Indentation
                    pdf.cell(0, 8, f"• {recommendation}", 0, 1)
            
            # Footer
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, 'Generated by Automated Handwriting Evaluation System', 0, 1, 'C')
            
            # Save PDF
            report_path = f"output/reports/{self._safe_filename(results['student_name'])}_comprehensive_report.pdf"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            pdf.output(report_path)
            
            return report_path
            
        except Exception as e:
            # Fallback to regular PDF generation
            return self.generate_pdf_report(results)
    
    # EXISTING METHODS - Keep all your existing methods below
    def generate_pdf_report(self, results):
        """Generate professional PDF report with Unicode support"""
        try:
            # Create PDF with Unicode support
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Add a Unicode-compatible font (make sure DejaVuSans.ttf is available)
            # For simplicity, we'll use standard fonts and avoid special characters
            pdf.add_page()
            
            # Header with colors
            pdf.set_fill_color(102, 126, 234)  # Blue color
            pdf.rect(0, 0, 210, 40, 'F')
            
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 20, self._safe_text(results.get('exam_title', 'Assessment Report')), 0, 1, 'C')
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'EVALUATION REPORT', 0, 1, 'C')
            
            # Reset text color
            pdf.set_text_color(0, 0, 0)
            pdf.ln(20)
            
            # Student info in a box
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, 60, 190, 30, 'F')
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Student: {self._safe_text(results.get('student_name', 'Student'))}", 0, 1)
            pdf.cell(0, 10, f"Subject: {self._safe_text(results.get('subject', 'Subject'))}", 0, 1)
            pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
            
            pdf.ln(15)
            
            # Summary metrics in a grid-like layout
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'PERFORMANCE SUMMARY', 0, 1)
            pdf.ln(5)
            
            # Metrics in a table
            col_width = 95
            row_height = 10
            
            # Header
            pdf.set_fill_color(200, 200, 200)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(col_width, row_height, 'METRIC', 1, 0, 'C', True)
            pdf.cell(col_width, row_height, 'VALUE', 1, 1, 'C', True)
            
            # Data rows
            pdf.set_font('Arial', '', 10)
            pdf.set_fill_color(255, 255, 255)
            
            metrics_data = [
                ('Total Score', f"{results['total_marks_obtained']}/{results['total_possible_marks']}"),
                ('Percentage', f"{results['score_percentage']:.1f}%"),
                ('Questions Correct', f"{results['questions_correct']}/{results['total_questions']}"),
                ('Average Similarity', f"{results['average_similarity']:.3f}"),
            ]
            
            for metric, value in metrics_data:
                pdf.cell(col_width, row_height, metric, 1, 0, 'L', True)
                pdf.cell(col_width, row_height, value, 1, 1, 'C', True)
            
            pdf.ln(10)
            
            # Detailed question analysis
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'QUESTION-WISE ANALYSIS', 0, 1)
            pdf.ln(5)
            
            # Table header
            pdf.set_fill_color(102, 126, 234)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 8)
            
            col_widths = [15, 45, 45, 20, 20, 15]
            headers = ['Q.No', 'Predicted', 'Expected', 'Similarity', 'Marks', 'Status']
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
            pdf.ln()
            
            # Table rows
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 7)
            
            for question in results['question_details']:
                # Question number
                pdf.cell(col_widths[0], 8, f"Q{question['question_number']}", 1, 0, 'C')
                
                # Predicted answer (truncated and safe encoded)
                predicted = self._safe_text(question['predicted_answer'])
                predicted = predicted[:20] + '...' if len(predicted) > 20 else predicted
                pdf.cell(col_widths[1], 8, predicted, 1, 0, 'L')
                
                # Expected answer (truncated and safe encoded)
                expected = self._safe_text(question['expected_answer'])
                expected = expected[:20] + '...' if len(expected) > 20 else expected
                pdf.cell(col_widths[2], 8, expected, 1, 0, 'L')
                
                # Similarity
                pdf.cell(col_widths[3], 8, f"{question['combined_similarity']:.3f}", 1, 0, 'C')
                
                # Marks
                pdf.cell(col_widths[4], 8, f"{question['marks_obtained']}/{question['total_marks']}", 1, 0, 'C')
                
                # Status - Use simple text instead of Unicode symbols
                if question['marks_obtained'] > 0:
                    status = 'CORRECT'
                else:
                    status = 'WRONG'
                
                pdf.cell(col_widths[5], 8, status, 1, 1, 'C')
            
            # Performance analysis section
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'PERFORMANCE ANALYSIS', 0, 1)
            
            pdf.set_font('Arial', '', 10)
            correct_count = results['questions_correct']
            total_count = results['total_questions']
            percentage = results['score_percentage']
            
            analysis_text = [
                f"Overall Performance: {percentage:.1f}%",
                f"Correct Answers: {correct_count} out of {total_count}",
                f"Accuracy Rate: {(correct_count/total_count*100):.1f}%",
                f"Average Confidence: {results['average_similarity']:.3f}"
            ]
            
            for text in analysis_text:
                pdf.cell(0, 8, text, 0, 1)
            
            # Footer
            pdf.ln(10)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, 'Generated by Automated Handwriting Evaluation System', 0, 1, 'C')
            
            # Save PDF
            report_path = f"output/reports/{self._safe_filename(results['student_name'])}_report.pdf"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            pdf.output(report_path)
            
            return report_path
            
        except Exception as e:
            # Fallback to simple PDF generation if the detailed one fails
            return self._generate_simple_pdf(results)
    
    def _safe_text(self, text):
        """Convert text to ASCII-safe string by removing/replacing special characters"""
        if text is None:
            return ""
        
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '✓': 'CORRECT',
            '✔': 'CORRECT', 
            '✅': 'CORRECT',
            '✗': 'WRONG',
            '✘': 'WRONG',
            '❌': 'WRONG',
            '–': '-',
            '—': '-',
            '…': '...',
            '‘': "'",
            '’': "'",
            '“': '"',
            '”': '"'
        }
        
        safe_text = str(text)
        for unicode_char, ascii_char in replacements.items():
            safe_text = safe_text.replace(unicode_char, ascii_char)
        
        # Remove any other non-ASCII characters
        safe_text = safe_text.encode('ascii', 'ignore').decode('ascii')
        
        return safe_text
    
    def _safe_filename(self, filename):
        """Create a safe filename without special characters"""
        safe_name = self._safe_text(filename)
        # Remove any problematic characters for filenames
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            safe_name = safe_name.replace(char, '_')
        return safe_name
    
    def _generate_simple_pdf(self, results):
        """Generate a very simple PDF as fallback"""
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'EVALUATION REPORT', 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Student: {self._safe_text(results.get('student_name', 'Student'))}", 0, 1)
        pdf.cell(0, 10, f"Exam: {self._safe_text(results.get('exam_title', 'Assessment'))}", 0, 1)
        pdf.cell(0, 10, f"Subject: {self._safe_text(results.get('subject', 'Subject'))}", 0, 1)
        pdf.ln(10)
        
        pdf.cell(0, 10, f"Final Score: {results['total_marks_obtained']}/{results['total_possible_marks']}", 0, 1)
        pdf.cell(0, 10, f"Percentage: {results['score_percentage']:.1f}%", 0, 1)
        pdf.cell(0, 10, f"Questions Correct: {results['questions_correct']}/{results['total_questions']}", 0, 1)
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Question Results:', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for question in results['question_details']:
            status = "CORRECT" if question['marks_obtained'] > 0 else "WRONG"
            pdf.cell(0, 8, f"Q{question['question_number']}: {status} - {question['marks_obtained']}/{question['total_marks']}", 0, 1)
        
        report_path = f"output/reports/{self._safe_filename(results['student_name'])}_simple_report.pdf"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        pdf.output(report_path)
        
        return report_path

    
    def generate_html_report(self, results):
        """Generate interactive HTML report (Unicode safe)"""
        try:
            # Calculate additional metrics
            confidence = self._calculate_confidence(results)
            ocr_accuracy = self._calculate_ocr_accuracy(results)
            
            # Prepare data for template
            template_data = {
                'exam_title': self._safe_text(results.get('exam_title', 'Assessment')),
                'student_name': self._safe_text(results.get('student_name', 'Student')),
                'subject': self._safe_text(results.get('subject', 'Subject')),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'total_marks_obtained': results['total_marks_obtained'],
                'total_possible_marks': results['total_possible_marks'],
                'score_percentage': round(results['score_percentage'], 1),
                'questions_correct': results['questions_correct'],
                'total_questions': results['total_questions'],
                'average_similarity': round(results['average_similarity'], 3),
                'improvement': results.get('improvement', 0),
                'grading_confidence': confidence['level'],
                'confidence_class': confidence['class'],
                'ocr_accuracy': ocr_accuracy,
                'questions': self._prepare_questions_data(results),
                'similarities': self._extract_similarities(results),
                'question_numbers': list(range(1, len(results['question_details']) + 1)),
                'question_scores': [q['marks_obtained'] for q in results['question_details']],
                'similarities_list': [q['combined_similarity'] for q in results['question_details']],
                'max_marks_per_question': max([q['total_marks'] for q in results['question_details']])
            }
            
            # Load template
            template_path = os.path.join(self.template_dir, "report_template.html")
            if not os.path.exists(template_path):
                self._create_default_template()
            
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Render template
            template = Template(template_content)
            html_content = template.render(**template_data)
            
            # Save HTML file
            report_path = f"output/reports/{self._safe_filename(results['student_name'])}_interactive_report.html"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return report_path
            
        except Exception as e:
            # Create a simple HTML fallback
            return self._generate_simple_html(results)
    
    def _generate_simple_html(self, results):
        """Generate simple HTML fallback"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Evaluation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
                .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self._safe_text(results.get('exam_title', 'Evaluation Report'))}</h1>
                <h2>Student: {self._safe_text(results.get('student_name', 'Student'))}</h2>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>Total Score</h3>
                    <p>{results['total_marks_obtained']}/{results['total_possible_marks']}</p>
                </div>
                <div class="metric">
                    <h3>Percentage</h3>
                    <p>{results['score_percentage']:.1f}%</p>
                </div>
                <div class="metric">
                    <h3>Correct Answers</h3>
                    <p>{results['questions_correct']}/{results['total_questions']}</p>
                </div>
                <div class="metric">
                    <h3>Average Similarity</h3>
                    <p>{results['average_similarity']:.3f}</p>
                </div>
            </div>
            
            <h3>Question Details:</h3>
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr style="background: #667eea; color: white;">
                    <th>Question</th>
                    <th>Predicted</th>
                    <th>Expected</th>
                    <th>Marks</th>
                    <th>Status</th>
                </tr>
        """
        
        for question in results['question_details']:
            status = "CORRECT" if question['marks_obtained'] > 0 else "WRONG"
            bg_color = "#d4edda" if question['marks_obtained'] > 0 else "#f8d7da"
            
            html_content += f"""
                <tr style="background: {bg_color};">
                    <td>Q{question['question_number']}</td>
                    <td>{self._safe_text(question['predicted_answer'])}</td>
                    <td>{self._safe_text(question['expected_answer'])}</td>
                    <td>{question['marks_obtained']}/{question['total_marks']}</td>
                    <td>{status}</td>
                </tr>
            """
        
        html_content += """
            </table>
            <p><em>Generated by Automated Handwriting Evaluation System</em></p>
        </body>
        </html>
        """
        
        report_path = f"output/reports/{self._safe_filename(results['student_name'])}_simple_report.html"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _calculate_confidence(self, results):
        """Calculate grading confidence level"""
        avg_prob = sum(q['correctness_probability'] for q in results['question_details']) / len(results['question_details'])
        
        if avg_prob >= 0.8:
            return {'level': 'High', 'class': 'confidence-high'}
        elif avg_prob >= 0.6:
            return {'level': 'Medium', 'class': 'confidence-medium'}
        else:
            return {'level': 'Low', 'class': 'confidence-low'}
    
    def _calculate_ocr_accuracy(self, results):
        """Calculate OCR accuracy based on similarity scores"""
        high_similarity = sum(1 for q in results['question_details'] if q['combined_similarity'] > 0.7)
        accuracy = (high_similarity / len(results['question_details'])) * 100
        return round(accuracy, 1)
    
    def _prepare_questions_data(self, results):
        """Prepare question data for template"""
        questions = []
        for q in results['question_details']:
            questions.append({
                'question_number': q['question_number'],
                'predicted_answer': self._safe_text(q['predicted_answer']),
                'expected_answer': self._safe_text(q['expected_answer']),
                'combined_similarity': round(q['combined_similarity'], 3),
                'correctness_probability': round(q['correctness_probability'], 3),
                'marks_obtained': q['marks_obtained'],
                'total_marks': q['total_marks'],
                'corrected': q.get('corrected', False)
            })
        return questions
    
    def _extract_similarities(self, results):
        """Extract similarity scores for distribution chart"""
        return [round(q['combined_similarity'], 2) for q in results['question_details']]
    
    def _create_default_template(self):
        """Create default HTML template"""
        # Use a simplified template to avoid Unicode issues
        template_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Evaluation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #667eea; color: white; padding: 20px; text-align: center; }
                .metric { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ exam_title }}</h1>
                <h2>Evaluation Report</h2>
            </div>
            
            <div class="metric">
                <h3>Student: {{ student_name }}</h3>
                <p>Score: {{ total_marks_obtained }}/{{ total_possible_marks }} ({{ score_percentage }}%)</p>
            </div>
        </body>
        </html>
        """
        
        template_path = os.path.join(self.template_dir, "report_template.html")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)