# Time Capsule Chatbot

A Flask-based application that lets you chat with past or future versions of yourself using Google's Gemini AI.

## Features

- **Past Self Mode**: Chat with a version of yourself from the past based on journal entries, social media posts, etc.
- **Future Self Mode**: Interact with a simulated future version of yourself based on your goals and aspirations.
- **Time-Travel Debate**: Generate a debate between your past and future selves on a specific topic.

## Setup

1. Clone this repository
2. Install the required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
3. Set your Gemini API key as an environment variable:
   \`\`\`
   export GEMINI_API_KEY="your_api_key_here"
   \`\`\`
4. Run the application:
   \`\`\`
   python app.py
   \`\`\`
5. Open your browser and navigate to `http://127.0.0.1:5000/`

## Usage

### Past Self Mode
1. Enter past context (journal entries, social media posts, etc.)
2. Type a message to your past self
3. Receive a response as if it were from your past self

### Future Self Mode
1. Enter your future goals and aspirations
2. Ask your future self a question
3. Get advice and perspective from your simulated future self

### Time-Travel Debate
1. Enter context for both your past and future selves
2. Specify a debate topic
3. Generate a back-and-forth debate between your past and future selves

## Technologies Used
- Flask (Python web framework)
- Google Generative AI (Gemini API)
- HTML/CSS/JavaScript (Frontend)
