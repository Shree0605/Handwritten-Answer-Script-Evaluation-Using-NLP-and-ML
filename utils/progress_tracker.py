import streamlit as st
import time

class ProgressTracker:
    def __init__(self):
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
    
    def update(self, message, progress):
        """Update progress bar and status"""
        self.status_text.text(f"🔄 {message}")
        self.progress_bar.progress(progress)
        time.sleep(0.5)  # Small delay for visual effect
    
    def complete(self):
        """Mark progress as complete"""
        self.status_text.text("✅ Processing complete!")
        self.progress_bar.progress(100)
