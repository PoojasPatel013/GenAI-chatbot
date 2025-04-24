from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
import json
from pathlib import Path
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key for sessions

# Get API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Gemini model
def initialize_gemini():
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Test the model with a simple prompt
            response = model.generate_content("Hello")
            return model
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            return None
    else:
        print("No Gemini API key found in environment variables")
        return None

@app.route('/')
def index():
    # Check if API key is valid
    model = initialize_gemini()
    api_key_valid = model is not None
    return render_template('index.html', api_key_valid=api_key_valid)

@app.route('/check-api', methods=['GET'])
def check_api():
    model = initialize_gemini()
    return jsonify({"valid": model is not None})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Get model with API key from environment
    model = initialize_gemini()
    if not model:
        return jsonify({"error": "Gemini API key is invalid or not set. Please check your environment variables."}), 500
    
    mode = data.get('mode', 'past')  # 'past' or 'future'
    message = data.get('message', '')
    context = data.get('context', '')
    
    if mode == 'past':
        prompt = f"""
        Based on the following past context about me:
        {context}
        
        Roleplay as my past self from that time period. Respond to: '{message}'
        Maintain the tone, values, and perspective I had during that time.
        """
    else:  # future mode
        prompt = f"""
        Based on my current goals and aspirations:
        {context}
        
        Roleplay as my future self who has achieved these goals. Respond to: '{message}'
        Provide perspective and advice from this future version of me.
        """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500

@app.route('/debate', methods=['POST'])
def debate():
    data = request.json
    
    # Get model with API key from environment
    model = initialize_gemini()
    if not model:
        return jsonify({"error": "Gemini API key is invalid or not set. Please check your environment variables."}), 500
    
    past_context = data.get('pastContext', '')
    future_context = data.get('futureContext', '')
    topic = data.get('topic', '')
    
    prompt = f"""
    Create a debate between my past and future selves on the topic: '{topic}'
    
    Past self context:
    {past_context}
    
    Future self context:
    {future_context}
    
    Format the debate as a back-and-forth conversation with 3 exchanges from each side.
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500

@app.route('/upload-journal', methods=['POST'])
def upload_journal():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith(('.txt', '.md', '.pdf')):
        try:
            # Read file content
            content = file.read().decode('utf-8')
            return jsonify({"content": content})
        except Exception as e:
            return jsonify({"error": f"Error reading file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Please upload .txt, .md, or .pdf files."}), 400

if __name__ == '__main__':
    app.run(debug=True)
