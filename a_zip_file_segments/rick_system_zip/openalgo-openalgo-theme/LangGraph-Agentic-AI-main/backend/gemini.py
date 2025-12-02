import os
import glob
import google.generativeai as genai
from pathlib import Path
import time

# Configuration
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # Current directory
API_KEY_PATH = os.path.join(PROJECT_DIR, "gemini_api_key.txt")  # Path to your API key
FILE_EXTENSIONS = ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.php']  # File types to analyze
MAX_FILE_SIZE = 100000  # 100KB max file size to analyze
MAX_TOKENS = 30000  # Adjust based on your API limits
MODEL_NAME = "gemini-2.5-flash"  # Using the flash model for speed

# Initialize Gemini API
def initialize_gemini():
    try:
        with open(API_KEY_PATH, 'r') as f:
            api_key = f.read().strip()
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        print(f"Error initializing Gemini API: {e}")
        return None

# Get all code files in project directory
def get_code_files(directory):
    code_files = []
    for ext in FILE_EXTENSIONS:
        code_files.extend(glob.glob(os.path.join(directory, '**', f'*{ext}'), recursive=True))
    
    # Filter out files that are too large
    return [f for f in code_files if os.path.getsize(f) <= MAX_FILE_SIZE]

# Analyze a single file
def analyze_file(model, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return None
            
        print(f"\nAnalyzing: {file_path}")
        
        prompt = f"""
        Analyze the following code file for potential issues, bugs, or improvements.
        Provide specific recommendations for debugging or optimization.
        Focus on:
        - Syntax errors
        - Logical errors
        - Performance bottlenecks
        - Security vulnerabilities
        - Code style improvements
        - Potential edge cases not handled
        
        File: {file_path}
        Code:
        {content}
        """
        
        # Split prompt if too large
        if len(prompt) > MAX_TOKENS:
            chunks = [prompt[i:i+MAX_TOKENS] for i in range(0, len(prompt), MAX_TOKENS)]
        else:
            chunks = [prompt]
        
        responses = []
        for chunk in chunks:
            response = model.generate_content(chunk)
            responses.append(response.text)
            time.sleep(1)  # Rate limiting
        
        return "\n".join(responses)
    
    except UnicodeDecodeError:
        print(f"Skipping binary file: {file_path}")
        return None
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

# Main analysis function
def analyze_project():
    model = initialize_gemini()
    if not model:
        return
    
    print(f"Scanning project directory: {PROJECT_DIR}")
    code_files = get_code_files(PROJECT_DIR)
    
    if not code_files:
        print("No code files found to analyze.")
        return
    
    print(f"Found {len(code_files)} code files to analyze.")
    
    analysis_results = {}
    for file_path in code_files:
        result = analyze_file(model, file_path)
        if result:
            analysis_results[file_path] = result
    
    # Save analysis results to a file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    report_file = os.path.join(PROJECT_DIR, f"code_analysis_report_{timestamp}.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Code Analysis Report - {timestamp}\n")
        f.write(f"Project Directory: {PROJECT_DIR}\n")
        f.write(f"Total Files Analyzed: {len(analysis_results)}\n\n")
        
        for file_path, analysis in analysis_results.items():
            f.write(f"=== {file_path} ===\n")
            f.write(analysis)
            f.write("\n\n")
    
    print(f"\nAnalysis complete. Report saved to: {report_file}")

if __name__ == "__main__":
    analyze_project()
