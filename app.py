from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import google.generativeai as genai
import os
import json
from pathlib import Path
import secrets
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
import uuid

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key for sessions

# Get API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/genai")
client = MongoClient(MONGO_URI)
db = client["genai"]
users_collection = db["user"]
chats_collection = db["chats"]
messages_collection = db["messages"]

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

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users_collection.find_one({"email": email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email already exists
        if users_collection.find_one({"email": email}):
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now()
        }
        
        users_collection.insert_one(new_user)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    return render_template('profile.html', user=user)

# Main routes
@app.route('/')
def index():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if API key is valid
    model = initialize_gemini()
    api_key_valid = model is not None
    
    # Get user's chats
    user_id = session['user_id']
    user_chats = list(chats_collection.find({"user_id": user_id}).sort("updated_at", -1))
    
    return render_template('index.html', api_key_valid=api_key_valid, user_chats=user_chats)

@app.route('/check-api', methods=['GET'])
def check_api():
    model = initialize_gemini()
    return jsonify({"valid": model is not None})

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({"error": "Please login to continue"}), 401
    
    data = request.json
    user_id = session['user_id']
    
    # Get model with API key from environment
    model = initialize_gemini()
    if not model:
        return jsonify({"error": "Gemini API key is invalid or not set. Please check your environment variables."}), 500
    
    mode = data.get('mode', 'past')  # 'past' or 'future'
    message = data.get('message', '')
    context = data.get('context', '')
    chat_id = data.get('chat_id', None)
    
    # Create a new chat if chat_id is not provided
    if not chat_id:
        chat_title = f"{mode.capitalize()} Self: {message[:30]}..." if len(message) > 30 else f"{mode.capitalize()} Self: {message}"
        new_chat = {
            "user_id": user_id,
            "title": chat_title,
            "mode": mode,
            "context": context,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = chats_collection.insert_one(new_chat)
        chat_id = str(result.inserted_id)
    else:
        # Update existing chat
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"updated_at": datetime.now()}}
        )
    
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
        response_text = response.text
        
        # Save message to database
        new_message = {
            "chat_id": chat_id,
            "user_id": user_id,
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        }
        messages_collection.insert_one(new_message)
        
        # Save response to database
        new_response = {
            "chat_id": chat_id,
            "user_id": user_id,
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now()
        }
        messages_collection.insert_one(new_response)
        
        return jsonify({
            "response": response_text,
            "chat_id": chat_id
        })
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500

@app.route('/debate', methods=['POST'])
def debate():
    if 'user_id' not in session:
        return jsonify({"error": "Please login to continue"}), 401
    
    data = request.json
    user_id = session['user_id']
    
    # Get model with API key from environment
    model = initialize_gemini()
    if not model:
        return jsonify({"error": "Gemini API key is invalid or not set. Please check your environment variables."}), 500
    
    past_context = data.get('pastContext', '')
    future_context = data.get('futureContext', '')
    topic = data.get('topic', '')
    chat_id = data.get('chat_id', None)
    
    # Create a new chat if chat_id is not provided
    if not chat_id:
        chat_title = f"Debate: {topic[:30]}..." if len(topic) > 30 else f"Debate: {topic}"
        new_chat = {
            "user_id": user_id,
            "title": chat_title,
            "mode": "debate",
            "past_context": past_context,
            "future_context": future_context,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = chats_collection.insert_one(new_chat)
        chat_id = str(result.inserted_id)
    else:
        # Update existing chat
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"updated_at": datetime.now()}}
        )
    
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
        response_text = response.text
        
        # Save message to database
        new_message = {
            "chat_id": chat_id,
            "user_id": user_id,
            "role": "user",
            "content": f"Debate topic: {topic}",
            "timestamp": datetime.now()
        }
        messages_collection.insert_one(new_message)
        
        # Save response to database
        new_response = {
            "chat_id": chat_id,
            "user_id": user_id,
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now()
        }
        messages_collection.insert_one(new_response)
        
        return jsonify({
            "response": response_text,
            "chat_id": chat_id
        })
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500

@app.route('/get-chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    if 'user_id' not in session:
        return jsonify({"error": "Please login to continue"}), 401
    
    user_id = session['user_id']
    
    # Get chat details
    chat = chats_collection.find_one({"_id": ObjectId(chat_id), "user_id": user_id})
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    
    # Get messages for this chat
    messages = list(messages_collection.find({"chat_id": chat_id}).sort("timestamp", 1))
    
    # Convert ObjectId to string for JSON serialization
    for message in messages:
        message['_id'] = str(message['_id'])
    
    chat['_id'] = str(chat['_id'])
    
    return jsonify({
        "chat": chat,
        "messages": messages
    })

@app.route('/delete-chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    if 'user_id' not in session:
        return jsonify({"error": "Please login to continue"}), 401
    
    user_id = session['user_id']
    
    # Delete chat and its messages
    chats_collection.delete_one({"_id": ObjectId(chat_id), "user_id": user_id})
    messages_collection.delete_many({"chat_id": chat_id})
    
    return jsonify({"success": True})

@app.route('/upload-journal', methods=['POST'])
def upload_journal():
    if 'user_id' not in session:
        return jsonify({"error": "Please login to continue"}), 401
    
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
