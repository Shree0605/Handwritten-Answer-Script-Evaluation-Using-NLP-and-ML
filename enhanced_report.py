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

    def generate_html_report(self, results):
        """Generate interactive HTML report using template"""
        
        # Calculate additional metrics
        confidence = self._calculate_confidence(results)
        ocr_accuracy = self._calculate_ocr_accuracy(results)
        
        # Prepare data for template
        template_data = {
            'exam_title': results.get('exam_title', 'Assessment'),
            'student_name': results.get('student_name', 'Student'),
            'subject': results.get('subject', 'Subject'),
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
            # Create template if it doesn't exist
            self._create_default_template()
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Render template
        template = Template(template_content)
        html_content = template.render(**template_data)
        
        # Save HTML file
        report_path = f"output/reports/{results['student_name']}_interactive_report.html"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
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
                'predicted_answer': q['predicted_answer'],
                'expected_answer': q['expected_answer'],
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
        """Create default HTML template if it doesn't exist"""
        # This is the complete HTML template from above
        template_content = """
        <!DOCTYPE html>
        <html lang="en">
        ... [the entire HTML template from above] ...
        </html>
        """
        
        template_path = os.path.join(self.template_dir, "report_template.html")
        with open(template_path, 'w') as f:
            f.write(template_content)
    
    def generate_pdf_report(self, results):
        """Generate professional PDF report"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add first page
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, results['exam_title'], 0, 1, 'C')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'EVALUATION REPORT', 0, 1, 'C')
        pdf.ln(10)
        
        # Student info
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Student: {results['student_name']}", 0, 1)
        pdf.cell(0, 10, f"Subject: {results['subject']}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.ln(10)
        
        # Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SUMMARY', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        summary_data = [
            f"Total Score: {results['total_marks_obtained']}/{results['total_possible_marks']}",
            f"Percentage: {results['score_percentage']:.1f}%",
            f"Questions Correct: {results['questions_correct']}/{results['total_questions']}",
            f"Average Similarity: {results['average_similarity']:.3f}"
        ]
        
        for line in summary_data:
            pdf.cell(0, 10, line, 0, 1)
        
        pdf.ln(10)
        
        # Detailed results
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'DETAILED BREAKDOWN', 0, 1)
        
        # Table header
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(20, 10, 'Q.No', 1)
        pdf.cell(60, 10, 'Predicted', 1)
        pdf.cell(60, 10, 'Expected', 1)
        pdf.cell(20, 10, 'Marks', 1)
        pdf.cell(30, 10, 'Similarity', 1)
        pdf.ln()
        
        # Table rows
        pdf.set_font('Arial', '', 9)
        for question in results['question_details']:
            pdf.cell(20, 10, f"Q{question['question_number']}", 1)
            pdf.cell(60, 10, question['predicted_answer'][:30], 1)
            pdf.cell(60, 10, question['expected_answer'][:30], 1)
            pdf.cell(20, 10, f"{question['marks_obtained']}/{question['total_marks']}", 1)
            pdf.cell(30, 10, f"{question['combined_similarity']:.3f}", 1)
            pdf.ln()
        
        # Save PDF
        report_path = f"output/reports/{results['student_name']}_report.pdf"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        pdf.output(report_path)
        
        return report_path
    
    def _create_score_gauge(self, results):
        """Create a gauge chart for the score"""
        percentage = results['score_percentage']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = percentage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        fig.update_layout(height=300)
        return fig
    
    def _create_score_distribution(self, results):
        """Create a distribution chart of similarity scores"""
        similarities = [q['combined_similarity'] for q in results['question_details']]
        
        fig = px.histogram(x=similarities, 
                          nbins=10,
                          title="Distribution of Answer Similarities",
                          labels={'x': 'Similarity Score', 'y': 'Number of Questions'})
        
        fig.update_layout(height=300)
        return fig
    

#
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

    def generate_html_report(self, results):
        """Generate interactive HTML report using template"""
        
        # Calculate additional metrics
        confidence = self._calculate_confidence(results)
        ocr_accuracy = self._calculate_ocr_accuracy(results)
        
        # Prepare data for template
        template_data = {
            'exam_title': results.get('exam_title', 'Assessment'),
            'student_name': results.get('student_name', 'Student'),
            'subject': results.get('subject', 'Subject'),
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
            # Create template if it doesn't exist
            self._create_default_template()
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Render template
        template = Template(template_content)
        html_content = template.render(**template_data)
        
        # Save HTML file
        report_path = f"output/reports/{results['student_name']}_interactive_report.html"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
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
                'predicted_answer': q['predicted_answer'],
                'expected_answer': q['expected_answer'],
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
        """Create default HTML template if it doesn't exist"""
        # This is the complete HTML template from above
        template_content = """
        <!DOCTYPE html>
        <html lang="en">
        ... [the entire HTML template from above] ...
        </html>
        """
        
        template_path = os.path.join(self.template_dir, "report_template.html")
        with open(template_path, 'w') as f:
            f.write(template_content)
    
    def generate_pdf_report(self, results):
        """Generate professional PDF report"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add first page
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, results['exam_title'], 0, 1, 'C')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'EVALUATION REPORT', 0, 1, 'C')
        pdf.ln(10)
        
        # Student info
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Student: {results['student_name']}", 0, 1)
        pdf.cell(0, 10, f"Subject: {results['subject']}", 0, 1)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.ln(10)
        
        # Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SUMMARY', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        summary_data = [
            f"Total Score: {results['total_marks_obtained']}/{results['total_possible_marks']}",
            f"Percentage: {results['score_percentage']:.1f}%",
            f"Questions Correct: {results['questions_correct']}/{results['total_questions']}",
            f"Average Similarity: {results['average_similarity']:.3f}"
        ]
        
        for line in summary_data:
            pdf.cell(0, 10, line, 0, 1)
        
        pdf.ln(10)
        
        # Detailed results
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'DETAILED BREAKDOWN', 0, 1)
        
        # Table header
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(20, 10, 'Q.No', 1)
        pdf.cell(60, 10, 'Predicted', 1)
        pdf.cell(60, 10, 'Expected', 1)
        pdf.cell(20, 10, 'Marks', 1)
        pdf.cell(30, 10, 'Similarity', 1)
        pdf.ln()
        
        # Table rows
        pdf.set_font('Arial', '', 9)
        for question in results['question_details']:
            pdf.cell(20, 10, f"Q{question['question_number']}", 1)
            pdf.cell(60, 10, question['predicted_answer'][:30], 1)
            pdf.cell(60, 10, question['expected_answer'][:30], 1)
            pdf.cell(20, 10, f"{question['marks_obtained']}/{question['total_marks']}", 1)
            pdf.cell(30, 10, f"{question['combined_similarity']:.3f}", 1)
            pdf.ln()
        
        # Save PDF
        report_path = f"output/reports/{results['student_name']}_report.pdf"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        pdf.output(report_path)
        
        return report_path
    
    def _create_score_gauge(self, results):
        """Create a gauge chart for the score"""
        percentage = results['score_percentage']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = percentage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        fig.update_layout(height=300)
        return fig
    
    def _create_score_distribution(self, results):
        """Create a distribution chart of similarity scores"""
        similarities = [q['combined_similarity'] for q in results['question_details']]
        
        fig = px.histogram(x=similarities, 
                          nbins=10,
                          title="Distribution of Answer Similarities",
                          labels={'x': 'Similarity Score', 'y': 'Number of Questions'})
        
        fig.update_layout(height=300)
        return fig
    
