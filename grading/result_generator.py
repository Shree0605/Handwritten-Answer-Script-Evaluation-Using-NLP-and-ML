import os
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from config import REPORTS_DIR

class ResultGenerator:
    def __init__(self):
        self.report_count = 0
    
    def generate_report(self, results):
        """Generate visual report with all results"""
        # Create figure
        plt.figure(figsize=(12, 16))
        plt.suptitle(f"{results['exam_title']} - EVALUATION REPORT", 
                    fontsize=16, fontweight='bold', y=0.98)
        
        # Student info
        plt.figtext(0.1, 0.95, f"Student: {results['student_name']}", fontsize=12)
        plt.figtext(0.1, 0.92, f"Subject: {results['subject']}", fontsize=12)
        plt.figtext(0.1, 0.89, f"Final Score: {results['total_marks_obtained']}/{results['total_possible_marks']} ({results['score_percentage']:.1f}%)", 
                   fontsize=12, fontweight='bold', color='blue')
        
        # Add annotated image
        if os.path.exists(results['annotated_image']):
            ax1 = plt.subplot(3, 1, 1)
            img = cv2.imread(results['annotated_image'])
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.imshow(img_rgb)
            plt.title("Detected Answer Boxes", fontsize=12)
            plt.axis('off')
        
        # Question-wise results
        ax2 = plt.subplot(3, 1, 2)
        questions = list(range(1, len(results['question_details']) + 1))
        marks_obtained = [q['marks_obtained'] for q in results['question_details']]
        similarities = [q['combined_similarity'] for q in results['question_details']]
        
        # Create table data
        table_data = []
        for i, q in enumerate(results['question_details']):
            table_data.append([
                f"Q{i+1}",
                q['predicted_answer'][:30] + "..." if len(q['predicted_answer']) > 30 else q['predicted_answer'],
                q['expected_answer'],
                f"{q['combined_similarity']:.3f}",
                f"{q['correctness_probability']:.3f}",
                f"{q['marks_obtained']}/{q['total_marks']}"
            ])
        
        # Create table
        table = plt.table(cellText=table_data,
                         colLabels=['Q.No', 'Predicted', 'Expected', 'Similarity', 'ML Conf', 'Marks'],
                         loc='center',
                         cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        plt.axis('off')
        plt.title("Question-wise Evaluation", fontsize=12)
        
        # Score summary
        ax3 = plt.subplot(3, 1, 3)
        labels = ['Correct', 'Incorrect']
        sizes = [results['questions_correct'], 
                results['total_questions'] - results['questions_correct']]
        colors = ['#4CAF50', '#F44336']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title("Performance Summary", fontsize=12)
        
        # Adjust layout and save
        plt.tight_layout(rect=[0, 0, 1, 0.93])
        
        # Save report
        self.report_count += 1
        report_path = os.path.join(REPORTS_DIR, f"evaluation_report_{self.report_count}.png")
        plt.savefig(report_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Also save text report
        text_report_path = os.path.join(REPORTS_DIR, f"evaluation_report_{self.report_count}.txt")
        self._save_text_report(results, text_report_path)
        
        return report_path
    
    def _save_text_report(self, results, filepath):
        """Save detailed text report"""
        with open(filepath, 'w') as f:
            f.write(f"{'='*60}\n")
            f.write(f"           {results['exam_title']} - EVALUATION REPORT\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Student: {results['student_name']}\n")
            f.write(f"Subject: {results['subject']}\n")
            f.write(f"Total Questions: {results['total_questions']}\n")
            f.write(f"Questions Correct: {results['questions_correct']}\n")
            f.write(f"Final Score: {results['total_marks_obtained']}/{results['total_possible_marks']}\n")
            f.write(f"Percentage: {results['score_percentage']:.1f}%\n")
            f.write(f"Average Similarity: {results['average_similarity']:.3f}\n\n")
            
            f.write(f"{'-'*80}\n")
            f.write(f"QUESTION-WISE DETAILS\n")
            f.write(f"{'-'*80}\n")
            
            for i, q in enumerate(results['question_details']):
                f.write(f"\nQ{i+1}:\n")
                f.write(f"  Predicted: {q['predicted_answer']}\n")
                f.write(f"  Expected:  {q['expected_answer']}\n")
                f.write(f"  Similarity: {q['combined_similarity']:.3f}\n")
                f.write(f"  ML Confidence: {q['correctness_probability']:.3f}\n")
                f.write(f"  Marks: {q['marks_obtained']}/{q['total_marks']}\n")
                f.write(f"  Status: {q['ml_prediction']}\n")

